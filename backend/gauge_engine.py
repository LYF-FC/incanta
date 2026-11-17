# backend/gauge_engine.py

import random

# List of gauge keys
GAUGE_KEYS = [
    "Trust",
    "Intimacy",
    "Curiosity",
    "Affection",
    "Confidence",
    "Confusion",
    "Arousal"
]

# Emotion thresholds mapped to dominant gauge values
EMOTION_MAPPING = [
    ("Happy", lambda g: g["Trust"] > 50),
    ("Sad", lambda g: g["Affection"] < 30),
    ("Shy", lambda g: g["Confidence"] < 25),
    ("Angry", lambda g: g["Arousal"] < 20 and g["Confidence"] > 60),
    ("Confident", lambda g: g["Confidence"] > 70),
    ("Curious", lambda g: g["Curiosity"] > 50),
    ("Affectionate", lambda g: g["Affection"] > 60),
    ("Embarrassed", lambda g: g["Confidence"] < 40 and g["Intimacy"] > 40),
    ("Playful", lambda g: g["Curiosity"] > 30 and g["Confidence"] > 30),
    ("Flirty", lambda g: g["Intimacy"] > 50 and g["Arousal"] > 30),
    ("Submissive", lambda g: g["Confidence"] < 30 and g["Intimacy"] > 60),
    ("Dominant", lambda g: g["Confidence"] > 80 and g["Intimacy"] > 40),
    ("Aroused", lambda g: g["Arousal"] > 50),
    ("Pleasured", lambda g: g["Arousal"] > 75),
    ("Orgasmic", lambda g: g["Arousal"] == 100),
    ("Horny", lambda g: g["Arousal"] > 60 and g["Curiosity"] > 40),
    ("Neutral", lambda g: True),  # Fallback after all meaningful rules
]

def update_gauges(user_input: str, response: str, gauges: dict, rng=None) -> dict:
    """
    Adjust gauges based on keywords and responses.
    You can improve this later with an emotion classifier.
    """
    gauges = gauges.copy()
    rng = rng if rng is not None else random
    text = (user_input + " " + response).lower()

    def boost(key, amount=5):
        gauges[key] = min(100, gauges[key] + amount)

    def reduce(key, amount=5):
        gauges[key] = max(0, gauges[key] - amount)

    # Heuristic triggers
    if any(word in text for word in ["trust", "safe", "promise"]):
        boost("Trust", 8)

    if any(word in text for word in ["hug", "love", "dear", "sweet"]):
        boost("Affection", 10)
        boost("Intimacy", 6)

    if "?" in user_input:
        boost("Curiosity", 4)

    if any(word in text for word in ["sorry", "awkward", "shy", "blush"]):
        reduce("Confidence", 5)
        boost("Confusion", 3)

    if any(word in text for word in ["kiss", "touch", "moan", "wet", "hard"]):
        boost("Arousal", 10)
        boost("Intimacy", 4)

    if "angry" in text or "mad" in text:
        boost("Confidence", 5)
        boost("Arousal", 6)

    # Random soft fluctuation
    for k in gauges:
        if k not in ["Arousal"]:
            fluctuation = rng.randint(-1, 1)
            gauges[k] = max(0, min(100, gauges[k] + fluctuation))

    return gauges

def get_current_gauges() -> dict:
    return {k: 0 for k in GAUGE_KEYS}

def determine_emotion(gauges: dict) -> str:
    """
    Returns the current dominant emotion based on the emotion mapping.
    The first match in priority order is returned.
    """
    for emotion, condition in EMOTION_MAPPING:
        if condition(gauges):
            return emotion
    return "Neutral"