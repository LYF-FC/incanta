import datetime

# Initial gauge values
initial_gauges = {
    "Trust": 0,
    "Intimacy": 0,
    "Curiosity": 0,
    "Affection": 0,
    "Confidence": 0,
    "Confusion": 0,
    "Arousal": 0,
}

# Threshold mapping for emotional triggers
emotion_map = [
    ("Orgasmic", lambda g: g["Arousal"] == 100),
    ("Pleasured", lambda g: g["Arousal"] > 75),
    ("Aroused", lambda g: g["Arousal"] > 50),
    ("Horny", lambda g: g["Arousal"] > 60 and g["Curiosity"] > 40),
    ("Flirty", lambda g: g["Intimacy"] > 50 and g["Arousal"] > 30),
    ("Submissive", lambda g: g["Confidence"] < 30 and g["Intimacy"] > 60),
    ("Dominant", lambda g: g["Confidence"] > 80 and g["Intimacy"] > 40),
    ("Embarrassed", lambda g: g["Confidence"] < 40 and g["Intimacy"] > 40),
    ("Affectionate", lambda g: g["Affection"] > 60),
    ("Sad", lambda g: g["Affection"] < 30),
    ("Angry", lambda g: g["Arousal"] < 20 and g["Confidence"] > 60),
    ("Confident", lambda g: g["Confidence"] > 70),
    ("Shy", lambda g: g["Confidence"] < 25),
    ("Playful", lambda g: g["Curiosity"] > 30 and g["Confidence"] > 30),
    ("Curious", lambda g: g["Curiosity"] > 50),
    ("Happy", lambda g: g["Affection"] > 40 and g["Trust"] > 30),
    ("Neutral", lambda g: True),
]

class CharacterState:
    def __init__(self):
        self.gauges = initial_gauges.copy()
        self.last_update = datetime.datetime.now()
        self.current_emotion = "Neutral"
        self.schedule = {
            "sleep": {"start": 0, "end": 7},
            "work": {"start": 9, "end": 17},
            "free": {"start": 18, "end": 23}
        }

    def update_gauge(self, name, delta):
        if name not in self.gauges:
            return

        before = self.gauges[name]
        self.gauges[name] = max(0, min(100, before + delta))

    def get_gauges(self):
        return self.gauges

    def get_emotion(self):
        for emotion, condition in emotion_map:
            if condition(self.gauges):
                self.current_emotion = emotion
                return emotion
        return "Neutral"

    def set_gauge(self, name, value):
        if name in self.gauges:
            self.gauges[name] = max(0, min(100, value))

    def get_current_schedule_period(self):
        hour = datetime.datetime.now().hour
        if self.schedule["sleep"]["start"] <= hour < self.schedule["sleep"]["end"]:
            return "sleeping"
        elif self.schedule["work"]["start"] <= hour < self.schedule["work"]["end"]:
            return "working"
        elif self.schedule["free"]["start"] <= hour <= self.schedule["free"]["end"]:
            return "free"
        return "idle"

    def get_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M")