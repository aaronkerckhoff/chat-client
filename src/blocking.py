import os
import json
from pathlib import Path
from . import user_config

def load_blocked_config() -> dict:
    """Loads the config, ensuring the blocked key is set up if not present"""

    config = user_config.load_config()

    if "blocked" not in config:
        config["blocked"] = []
    
    return config


def block(pk: str):
    try:
        config = load_blocked_config()

        if pk not in config["blocked"]:
            config["blocked"].append(pk)
            # We only need to save if we changed the config
            user_config.write_config(config)
    except Exception as e:
        print(f"An error occurred trying to block the user: {e}")


def unblock(pk: str):
    try:
        blocked_users = load_blocked_config()

        # Remove pk from the blocked list if it exists
        if pk in blocked_users["blocked"]:
            blocked_users["blocked"].remove(pk)
            user_config.write_config(blocked_users)

    except Exception as e:
        print(f"An error occurred trying to unblock the user: {e}")

def check_blocked(pk: str):
    try:
        blocked_users = load_blocked_config()

        # Check if pk is in the blocked list
        return pk in blocked_users["blocked"]

    except Exception as e:
        print(f"An error occurred trying to load whether a user was blocked: {e}")
        return False