"""One state owner and completion boundary per local application instance."""
import copy
from datetime import datetime
from threading import Lock
from backend.errors import AppError
from backend.gauge_engine import get_current_gauges, update_gauges, determine_emotion
from backend.llm_interface import LocalInference, format_chat_input
from backend.memory_manager import MemoryManager, get_time_context
from backend.personality_loader import load_personality


class ChatEngine:
    def __init__(self, settings, inference=None, memory=None, rng=None):
        self.settings = settings
        self.inference = inference if inference is not None else LocalInference(settings)
        self.memory = memory if memory is not None else MemoryManager(settings.personality_path.stem, settings.data_dir)
        self.rng = rng
        self._state = {'gauges':get_current_gauges(), 'emotion':'Neutral', 'history':[]}
        self._processing = Lock()

    @property
    def history(self):
        return copy.deepcopy(self._state['history'])

    def status(self):
        issues = []
        if not self.settings.valid:
            issues.append('invalid_configuration')
        model_state = self.inference.state()
        if model_state == 'unavailable':
            issues.append('model_unavailable')
        try:
            load_personality(self.settings.personality_path)
        except AppError as error:
            issues.append(error.code)
        try:
            self.memory.check_storage()
            self.memory.load_memory()
        except AppError as error:
            issues.append(error.code)
        state = self._state
        return {'status':'ok', 'ready':not issues, 'model_state':model_state,
                'issues':issues, 'emotion':state['emotion'], 'gauges':dict(state['gauges'])}

    def process(self, user_input):
        # Defend the service boundary too, even when called without HTTP.
        if not isinstance(user_input, str) or not user_input.strip():
            raise AppError('invalid_request')
        user_input = user_input.strip()
        if len(user_input) > 8000:
            raise AppError('input_too_large')
        if not self._processing.acquire(blocking=False):
            raise AppError('conversation_busy')
        try:
            if not self.settings.valid:
                raise AppError('invalid_configuration')
            personality = load_personality(self.settings.personality_path)
            self.memory.check_storage()
            document = self.memory.load_memory()
            state = self._state
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            prompt = format_chat_input(user_input, personality,
                                       self.memory.get_context_snippet(document),
                                       state['gauges'], timestamp, get_time_context(),
                                       state['emotion'], state['history'])
            try:
                response = self.inference.generate(prompt)
                if not isinstance(response, str) or not response.strip():
                    raise ValueError
                response = response.strip()
            except AppError:
                raise
            except Exception:
                raise AppError('generation_failed') from None
            gauges = update_gauges(user_input, response, state['gauges'], rng=self.rng)
            emotion = determine_emotion(gauges)
            history = (state['history'] + [{'user':user_input, 'celeste':response}])[-5:]
            # Prepare all allocations before commit; publish with one pointer assignment.
            next_state = {'gauges':gauges, 'emotion':emotion, 'history':history}
            result = {'response':response, 'gauges':dict(gauges), 'emotion':emotion}
            self.memory.append_event(user_input, response, timestamp)
            self._state = next_state
            return result
        finally:
            self._processing.release()
