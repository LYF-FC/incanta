import json
import os
from typing import List, Dict, Optional
from datetime import datetime

MEMORY_PATH = "chat_histories"

class MemoryManager:
    def __init__(self, character_name: str):
        self.character_name = character_name.lower()
        os.makedirs(MEMORY_PATH, exist_ok=True)
        self.memory_file = os.path.join(MEMORY_PATH, f"{self.character_name}_memory.json")
        self.memory = self.load_memory()

    def load_memory(self) -> Dict:
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "timeline": [],
                "milestones": {},
                "emotions": {},
                "beliefs": {},
                "desires": {},
                "reflections": [],
                "adaptive_style": {}
            }

    def save_memory(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def add_timeline_event(self, user_input: str, ai_response: str, timestamp: Optional[str] = None):
        timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.memory["timeline"].append({
            "timestamp": timestamp,
            "user": user_input,
            "celeste": ai_response
        })
        self.save_memory()

    def add_milestone(self, key: str, value: str):
        self.memory["milestones"][key] = value
        self.save_memory()

    def update_emotion(self, topic: str, feeling: str):
        self.memory["emotions"][topic] = feeling
        self.save_memory()

    def update_belief(self, belief: str, value: str):
        self.memory["beliefs"][belief] = value
        self.save_memory()

    def update_desire(self, goal: str, status: str):
        self.memory["desires"][goal] = status
        self.save_memory()

    def add_reflection(self, entry: str):
        self.memory["reflections"].append(entry)
        self.save_memory()

    def update_style(self, key: str, value: str):
        self.memory["adaptive_style"][key] = value
        self.save_memory()

    def get_memory(self) -> Dict:
        return self.memory

    def get_context_snippet(self, max_events: int = 5) -> str:
        timeline = self.memory["timeline"][-max_events:]
        memories = []

        for item in timeline:
            timestamp = item.get("timestamp", "")
            user = item.get("user", "")
            celeste = item.get("celeste", "")
            memories.append(f"[{timestamp}] You: {user}\nCeleste: {celeste}")

        for key, val in self.memory["milestones"].items():
            memories.append(f"[FACT] {key}: {val}")

        return "\n".join(memories[-max_events:])

# --- NEW FUNCTION OUTSIDE THE CLASS ---
def update_memories(user_input: str, response: str, timestamp: str):
    """
    Updates Celeste's memory with new conversation turns.
    """
    mem = MemoryManager("celeste")
    mem.add_timeline_event(user_input, response, timestamp)

    # example: store milestones if keywords appear
    if "brother" in response.lower():
        mem.add_milestone("has_siblings", "yes")

    print(f"[Memory] Updated at {timestamp}")

def retrieve_relevant_memories(user_input: str) -> str:
    """
    For now, return the last few memories as string context.
    Later this can be improved with keyword search or embeddings.
    """
    mem = MemoryManager("celeste")
    return mem.get_context_snippet(max_events=5)

def store_event(user_input: str, response: str, timestamp: Optional[str] = None):
    """
    Saves a new timeline entry to the memory file for Celeste.
    """
    mem = MemoryManager("celeste")
    mem.add_timeline_event(user_input, response, timestamp)

from datetime import datetime

def get_time_context() -> str:
    """
    Returns a human-readable time context like:
    'Monday morning', 'Saturday night', etc.
    """
    now = datetime.now()
    day = now.strftime("%A")
    hour = now.hour

    if 5 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 17:
        period = "afternoon"
    elif 17 <= hour < 21:
        period = "evening"
    else:
        period = "night"

    return f"{day} {period}"