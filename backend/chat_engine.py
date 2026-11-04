from backend.llm_interface import (
    generate_response,
    format_chat_input,
    record_conversation
)
from backend.memory_manager import (
    update_memories,
    retrieve_relevant_memories,
    store_event,
    get_time_context
)
from backend.personality_loader import load_personality
from backend.gauge_engine import (
    update_gauges,
    get_current_gauges,
    determine_emotion
)
from datetime import datetime

# Load Celeste's personality configuration
personality = load_personality("celeste")

# Persistent state for the session
conversation_history = []
gauges = {
    "Trust": 0,
    "Intimacy": 0,
    "Curiosity": 0,
    "Affection": 0,
    "Confidence": 0,
    "Confusion": 0,
    "Arousal": 0
}
current_emotion = "Neutral"

def process_user_input(user_input: str):
    global gauges, current_emotion

    # 🕓 Timestamp and time-of-day awareness
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    time_context = get_time_context()

    # 🧠 Retrieve memory context relevant to the user input
    memory_context = retrieve_relevant_memories(user_input)

    # 🧩 Construct structured input prompt with emotion & behavior
    prompt = format_chat_input(
        user_input=user_input,
        personality=personality,
        memory_context=memory_context,
        gauges=gauges,
        timestamp=timestamp,
        time_context=time_context,
        emotion=current_emotion
    )

    # 🧠 Generate model response using LLM
    response = generate_response(prompt)

    # 💬 Save to local dialogue history (used for short-term context)
    record_conversation(user_input, response)

    # 📈 Update emotional state based on input and model reply
    gauges = update_gauges(user_input, response, gauges)
    current_emotion = determine_emotion(gauges)

    # 🗂️ Persist new memories and timeline events
    update_memories(user_input, response, timestamp)
    store_event(user_input, response, timestamp)

    return response, gauges, current_emotion