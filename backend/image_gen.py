import os
from typing import Optional
from datetime import datetime

IMAGES_PATH = "generated_images"
os.makedirs(IMAGES_PATH, exist_ok=True)

class ImageGenerator:
    def __init__(self, character_name: str):
        self.character_name = character_name.lower()

    def generate_metadata(self, emotion: str, context: Optional[str] = "") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.character_name}_{emotion}_{timestamp}.json"
        filepath = os.path.join(IMAGES_PATH, filename)

        metadata = {
            "character": self.character_name,
            "emotion": emotion,
            "context": context,
            "timestamp": timestamp
        }

        with open(filepath, "w", encoding="utf-8") as f:
            import json
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return filepath