"""
hotkey_manager.py - Gestion des raccourcis clavier globaux.

Utilise pynput pour intercepter les touches même quand l'application
n'est pas au premier plan.

Raccourcis disponibles :
    Ctrl+Alt+Flèches         : Déplace le crosshair de 1 pixel
    Ctrl+Alt+Shift+Flèches   : Déplace le crosshair de 10 pixels
    Ctrl+Alt+C               : Centre le crosshair
    Ctrl+Alt+S               : Affiche/cache le panneau de configuration
    Ctrl+Alt+H               : Affiche/cache le crosshair
    Ctrl+Alt+Q               : Quitte l'application
"""

import threading
from typing import Callable, Optional

from pynput import keyboard


class HotkeyManager:
    """
    Gère les raccourcis clavier globaux via pynput.

    Les callbacks sont appelés depuis le thread pynput ;
    utilisez Qt.QueuedConnection ou invokeMethod si vous mettez
    à jour l'interface graphique depuis ces callbacks.
    """

    def __init__(
        self,
        on_move: Callable[[int, int], None],
        on_center: Callable[[], None],
        on_toggle_settings: Callable[[], None],
        on_toggle_crosshair: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        """
        Initialise le gestionnaire de raccourcis.

        Paramètres :
            on_move              : Callback(dx, dy) pour le déplacement
            on_center            : Callback() pour centrer
            on_toggle_settings   : Callback() pour afficher/cacher les paramètres
            on_toggle_crosshair  : Callback() pour afficher/cacher le crosshair
            on_quit              : Callback() pour quitter l'application
        """
        self.on_move = on_move
        self.on_center = on_center
        self.on_toggle_settings = on_toggle_settings
        self.on_toggle_crosshair = on_toggle_crosshair
        self.on_quit = on_quit

        # Ensemble des touches actuellement pressées
        self._pressed: set = set()
        self._listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Démarrage / arrêt
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Démarre l'écoute des touches en arrière-plan."""
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        """Arrête l'écoute des touches."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    # ------------------------------------------------------------------
    # Gestion des touches
    # ------------------------------------------------------------------

    def _normalize(self, key) -> Optional[str]:
        """
        Convertit une touche pynput en identifiant normalisé (chaîne).

        Retourne None si la touche n'est pas gérée.
        """
        try:
            # Touches spéciales (Enum pynput)
            return key.name  # ex: "ctrl_l", "alt_l", "shift", "up", etc.
        except AttributeError:
            # Caractère alphanumérique
            try:
                return key.char.lower() if key.char else None
            except AttributeError:
                return None

    def _is_ctrl(self) -> bool:
        return "ctrl_l" in self._pressed or "ctrl_r" in self._pressed

    def _is_alt(self) -> bool:
        return "alt_l" in self._pressed or "alt_r" in self._pressed or "alt_gr" in self._pressed

    def _is_shift(self) -> bool:
        return "shift" in self._pressed or "shift_l" in self._pressed or "shift_r" in self._pressed

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

        shift = self._is_shift()
        step = 10 if shift else 1

        # Déplacements
        if last_key == "up":
            self.on_move(0, -step)
        elif last_key == "down":
            self.on_move(0, step)
        elif last_key == "left":
            self.on_move(-step, 0)
        elif last_key == "right":
            self.on_move(step, 0)

        # Actions
        elif last_key == "c":
            self.on_center()
        elif last_key == "s":
            self.on_toggle_settings()
        elif last_key == "h":
            self.on_toggle_crosshair()
        elif last_key == "q":
            self.on_quit()
