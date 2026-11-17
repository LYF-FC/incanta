"""Synthetic fixtures only: no real weights, histories or character definitions."""
from dataclasses import replace
import json
from pathlib import Path
from backend.config import Settings


class FakeInference:
    def __init__(self, reply="A synthetic response."):
        self.reply = reply
        self.calls = 0
        self.prompts = []
        self.failure = None

    def state(self):
        return "unloaded" if not self.calls else "loaded"

    def generate(self, prompt):
        self.calls += 1
        self.prompts.append(prompt)
        if self.failure:
            raise self.failure
        return self.reply


def settings_for(root):
    root = Path(root)
    personality = root / "synthetic.json"
    personality.write_text(json.dumps({"name": "Synthetic"}))
    model = root / "synthetic.gguf"
    model.write_bytes(b"not real weights; injected adapter only")
    return replace(Settings(), model_path=model, personality_path=personality,
                   data_dir=root / "histories")
