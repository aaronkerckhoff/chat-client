from pathlib import Path
import json
import os

config_version = 1

def load_config(path: Path = None) -> dict:
    """Tries to load the current save file from disk. If it can't load from disk, it'll create a new save object"""
    if not path:
        path = get_default_config_path()
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        user_config = json.load(file)

    if "config_version" not in user_config:
        return {}
    if user_config["config_version"] != config_version:
        return {}

    return user_config

def write_config(save: dict, path: Path = None):
    if not path:
        path = get_default_config_path()

    save["config_version"] = config_version

    with path.open("w", encoding="utf-8") as file:
        json.dump(save, file, ensure_ascii=False, indent=4)

def ensure_exists():
    config_path = get_default_config_path()
    parent = config_path.parent # We will at max only create one parent of our config
    if not parent.exists():
        parent.mkdir()
    

    


def get_default_config_path() -> Path:
    if os.name == "nt":
        base_save_path = Path(os.getenv("APPDATA"))
    else:
        base_save_path = Path(os.getenv("HOME"))
        
    return base_save_path / "Chat" / "user.txt"  # Correct path creation