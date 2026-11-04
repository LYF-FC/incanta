import os
import json

# Folder where all personality JSON files are stored
PERSONALITY_DIR = os.path.join("backend", "personalities")

def load_personality(name: str) -> dict:
    """
    Load a personality configuration by name from JSON.

    Args:
        name (str): Name of the character file (without .json)

    Returns:
        dict: Personality definition
    """
    filename = f"{name.lower()}.json"
    filepath = os.path.join(PERSONALITY_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[❌] Personality file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def list_personalities() -> list:
    """
    List all available personality JSONs in the folder.

    Returns:
        list: List of personality names (without .json)
    """
    if not os.path.exists(PERSONALITY_DIR):
        return []

    return [
        os.path.splitext(f)[0]
        for f in os.listdir(PERSONALITY_DIR)
        if f.endswith(".json")
    ]