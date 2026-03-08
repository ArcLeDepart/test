"""
config.py - Gestion de la configuration de l'application Cursor.

Sauvegarde et chargement de la configuration au format JSON.
"""

import json
import os
import sys


# Valeurs par défaut de la configuration
DEFAULT_CONFIG = {
    "shape": "cross",
    "size": 20,
    "thickness": 2,
    "color": "#FF0000",
    "opacity": 100,
    "gap": 4,
    "outline": True,
    "outline_color": "#000000",
    "position_x": None,
    "position_y": None,
}


def get_config_path() -> str:
    """
    Retourne le chemin vers le fichier de configuration.

    Utilise le dossier de l'exécutable en priorité,
    sinon %APPDATA%/Cursor/ sur Windows.
    """
    # Si on est dans un exécutable PyInstaller
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        # En mode développement : dossier du script
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    config_file = os.path.join(exe_dir, "cursor_config.json")

    # Vérifier si on peut écrire dans ce dossier
    try:
        test_path = os.path.join(exe_dir, ".write_test")
        with open(test_path, "w") as f:
            f.write("")
        os.remove(test_path)
        return config_file
    except OSError:
        pass

    # Repli sur %APPDATA%/Cursor/
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    config_dir = os.path.join(appdata, "Cursor")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "cursor_config.json")


def load_config() -> dict:
    """
    Charge la configuration depuis le fichier JSON.

    Retourne la configuration par défaut si le fichier n'existe pas
    ou s'il est invalide.
    """
    config_path = get_config_path()
    config = DEFAULT_CONFIG.copy()

    if not os.path.exists(config_path):
        return config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Fusion : on garde les valeurs par défaut pour les clés manquantes
        for key, value in data.items():
            if key in config:
                config[key] = value
    except (json.JSONDecodeError, OSError) as e:
        print(f"[Config] Erreur lors du chargement : {e}")

    return config


def save_config(config: dict) -> None:
    """
    Sauvegarde la configuration dans le fichier JSON.

    Paramètres :
        config (dict) : Dictionnaire de configuration à sauvegarder.
    """
    config_path = get_config_path()

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[Config] Erreur lors de la sauvegarde : {e}")
