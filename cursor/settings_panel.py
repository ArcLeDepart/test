"""
settings_panel.py - Panneau de configuration de l'application Cursor.

Interface graphique sombre/moderne permettant de personnaliser le crosshair
en temps réel.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_CONFIG

# Style sombre partagé pour tout le panneau
DARK_STYLE = """
QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #444444;
    border-radius: 6px;
    margin-top: 10px;
    padding: 8px;
    font-weight: bold;
    color: #cccccc;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #555555;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #0078d4;
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: #0078d4;
    border-radius: 2px;
}

QPushButton {
    background-color: #3c3c3c;
    color: #e0e0e0;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px 14px;
}

QPushButton:hover {
    background-color: #4a4a4a;
}

QPushButton:pressed {
    background-color: #222222;
}

QComboBox {
    background-color: #3c3c3c;
    color: #e0e0e0;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 3px 8px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    color: #e0e0e0;
    selection-background-color: #0078d4;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #3c3c3c;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
}

QLabel#colorPreview {
    border-radius: 4px;
    border: 1px solid #555555;
    min-width: 32px;
    min-height: 20px;
}
"""


class ColorButton(QPushButton):
    """Bouton affichant une couleur et ouvrant un sélecteur de couleur au clic."""

    colorChanged = pyqtSignal(str)  # hex color

    def __init__(self, color: str = "#FF0000", parent=None):
        super().__init__(parent)
        self._color = color
        self._update_style()
        self.clicked.connect(self._pick_color)
        self.setFixedSize(40, 24)

    def _update_style(self) -> None:
        self.setStyleSheet(
            f"background-color: {self._color}; border: 1px solid #555555;"
            " border-radius: 4px;"
        )

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(
            QColor(self._color), self, "Choisir une couleur"
        )
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.colorChanged.emit(self._color)

    def set_color(self, color: str) -> None:
        self._color = color
        self._update_style()

    def get_color(self) -> str:
        return self._color


class SettingsPanel(QWidget):
    """
    Panneau de paramètres du crosshair.

    Émet le signal `config_changed` à chaque modification,
    avec le dictionnaire de configuration mis à jour.
    """

    config_changed = pyqtSignal(dict)
    center_requested = pyqtSignal()

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self._updating = False  # Garde contre les boucles de mise à jour

        self.setWindowTitle("Cursor — Paramètres")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setFixedWidth(360)
        self.setStyleSheet(DARK_STYLE)

        self._build_ui()
        self._load_values()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Construit tous les widgets du panneau."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        layout.addWidget(self._build_shape_group())
        layout.addWidget(self._build_size_group())
        layout.addWidget(self._build_color_group())
        layout.addWidget(self._build_outline_group())
        layout.addLayout(self._build_buttons())

    def _make_slider(self, min_val: int, max_val: int) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        return slider

    def _labeled_slider(
        self, label_text: str, slider: QSlider, suffix: str = ""
    ) -> tuple:
        """Retourne (layout, value_label) pour un slider avec étiquette."""
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setFixedWidth(90)
        val_label = QLabel()
        val_label.setFixedWidth(36)
        val_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        def _update_label(v):
            val_label.setText(f"{v}{suffix}")

        slider.valueChanged.connect(_update_label)
        _update_label(slider.value())

        row.addWidget(lbl)
        row.addWidget(slider)
        row.addWidget(val_label)
        return row, val_label

    # ------------------------------------------------------------------
    # Groupes de paramètres
    # ------------------------------------------------------------------

    def _build_shape_group(self) -> QGroupBox:
        group = QGroupBox("Forme")
        layout = QVBoxLayout(group)

        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Croix", "Cercle", "Point", "Croix + Cercle"])
        self.shape_combo.currentIndexChanged.connect(self._on_change)
        layout.addWidget(self.shape_combo)
        return group

    def _build_size_group(self) -> QGroupBox:
        group = QGroupBox("Dimensions")
        layout = QVBoxLayout(group)

        self.size_slider = self._make_slider(5, 100)
        row_size, _ = self._labeled_slider("Taille", self.size_slider, " px")
        self.size_slider.valueChanged.connect(self._on_change)
        layout.addLayout(row_size)

        self.thickness_slider = self._make_slider(1, 10)
        row_thick, _ = self._labeled_slider(
            "Épaisseur", self.thickness_slider, " px"
        )
        self.thickness_slider.valueChanged.connect(self._on_change)
        layout.addLayout(row_thick)

        self.gap_slider = self._make_slider(0, 20)
        row_gap, _ = self._labeled_slider("Gap central", self.gap_slider, " px")
        self.gap_slider.valueChanged.connect(self._on_change)
        layout.addLayout(row_gap)

        self.opacity_slider = self._make_slider(10, 100)
        row_op, _ = self._labeled_slider("Opacité", self.opacity_slider, "%")
        self.opacity_slider.valueChanged.connect(self._on_change)
        layout.addLayout(row_op)

        return group

    def _build_color_group(self) -> QGroupBox:
        group = QGroupBox("Couleur")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        row.addWidget(QLabel("Couleur du crosshair"))
        self.color_btn = ColorButton("#FF0000")
        self.color_btn.colorChanged.connect(self._on_change)
        row.addStretch()
        row.addWidget(self.color_btn)
        layout.addLayout(row)

        return group

    def _build_outline_group(self) -> QGroupBox:
        group = QGroupBox("Contour (Outline)")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        self.outline_check = QCheckBox("Activer le contour")
        self.outline_check.stateChanged.connect(self._on_change)
        row.addWidget(self.outline_check)
        layout.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Couleur du contour"))
        self.outline_color_btn = ColorButton("#000000")
        self.outline_color_btn.colorChanged.connect(self._on_change)
        row2.addStretch()
        row2.addWidget(self.outline_color_btn)
        layout.addLayout(row2)

        return group

    def _build_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()

        btn_reset = QPushButton("Réinitialiser")
        btn_reset.clicked.connect(self._on_reset)

        btn_center = QPushButton("Centrer le crosshair")
        btn_center.clicked.connect(self.center_requested.emit)

        row.addWidget(btn_reset)
        row.addWidget(btn_center)
        return row

    # ------------------------------------------------------------------
    # Chargement / lecture des valeurs
    # ------------------------------------------------------------------

    _SHAPE_MAP = {
        "cross": 0,
        "circle": 1,
        "dot": 2,
        "cross_circle": 3,
    }
    _SHAPE_REVERSE = {v: k for k, v in _SHAPE_MAP.items()}

    def _load_values(self) -> None:
        """Initialise les widgets selon la configuration courante."""
        self._updating = True

        self.shape_combo.setCurrentIndex(
            self._SHAPE_MAP.get(self.config.get("shape", "cross"), 0)
        )
        self.size_slider.setValue(self.config.get("size", 20))
        self.thickness_slider.setValue(self.config.get("thickness", 2))
        self.gap_slider.setValue(self.config.get("gap", 4))
        self.opacity_slider.setValue(self.config.get("opacity", 100))
        self.color_btn.set_color(self.config.get("color", "#FF0000"))
        self.outline_check.setChecked(self.config.get("outline", True))
        self.outline_color_btn.set_color(
            self.config.get("outline_color", "#000000")
        )

        self._updating = False

    def _read_values(self) -> dict:
        """Lit les valeurs courantes des widgets et retourne un dict config."""
        config = self.config.copy()
        config["shape"] = self._SHAPE_REVERSE.get(
            self.shape_combo.currentIndex(), "cross"
        )
        config["size"] = self.size_slider.value()
        config["thickness"] = self.thickness_slider.value()
        config["gap"] = self.gap_slider.value()
        config["opacity"] = self.opacity_slider.value()
        config["color"] = self.color_btn.get_color()
        config["outline"] = self.outline_check.isChecked()
        config["outline_color"] = self.outline_color_btn.get_color()
        return config

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_change(self, *_args) -> None:
        """Appelé à chaque modification d'un widget — émet config_changed."""
        if self._updating:
            return
        self.config = self._read_values()
        self.config_changed.emit(self.config)

    def _on_reset(self) -> None:
        """Réinitialise les paramètres aux valeurs par défaut."""
        self.config = DEFAULT_CONFIG.copy()
        self._load_values()
        self.config_changed.emit(self.config)

    # ------------------------------------------------------------------
    # Mise à jour externe
    # ------------------------------------------------------------------

    def refresh_config(self, config: dict) -> None:
        """Met à jour le panneau depuis une configuration externe (ex: hotkey)."""
        self.config = config.copy()
        self._load_values()
