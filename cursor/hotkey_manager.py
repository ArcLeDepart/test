"""
hotkey_manager.py - Gestion des raccourcis clavier globaux.

Utilise pynput pour intercepter les touches et la souris même quand
l'application n'est pas au premier plan.

Raccourcis disponibles :
    Ctrl+Alt+M               : Toggle mode déplacement souris (le crosshair suit la souris)
    Ctrl+Alt+C               : Centre le crosshair
    Ctrl+Alt+S               : Affiche/cache le panneau de configuration
    Ctrl+Alt+H               : Affiche/cache le crosshair
    Ctrl+Alt+L               : Verrouille/déverrouille l'overlay (click-through total)
    Ctrl+Alt+↑               : Augmenter la taille du crosshair
    Ctrl+Alt+↓               : Diminuer la taille du crosshair
    Ctrl+Alt+Q               : Quitte l'application
"""

import threading
from typing import Callable, Optional

from pynput import keyboard, mouse


class HotkeyManager:
    """
    Gère les raccourcis clavier globaux et le mode déplacement souris.

    Mode déplacement souris :
        - Ctrl+Alt+M pour activer : le crosshair suit les mouvements de la souris
        - Ctrl+Alt+M pour désactiver : le crosshair reste à sa position actuelle
    """

    def __init__(self,
        on_move: Callable[[int, int], None],
        on_center: Callable[[], None],
        on_toggle_settings: Callable[[], None],
        on_toggle_crosshair: Callable[[], None],
        on_quit: Callable[[], None],
        on_set_position: Optional[Callable[[int, int], None]] = None,
        on_toggle_mouse_mode: Optional[Callable[[bool], None]] = None,
        on_toggle_lock: Optional[Callable[[], None]] = None,
        on_change_size: Optional[Callable[[int], None]] = None,
    ):
        """
        Initialise le gestionnaire de raccourcis.

        Paramètres :
            on_move              : Callback(dx, dy) pour le déplacement relatif
            on_center            : Callback() pour centrer
            on_toggle_settings   : Callback() pour afficher/cacher les paramètres
            on_toggle_crosshair  : Callback() pour afficher/cacher le crosshair
            on_quit              : Callback() pour quitter l'application
            on_set_position      : Callback(x, y) pour positionner le crosshair (absolu)
            on_toggle_mouse_mode : Callback(active) appelé quand le mode souris change
            on_toggle_lock       : Callback() pour verrouiller/déverrouiller l'overlay
            on_change_size       : Callback(delta) pour changer la taille du crosshair
        """
        self.on_move = on_move
        self.on_center = on_center
        self.on_toggle_settings = on_toggle_settings
        self.on_toggle_crosshair = on_toggle_crosshair
        self.on_quit = on_quit
        self.on_set_position = on_set_position
        self.on_toggle_mouse_mode = on_toggle_mouse_mode
        self.on_toggle_lock = on_toggle_lock
        self.on_change_size = on_change_size

        # État du mode déplacement souris
        self._mouse_mode = False

        # Ensemble des touches actuellement pressées
        self._pressed: set = set()
        self._kb_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Propriété mode souris
    # ------------------------------------------------------------------

    @property
    def mouse_mode(self) -> bool:
        """Retourne True si le mode déplacement souris est actif."""
        return self._mouse_mode

    # ------------------------------------------------------------------
    # Démarrage / arrêt
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Démarre l'écoute des touches et de la souris en arrière-plan."""
        self._kb_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._kb_listener.daemon = True
        self._kb_listener.start()

        # Listener souris pour le mode déplacement
        self._mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
        )
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

    def stop(self) -> None:
        """Arrête l'écoute des touches et de la souris."""
        if self._kb_listener is not None:
            self._kb_listener.stop()
            self._kb_listener = None
        if self._mouse_listener is not None:
            self._mouse_listener.stop()
            self._mouse_listener = None

    # ------------------------------------------------------------------
    # Gestion de la souris
    # ------------------------------------------------------------------

    def _on_mouse_move(self, x: int, y: int) -> None:
        """Appelé à chaque mouvement de souris. Positionne le crosshair si le mode est actif."""
        if self._mouse_mode and self.on_set_position:
            self.on_set_position(x, y)

    def _toggle_mouse_mode(self) -> None:
        """Bascule le mode déplacement souris on/off."""
        self._mouse_mode = not self._mouse_mode
        if self.on_toggle_mouse_mode:
            self.on_toggle_mouse_mode(self._mouse_mode)

    # ------------------------------------------------------------------
    # Gestion des touches
    # ------------------------------------------------------------------

    def _normalize(self, key) -> Optional[str]:
        """
        Convertit une touche pynput en identifiant normalisé (chaîne).

        Retourne None si la touche n'est pas gérée.
        """
        try:
            return key.name
        except AttributeError:
            try:
                # key.char is None when Ctrl+Alt are held on Windows
                if key.char:
                    return key.char.lower()
                # Fallback: use virtual key code to get the letter
                if hasattr(key, 'vk') and key.vk is not None:
                    # vk codes 65-90 map to 'a'-'z'
                    if 65 <= key.vk <= 90:
                        return chr(key.vk).lower()
                return None
            except AttributeError:
                return None

    def _is_ctrl(self) -> bool:
        return "ctrl_l" in self._pressed or "ctrl_r" in self._pressed

    def _is_alt(self) -> bool:
        return "alt_l" in self._pressed or "alt_r" in self._pressed or "alt_gr" in self._pressed

    def _on_press(self, key) -> None:
        """Appelé à chaque appui de touche."""
        name = self._normalize(key)
        if name is None:
            return

        with self._lock:
            self._pressed.add(name)
            self._handle_hotkey(name)

    def _on_release(self, key) -> None:
        """Appelé à chaque relâchement de touche."""
        name = self._normalize(key)
        if name is None:
            return

        with self._lock:
            self._pressed.discard(name)

    def _handle_hotkey(self, last_key: str) -> None:
        """
        Vérifie si la combinaison courante correspond à un raccourci
        et appelle le callback approprié.
        """
        if not (self._is_ctrl() and self._is_alt()):
            return

        # Toggle mode déplacement souris
        if last_key == "m":
            self._toggle_mouse_mode()

        # Centrer le crosshair (désactive aussi le mode souris)
        elif last_key == "c":
            if self._mouse_mode:
                self._mouse_mode = False
                if self.on_toggle_mouse_mode:
                    self.on_toggle_mouse_mode(False)
            self.on_center()

        # Afficher/cacher les paramètres
        elif last_key == "s":
            self.on_toggle_settings()

        # Afficher/cacher le crosshair
        elif last_key == "h":
            self.on_toggle_crosshair()

        # Verrouiller/déverrouiller l'overlay
        elif last_key == "l":
            if self.on_toggle_lock:
                self.on_toggle_lock()

        # Augmenter la taille du crosshair
        elif last_key == "up":
            if self.on_change_size:
                self.on_change_size(2)

        # Diminuer la taille du crosshair
        elif last_key == "down":
            if self.on_change_size:
                self.on_change_size(-2)

        # Quitter
        elif last_key == "q":
            self.on_quit()