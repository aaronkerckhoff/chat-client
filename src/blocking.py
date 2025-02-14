import os
import json
from pathlib import Path

def block(pk):
    try:
        # Convert pk to string to prevent type mismatches
        pk = str(pk)

        # Get the path to the user file in the APPDATA directory
        appdata_path = Path(os.getenv("APPDATA"))
        file_path = appdata_path / "Chat" / "user.txt"

        # Check if the file exists
        if not file_path.exists():
            return
        
        # Read the current blocked users from the file
        with file_path.open("r", encoding="utf-8") as file:
            blocked_users = json.load(file)

        # Ensure the "blocked" key exists
        if "blocked" not in blocked_users:
            blocked_users["blocked"] = []

        # Only add pk to the blocked list if it's not already there
        if pk not in blocked_users["blocked"]:
            blocked_users["blocked"].append(pk)

        # Write the updated blocked users back to the file
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(blocked_users, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")


def unblock(pk):
    try:
        # Convert pk to string to prevent type mismatches
        pk = str(pk)

        # Get the path to the user file in the APPDATA directory
        appdata_path = Path(os.getenv("APPDATA"))
        file_path = appdata_path / "Chat" / "user.txt"

        # Check if the file exists
        if not file_path.exists():
            return
        
        # Read the current blocked users from the file
        with file_path.open("r", encoding="utf-8") as file:
            blocked_users = json.load(file)

        # Ensure the "blocked" key exists
        if "blocked" not in blocked_users:
            return

        # Remove pk from the blocked list if it exists
        if pk in blocked_users["blocked"]:
            blocked_users["blocked"].remove(pk)

            # Write the updated blocked users back to the file
            with file_path.open("w", encoding="utf-8") as file:
                json.dump(blocked_users, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")

def check_blocked(pk):
    try:
        # Convert pk to string to prevent type mismatches
        pk = str(pk)

        # Get the path to the user file in the APPDATA directory
        appdata_path = Path(os.getenv("APPDATA"))
        file_path = appdata_path / "Chat" / "user.txt"

        # Check if the file exists
        if not file_path.exists():
            return False  # If the file doesn't exist, return False
        
        # Read the current blocked users from the file
        with file_path.open("r", encoding="utf-8") as file:
            blocked_users = json.load(file)

        # Ensure the "blocked" key exists
        if "blocked" not in blocked_users:
            return False  # If the "blocked" key doesn't exist, return False

        # Check if pk is in the blocked list
        return pk in blocked_users["blocked"]

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

print(check_blocked(69))