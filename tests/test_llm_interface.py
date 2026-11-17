from dataclasses import replace
import tempfile
import unittest
from unittest.mock import Mock
from helpers import settings_for


class LazyInferenceTests(unittest.TestCase):
    def test_loads_once_and_generates_without_logging_private_exceptions(self):
        from backend.llm_interface import LocalInference
        from backend.errors import AppError
        with tempfile.TemporaryDirectory() as root:
            settings = settings_for(root)
            model = Mock()
            model.create_chat_completion.return_value = {'choices':[{'message':{'content':'synthetic'}}]}
            factory = Mock(return_value=model)
            adapter = LocalInference(settings, factory=factory)
            self.assertEqual(adapter.state(), 'unloaded')
            factory.assert_not_called()
            self.assertEqual(adapter.generate('synthetic prompt'), 'synthetic')
            self.assertEqual(adapter.generate('another prompt'), 'synthetic')
            self.assertEqual(factory.call_count, 1)
            self.assertFalse(factory.call_args.kwargs['verbose'])
            settings.model_path.unlink()
            self.assertEqual(adapter.state(), 'unavailable')
            with self.assertRaises(AppError): adapter.generate('synthetic')

    def test_failed_load_can_be_retried_and_empty_output_is_rejected(self):
        from backend.llm_interface import LocalInference
        from backend.errors import AppError
        with tempfile.TemporaryDirectory() as root:
            model = Mock()
            factory = Mock(side_effect=[RuntimeError('/private/synthetic-path'), model])
            model.create_chat_completion.return_value = {'choices':[{'message':{'content':'  '}}]}
            adapter = LocalInference(settings_for(root), factory=factory)
            with self.assertRaises(AppError) as caught: adapter.generate('text')
            self.assertNotIn('/private', str(caught.exception))
            self.assertEqual(adapter.state(), 'unavailable')
            with self.assertRaises(AppError) as caught: adapter.generate('text')
            self.assertEqual(caught.exception.code, 'generation_failed')
            model.create_chat_completion.return_value = {'choices':[{'message':{'content':'hello'}}]}
            self.assertEqual(adapter.generate('text'), 'hello')
            self.assertEqual(adapter.state(), 'loaded')
