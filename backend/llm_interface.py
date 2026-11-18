"""Pure prompt construction and an explicitly lazy, local-only inference adapter."""
import importlib.util
import os
from backend.emotion_mapping import emotion_behavior_map
from backend.errors import AppError


def format_chat_input(user_input, personality, memory_context, gauges, timestamp,
                      time_context, emotion, history=()):
    # Personality schema/prompt integration is M3; retain the baseline persona.
    gauge_text = ', '.join(f'{key}: {value}' for key, value in gauges.items())
    prompt = f'''You are Celeste, a shy but warm, expressive and curious young woman.
Stay consistent with previously shared events and the current conversation.
Current time: {timestamp}
Context: {time_context}
Current emotion: {emotion}
Emotional gauges: {gauge_text}
Emotional behavior: {emotion_behavior_map.get(emotion, '')}
Long-term memory summary:
{memory_context}
Recent dialogue:
'''
    for entry in history[-5:]:
        prompt += f"User: {entry['user']}\nCeleste: {entry['celeste']}\n"
    return (prompt + f'User: {user_input}\nCeleste:').strip()


class LocalInference:
    def __init__(self, settings, factory=None):
        self.settings = settings
        self._factory = factory
        self._model = None
        self._load_failed = False

    def _assets_available(self):
        path = self.settings.model_path
        try:
            if not (path.is_file() and path.stat().st_size > 0 and os.access(path, os.R_OK)):
                return False
            return self._factory is not None or importlib.util.find_spec('llama_cpp') is not None
        except (OSError, ImportError, ValueError):
            return False

    def state(self):
        if not self._assets_available() or self._load_failed:
            return 'unavailable'
        return 'loaded' if self._model is not None else 'unloaded'

    def unload(self):
        if self._model is not None:
            try:
                self._model.close()
            except Exception:
                raise AppError('render_handoff') from None
            self._model = None

    def generate(self, prompt):
        if not self._assets_available():
            raise AppError('model_unavailable')
        if self._model is None:
            try:
                factory = self._factory
                if factory is None:
                    from llama_cpp import Llama
                    factory = Llama
                self._model = factory(
                    model_path=str(self.settings.model_path),
                    n_ctx=self.settings.context_length, n_threads=self.settings.threads,
                    n_gpu_layers=self.settings.gpu_layers, use_mmap=True,
                    use_mlock=False, chat_format='chatml', verbose=False,
                )
                self._load_failed = False
            except Exception:
                self._load_failed = True
                raise AppError('model_unavailable') from None
        try:
            output = self._model.create_chat_completion(
                messages=prompt if isinstance(prompt, list) else [
                    {'role':'system', 'content':'Follow the supplied local conversation instructions.'},
                    {'role':'user', 'content':prompt}],
                temperature=0.7, top_p=0.95, top_k=40, repeat_penalty=1.1,
                max_tokens=256, stop=['<|im_end|>'],
            )
            response = output['choices'][0]['message']['content']
            if not isinstance(response, str) or not response.strip():
                raise ValueError
            return response.strip()
        except Exception:
            raise AppError('generation_failed') from None
