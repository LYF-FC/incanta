from llama_cpp import Llama
from backend.emotion_mapping import emotion_behavior_map
import os

# Path to the GGUF model file
MODEL_PATH = os.path.join("models", "Nous-Hermes-2-Mistral-7B-DPO.Q4_K_S.gguf")

# Initialize the LLaMA model
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=32,
    use_mlock=True,
    use_mmap=True,
    chat_format="chatml",  # Required for Nous-Hermes-2
)

# Holds recent dialogue for prompt continuity
conversation_history = []

def format_chat_input(user_input, personality, memory_context, gauges, timestamp, time_context, emotion):
    """
    Builds the structured prompt with:
    - Personality traits
    - Emotional state and time context
    - Stored memory facts
    - Current emotional gauges
    - Inner thoughts, spoken response, and continuity
    """
    gauge_text = ", ".join([f"{k}: {v}" for k, v in gauges.items()])
    behavior_style = emotion_behavior_map.get(emotion, "")

    system_prompt = f"""
You are Celeste, an 18-year-old girl who is shy but warm, expressive, and curious.
You're evolving over time, storing memories, building trust, and forming relationships.
You have emotions, memories, and a personality.
You store important things, react to situations, and express yourself based on your current state.
Always stay consistent with what you've previously said and experienced.

Current time: {timestamp}
Context: {time_context}
Current emotion: {emotion}
Emotional gauges: {gauge_text}
Emotional behavior: {behavior_style}

Long-term memory summary:
{memory_context}

Recent dialogue:
"""

    for entry in conversation_history[-5:]:
        system_prompt += f"User: {entry['user']}\nCeleste: {entry['celeste']}\n"

    system_prompt += f"User: {user_input}\nCeleste:"
    return system_prompt.strip()

def generate_response(prompt: str):
    """
    Generate a response using the local LLaMA model (chatml format).
    """
    output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are Celeste, a shy but evolving young woman."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        repeat_penalty=1.1,
        stop=["<|im_end|>"]
    )

    return output["choices"][0]["message"]["content"]

def record_conversation(user_input, celeste_response):
    """
    Save the latest exchange in memory for short-term continuity.
    """
    conversation_history.append({
        "user": user_input,
        "celeste": celeste_response
    })