# 🎯 Cursor — Crosshair Overlay

> Crosshair overlay personnalisable pour Windows, développé en Python avec PyQt5.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green)
![Windows](https://img.shields.io/badge/Windows-10%2F11-blue)
![License](https://img.shields.io/badge/licence-MIT-lightgrey)

---

## 📋 Description

**Cursor** est un logiciel de crosshair overlay qui affiche un viseur personnalisable par-dessus toutes les fenêtres, y compris les jeux en mode fenêtré ou sans bordure.  
Il est conçu pour être léger, discret et entièrement configurable via un panneau de paramètres moderne.

### Fonctionnalités principales

- 🎯 **4 formes de crosshair** : Croix, Cercle, Point, Croix + Cercle  
- 🎨 **Personnalisation complète** : taille, épaisseur, couleur, opacité, gap, contour  
- ⌨️  **Raccourcis clavier globaux** pour contrôler l'overlay sans quitter le jeu  
- 🖥️  **System tray** pour un accès rapide aux paramètres  
- 💾 **Sauvegarde automatique** de la configuration (JSON)  
- 🪟 **Click-through** : les clics passent à travers l'overlay  
- 📦 **Compilable en .exe** standalone avec PyInstaller  

---

## 🗂️ Structure du projet

```
cursor/
├── main.py                  # Point d'entrée de l'application
├── crosshair_overlay.py     # Fenêtre overlay transparente (crosshair)
├── settings_panel.py        # Panneau de configuration (UI sombre)
├── hotkey_manager.py        # Raccourcis clavier globaux (pynput)
├── config.py                # Sauvegarde/chargement de la configuration JSON
├── requirements.txt         # Dépendances Python
├── build.bat                # Script de compilation en .exe
└── assets/
    └── icon.ico             # Icône de l'application
```

---

## 🚀 Installation et lancement

### Prérequis

- Windows 10 ou Windows 11
- Python 3.10 ou supérieur

### 1. Cloner le dépôt

```bash
git clone https://github.com/ArcLeDepart/test.git
cd test/cursor
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
python main.py
```

---

## 📦 Compilation en .exe standalone

### Méthode automatique (recommandée)

```bash
cd cursor
build.bat
```

Le script installe automatiquement PyInstaller et compile l'application.  
L'exécutable se trouve dans `cursor/dist/Cursor.exe`.

### Méthode manuelle

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name Cursor --icon assets\icon.ico --add-data "assets;assets" main.py
```

---

## ⌨️ Raccourcis clavier

Tous les raccourcis fonctionnent même quand l'application n'est **pas** au premier plan.

| Raccourci | Action |
|-----------|--------|
| `Ctrl+Alt+↑↓←→` | Déplace le crosshair de **1 pixel** |
| `Ctrl+Alt+Shift+↑↓←→` | Déplace le crosshair de **10 pixels** |
| `Ctrl+Alt+C` | **Centre** le crosshair sur l'écran |
| `Ctrl+Alt+S` | **Affiche/cache** le panneau de paramètres |
| `Ctrl+Alt+H` | **Affiche/cache** le crosshair |
| `Ctrl+Alt+Q` | **Quitte** l'application |

---

## ⚙️ Paramètres disponibles

| Paramètre | Valeurs | Défaut |
|-----------|---------|--------|
| Forme | Croix / Cercle / Point / Croix+Cercle | Croix |
| Taille | 5 — 100 px | 20 px |
| Épaisseur | 1 — 10 px | 2 px |
| Couleur | Sélecteur de couleur | Rouge (#FF0000) |
| Opacité | 10 % — 100 % | 100 % |
| Gap central | 0 — 20 px | 4 px |
| Contour | Activé / Désactivé | Activé |
| Couleur du contour | Sélecteur de couleur | Noir (#000000) |

---

## 💾 Configuration

La configuration est sauvegardée automatiquement dans `cursor_config.json` (à côté de l'exécutable ou dans `%APPDATA%\Cursor\`).

Exemple de fichier de configuration :

```json
{
  "shape": "cross",
  "size": 20,
  "thickness": 2,
  "color": "#FF0000",
  "opacity": 100,
  "gap": 4,
  "outline": true,
  "outline_color": "#000000",
  "position_x": null,
  "position_y": null
}
```

---

## 🖥️ System Tray

Une icône apparaît dans la zone de notification (system tray) :

- **Clic droit** → menu contextuel : Paramètres, Centrer, Afficher/Masquer, Quitter  
- **Double-clic** → ouvre le panneau de paramètres  

---

## ❓ FAQ / Dépannage

### L'overlay n'apparaît pas
- Vérifiez que vous n'êtes pas en mode plein écran exclusif (utilisez le mode fenêtré sans bordure).
- Relancez l'application en tant qu'administrateur si nécessaire.

### Les raccourcis ne fonctionnent pas
- Assurez-vous que `pynput` est bien installé : `pip install pynput`.
- Sur certains systèmes, les droits d'accès aux événements clavier peuvent être restreints.

### L'application plante au démarrage
- Vérifiez que PyQt5 est correctement installé : `pip install PyQt5`.
- Consultez les logs dans la console (lancez `python main.py` depuis un terminal).

### Comment réinitialiser la configuration ?
- Dans le panneau de paramètres, cliquez sur **Réinitialiser**.
- Ou supprimez manuellement `cursor_config.json`.

---

## 🛠️ Dépendances

| Package | Version minimale | Rôle |
|---------|-----------------|------|
| PyQt5 | 5.15.0 | Interface graphique et overlay |
| pynput | 1.7.6 | Raccourcis clavier globaux |

---

## 📄 Licence

MIT — Voir [LICENSE](LICENSE) pour plus de détails.