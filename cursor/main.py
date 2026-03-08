"""
main.py - Point d'entrée de l'application Cursor.

Lance l'overlay, le panneau de paramètres et le gestionnaire de raccourcis.
Intègre une icône dans le system tray.
"""

import os
import sys

from PyQt5.QtCore import QEvent, QMetaObject, QObject, Qt, Q_ARG
from PyQt5.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon

from config import DEFAULT_CONFIG, load_config, save_config
from crosshair_overlay import CrosshairOverlay
from hotkey_manager import HotkeyManager
from settings_panel import SettingsPanel

def _generate_icon(size: int = 32) -> QIcon:
    """
    Génère une icône simple (viseur rouge) si aucun fichier .ico n'est disponible.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    center = size // 2
    radius = size // 2 - 2
    thickness = max(1, size // 16)

    pen_outer = painter.pen()
    pen_outer.setColor(QColor("#FF0000"))
    pen_outer.setWidth(thickness)
    painter.setPen(pen_outer)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)

    gap = size // 8
    arm = radius - gap
    painter.drawLine(center, center - gap, center, center - arm)
    painter.drawLine(center, center + gap, center, center + arm)
    painter.drawLine(center - gap, center, center - arm, center)
    painter.drawLine(center + gap, center, center + arm, center)

    painter.end()
    return QIcon(pixmap)

def _load_icon() -> QIcon:
    """Charge l'icône depuis le dossier assets ou génère une icône de secours."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(base, "assets", "icon.ico")
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    return _generate_icon()

# ---------------------------------------------------------------------------
# Événement générique pour appeler une fonction depuis le thread principal Qt
# ---------------------------------------------------------------------------

_FUNCTION_CALL_EVENT_TYPE = QEvent.registerEventType()


class _FunctionCallEvent(QEvent):
    """Événement permettant d'appeler une fonction dans le thread Qt principal."""

    def __init__(self, func):
        super().__init__(QEvent.Type(_FUNCTION_CALL_EVENT_TYPE))
        self.func = func


class _EventFilter(QObject):
    """Filtre d'événements qui exécute les _FunctionCallEvent. Hérite de QObject."""

    def eventFilter(self, obj, event):
        if event.type() == _FUNCTION_CALL_EVENT_TYPE:
            event.func()
            return True
        return super().eventFilter(obj, event)


class CursorApp:
    """
    Contrôleur principal de l'application.

    Coordonne l'overlay, le panneau de paramètres, le system tray
    et le gestionnaire de raccourcis.
    """

    def __init__(self, app: QApplication):
        self.app = app
        self.config = load_config()

        # Composants principaux
        self.overlay = CrosshairOverlay(self.config)
        self.settings = SettingsPanel(self.config)
        self.hotkeys = HotkeyManager(
            on_move=self._hotkey_move,
            on_center=self._hotkey_center,
            on_toggle_settings=self._hotkey_toggle_settings,
            on_toggle_crosshair=self._hotkey_toggle_crosshair,
            on_quit=self._hotkey_quit,
            on_set_position=self._hotkey_set_position,
            on_toggle_mouse_mode=self._hotkey_toggle_mouse_mode,
        )

        self.icon = _load_icon()
        self.tray = self._build_tray()

        self._connect_signals()
        self._start()

    # ------------------------------------------------------------------
    # Démarrage
    # ------------------------------------------------------------------

    def _start(self) -> None:
        self.overlay.show()
        self.tray.show()
        self.hotkeys.start()

    # ------------------------------------------------------------------
    # Construction du system tray
    # ------------------------------------------------------------------

    def _build_tray(self) -> QSystemTrayIcon:
        tray = QSystemTrayIcon(self.icon, parent=None)
        tray.setToolTip("Cursor — Crosshair Overlay")

        menu = QMenu()
        menu.setStyleSheet(
            "QMenu { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #444; }"
            "QMenu::item:selected { background-color: #0078d4; }"
        )

        action_settings = QAction("⚙  Paramètres", menu)
        action_settings.triggered.connect(self._show_settings)

        action_center = QAction("⊕  Centrer", menu)
        action_center.triggered.connect(self._center_crosshair)

        action_toggle = QAction("👁  Afficher / Masquer", menu)
        action_toggle.triggered.connect(self._toggle_crosshair)

        action_quit = QAction("✕  Quitter", menu)
        action_quit.triggered.connect(self._quit)

        menu.addAction(action_settings)
        menu.addAction(action_center)
        menu.addAction(action_toggle)
        menu.addSeparator()
        menu.addAction(action_quit)

        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)

        return tray

    # ------------------------------------------------------------------
    # Connexion des signaux
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self.settings.config_changed.connect(self._on_config_changed)
        self.settings.center_requested.connect(self._center_crosshair)

    # ------------------------------------------------------------------
    # Callbacks internes
    # ------------------------------------------------------------------

    def _on_config_changed(self, config: dict) -> None:
        """Appelé quand les paramètres changent dans le panneau."""
        self.config.update(config)
        self.overlay.update_config(self.config)
        opacity = self.config.get("opacity", 100) / 100.0
        self.overlay.setWindowOpacity(opacity)
        save_config(self.config)

    def _show_settings(self) -> None:
        """Affiche le panneau de paramètres."""
        self.settings.show()
        self.settings.raise_()
        self.settings.activateWindow()

    def _hide_settings(self) -> None:
        """Cache le panneau de paramètres."""
        self.settings.hide()

    def _toggle_settings(self) -> None:
        """Bascule la visibilité du panneau de paramètres."""
        if self.settings.isVisible():
            self._hide_settings()
        else:
            self._show_settings()

    def _center_crosshair(self) -> None:
        """Centre le crosshair sur l'écran."""
        self.config["position_x"] = None
        self.config["position_y"] = None
        self.overlay.center_crosshair()
        self.settings.refresh_config(self.config)
        save_config(self.config)

    def _toggle_crosshair(self) -> None:
        """Bascule la visibilité du crosshair."""
        self.overlay.toggle_visibility()

    def _on_tray_activated(self, reason: int) -> None:
        """Double-clic sur l'icône = ouvrir les paramètres."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_settings()

    def _quit(self) -> None:
        """Quitte proprement l'application."""
        save_config(self.config)
        self.hotkeys.stop()
        self.tray.hide()
        self.overlay.close()
        self.settings.close()
        QApplication.quit()

    # ------------------------------------------------------------------
    # Callbacks hotkeys (appelés depuis le thread pynput)
    # ------------------------------------------------------------------

    def _hotkey_move(self, dx: int, dy: int) -> None:
        QMetaObject.invokeMethod(
            self.overlay,
            "move_crosshair",
            Qt.QueuedConnection,
            Q_ARG(int, dx),
            Q_ARG(int, dy),
        )

    def _hotkey_center(self) -> None:
        QMetaObject.invokeMethod(
            self.overlay,
            "center_crosshair",
            Qt.QueuedConnection,
        )

    def _hotkey_set_position(self, x: int, y: int) -> None:
        """Positionne le crosshair à une position absolue (mode souris)."""
        def _do():
            self.config["position_x"] = x
            self.config["position_y"] = y
            self.overlay.update_config(self.config)
        self.app.postEvent(self.overlay, _FunctionCallEvent(_do))

    def _hotkey_toggle_mouse_mode(self, active: bool) -> None:
        """Appelé quand le mode souris est activé/désactivé."""
        def _do():
            if active:
                self.tray.showMessage(
                    "Cursor",
                    "🖱 Mode souris ACTIVÉ — Bougez la souris pour déplacer le crosshair.
Ctrl+Alt+M pour désactiver.",
                    QSystemTrayIcon.Information,
                    2000,
                )
            else:
                # Sauvegarder la position actuelle
                save_config(self.config)
                self.tray.showMessage(
                    "Cursor",
                    "🔒 Mode souris DÉSACTIVÉ — Crosshair verrouillé.",
                    QSystemTrayIcon.Information,
                    2000,
                )
        self.app.postEvent(self.overlay, _FunctionCallEvent(_do))

    def _hotkey_toggle_settings(self) -> None:
        self.app.postEvent(self.overlay, _FunctionCallEvent(self._toggle_settings))

    def _hotkey_toggle_crosshair(self) -> None:
        self.app.postEvent(self.overlay, _FunctionCallEvent(self._toggle_crosshair))

    def _hotkey_quit(self) -> None:
        self.app.postEvent(self.overlay, _FunctionCallEvent(self._quit))


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> None:
    """Lance l'application Cursor."""
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("[Cursor] Avertissement : system tray non disponible.")

    cursor_app = CursorApp(app)

    # Filtre d'événements pour les appels thread-safe
    event_filter = _EventFilter(parent=app)
    app.installEventFilter(event_filter)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()