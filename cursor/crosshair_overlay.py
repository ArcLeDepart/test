"""
crosshair_overlay.py - Fenêtre overlay transparente pour le crosshair.

La fenêtre est :
- Transparente (fond transparent)
- Sans bordure
- Toujours au premier plan (always on top)
- Click-through (les clics passent à travers)
- Couvre tout l'écran principal
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget


class CrosshairOverlay(QWidget):
    """
    Fenêtre overlay transparente qui dessine le crosshair au centre (ou à
    une position personnalisée) de l'écran.
    """

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self._visible = True  # Visibilité du crosshair (toggle)

        self._init_window()
        self._apply_config(config)

    # ------------------------------------------------------------------
    # Initialisation de la fenêtre
    # ------------------------------------------------------------------

    def _init_window(self) -> None:
        """Configure les attributs de la fenêtre overlay."""
        # Flags : sans bordure, toujours au premier plan, outil (pas dans la barre des tâches)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )

        # Fond translucide + click-through
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # Couvrir tout l'écran principal
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            self.setGeometry(geometry)

    # ------------------------------------------------------------------
    # Application de la configuration
    # ------------------------------------------------------------------

    def _apply_config(self, config: dict) -> None:
        """Met à jour la configuration et redessine le crosshair."""
        self.config = config
        self.update()

    def update_config(self, config: dict) -> None:
        """Méthode publique pour mettre à jour la configuration en temps réel."""
        self._apply_config(config)

    # ------------------------------------------------------------------
    # Calcul de la position
    # ------------------------------------------------------------------

    def _get_center(self) -> tuple:
        """
        Retourne les coordonnées (x, y) du centre du crosshair.

        Si position_x / position_y sont None, utilise le centre de l'écran.
        """
        px = self.config.get("position_x")
        py = self.config.get("position_y")

        if px is None or py is None:
            cx = self.width() // 2
            cy = self.height() // 2
        else:
            cx = int(px)
            cy = int(py)

        return cx, cy

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        """Dessine le crosshair selon la configuration courante."""
        if not self._visible:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        shape = self.config.get("shape", "cross")
        cx, cy = self._get_center()

        if shape == "cross":
            self._draw_cross(painter, cx, cy)
        elif shape == "circle":
            self._draw_circle(painter, cx, cy)
        elif shape == "dot":
            self._draw_dot(painter, cx, cy)
        elif shape == "cross_circle":
            self._draw_cross(painter, cx, cy)
            self._draw_circle(painter, cx, cy)

        painter.end()

    def _make_pen(self, color_hex: str, thickness: int) -> QPen:
        """Crée un QPen avec la couleur et l'épaisseur données."""
        pen = QPen(QColor(color_hex))
        pen.setWidth(thickness)
        pen.setCapStyle(Qt.RoundCap)
        return pen

    def _draw_cross(self, painter: QPainter, cx: int, cy: int) -> None:
        """Dessine une croix avec gap central optionnel."""
        size = self.config.get("size", 20)
        thickness = self.config.get("thickness", 2)
        color = self.config.get("color", "#FF0000")
        gap = self.config.get("gap", 4)
        outline = self.config.get("outline", True)
        outline_color = self.config.get("outline_color", "#000000")

        if outline:
            outline_pen = self._make_pen(outline_color, thickness + 2)
            painter.setPen(outline_pen)
            self._draw_cross_lines(painter, cx, cy, size, gap)

        main_pen = self._make_pen(color, thickness)
        painter.setPen(main_pen)
        self._draw_cross_lines(painter, cx, cy, size, gap)

    def _draw_cross_lines(
        self,
        painter: QPainter,
        cx: int,
        cy: int,
        size: int,
        gap: int,
    ) -> None:
        """Dessine les quatre branches de la croix."""
        # Branche haut
        painter.drawLine(cx, cy - gap, cx, cy - gap - size)
        # Branche bas
        painter.drawLine(cx, cy + gap, cx, cy + gap + size)
        # Branche gauche
        painter.drawLine(cx - gap, cy, cx - gap - size, cy)
        # Branche droite
        painter.drawLine(cx + gap, cy, cx + gap + size, cy)

    def _draw_circle(self, painter: QPainter, cx: int, cy: int) -> None:
        """Dessine un cercle."""
        size = self.config.get("size", 20)
        thickness = self.config.get("thickness", 2)
        color = self.config.get("color", "#FF0000")
        outline = self.config.get("outline", True)
        outline_color = self.config.get("outline_color", "#000000")
        radius = size // 2

        if outline:
            outline_pen = self._make_pen(outline_color, thickness + 2)
            painter.setPen(outline_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(cx - radius, cy - radius, size, size)

        main_pen = self._make_pen(color, thickness)
        painter.setPen(main_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - radius, cy - radius, size, size)

    def _draw_dot(self, painter: QPainter, cx: int, cy: int) -> None:
        """Dessine un point central."""
        size = self.config.get("size", 20)
        color = self.config.get("color", "#FF0000")
        outline = self.config.get("outline", True)
        outline_color = self.config.get("outline_color", "#000000")
        radius = size // 2

        if outline:
            outline_pen = self._make_pen(outline_color, 1)
            painter.setPen(outline_pen)
            painter.setBrush(QColor(outline_color))
            painter.drawEllipse(
                cx - radius - 1, cy - radius - 1, size + 2, size + 2
            )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        painter.drawEllipse(cx - radius, cy - radius, size, size)

    # ------------------------------------------------------------------
    # Contrôle de la visibilité
    # ------------------------------------------------------------------

    def toggle_visibility(self) -> bool:
        """
        Bascule la visibilité du crosshair.

        Retourne le nouvel état (True = visible).
        """
        self._visible = not self._visible
        self.update()
        return self._visible

    def set_crosshair_visible(self, visible: bool) -> None:
        """Définit explicitement la visibilité du crosshair."""
        self._visible = visible
        self.update()

    def is_crosshair_visible(self) -> bool:
        """Retourne True si le crosshair est actuellement affiché."""
        return self._visible

    # ------------------------------------------------------------------
    # Mode verrouillage (lock) — click-through total
    # ------------------------------------------------------------------

    def set_locked(self, locked: bool) -> None:
        """
        Active/désactive le mode verrouillé.

        En mode verrouillé l'overlay est totalement transparent aux entrées
        (click-through au niveau Windows) et ne perturbe pas le jeu.
        """
        self._locked = locked
        if locked:
            self.setWindowFlags(
                Qt.WindowStaysOnTopHint
                | Qt.FramelessWindowHint
                | Qt.Tool
                | Qt.WindowTransparentForInput
            )
        else:
            self.setWindowFlags(
                Qt.WindowStaysOnTopHint
                | Qt.FramelessWindowHint
                | Qt.Tool
            )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.show()  # Re-show requis après changement de flags

    def is_locked(self) -> bool:
        """Retourne True si l'overlay est verrouillé."""
        return getattr(self, '_locked', False)

    # ------------------------------------------------------------------
    # Déplacement du crosshair
    # ------------------------------------------------------------------

    def move_crosshair(self, dx: int, dy: int) -> None:
        """
        Déplace le crosshair de (dx, dy) pixels.

        Si la position courante est None, part du centre de l'écran.
        """
        cx, cy = self._get_center()
        # Clamp dans les limites de la fenêtre
        new_x = max(0, min(self.width(), cx + dx))
        new_y = max(0, min(self.height(), cy + dy))
        self.config["position_x"] = new_x
        self.config["position_y"] = new_y
        self.update()

    def center_crosshair(self) -> None:
        """Recentre le crosshair au milieu de l'écran."""
        self.config["position_x"] = None
        self.config["position_y"] = None
        self.update()
