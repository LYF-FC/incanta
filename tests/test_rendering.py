import unittest
from uuid import uuid4

from backend.errors import AppError
from backend.rendering.comfyui_adapter import ComfyUI, output_descriptor
from backend.rendering.workflow import Workflow


class RenderingTests(unittest.TestCase):
    def test_reject_non_loopback_and_unsafe_outputs(self):
        for url in ('https://localhost:8188', 'http://localhost@other:8188',
                    'http://127.0.0.1:8188/api', 'http://127.0.0.2:8188'):
            with self.subTest(url=url), self.assertRaises(AppError):
                ComfyUI(url)
        for name in ('../file.png', '/file.png', 'other\\file.png', 'x.png [input]'):
            with self.subTest(name=name), self.assertRaises(AppError):
                output_descriptor({'filename': name, 'subfolder': 'incanta', 'type': 'output'})

    def test_resolved_hidden_inputs_survive_scene_binding(self):
        value = {'version': 1, 'comfyui_version': 'synthetic', 'comfyui_revision': 'b' * 40, 'photoshoot_revision': 'a' * 40,
                 'output_node': '2', 'scene_input': ['1', 'text'],
                 'photoshoot_state': [['1', 'builder_state']],
                 'prompt': {'1': {'class_type': 'PhotoSynthetic',
                                  'inputs': {'builder_state': '{"expression":"smile"}', 'text': '{incanta_scene}'}},
                            '2': {'class_type': 'SaveImage',
                                  'inputs': {'filename_prefix': 'sample', 'images': ['1', 0]}}}}
        workflow = Workflow(value)
        job = str(uuid4())
        graph = workflow.render('A park', job)
        self.assertEqual(graph['1']['inputs']['builder_state'], '{"expression":"smile"}')
        self.assertEqual(graph['1']['inputs']['text'], 'A park')
        self.assertEqual(graph['2']['inputs']['filename_prefix'], f'incanta/{job}')
        del value['prompt']['1']['inputs']['builder_state']
        with self.assertRaises(AppError):
            Workflow(value)

    def test_object_info_validates_actual_hidden_group(self):
        bundle = {'version': 1, 'comfyui_version': 'synthetic', 'comfyui_revision': 'b' * 40,
                  'photoshoot_revision': 'a' * 40, 'output_node': '3', 'scene_input': ['2', 'scene'],
                  'photoshoot_state': [['1', 'ExpressionState']],
                  'prompt': {
                      '1': {'class_type': 'Krea2ExpressionBuilder', 'inputs': {'seed': 12, 'ExpressionState': '{}'}},
                      '2': {'class_type': 'SyntheticTextToImage',
                            'inputs': {'scene': 'portrait {incanta_scene}', 'expression': ['1', 0]}},
                      '3': {'class_type': 'SaveImage', 'inputs': {'filename_prefix': 'sample', 'images': ['2', 0]}}}}
        nodes = {
            'Krea2ExpressionBuilder': {'category': 'Photoshoot', 'output': ['STRING'],
                                      'input': {'required': {'seed': ['INT', {}]},
                                                'hidden': {'ExpressionState': ['STRING', {}]}}},
            'SyntheticTextToImage': {'output': ['IMAGE'], 'input': {'required': {
                'scene': ['STRING', {}], 'expression': ['STRING', {}]}}},
            'SaveImage': {'output_node': True, 'input': {'required': {
                'filename_prefix': ['STRING', {}], 'images': ['IMAGE', {}]}}},
        }
        workflow = Workflow(bundle)
        workflow.validate_nodes(nodes)
        graph = workflow.render('atrium', str(uuid4()))
        self.assertEqual(graph['2']['inputs']['scene'], 'portrait atrium')
        nodes['Krea2ExpressionBuilder']['input']['hidden']['PersonState'] = ['STRING', {}]
        with self.assertRaises(AppError):
            workflow.validate_nodes(nodes)

    def test_cancel_targets_only_incanta_pending_job(self):
        from unittest.mock import patch

        job, foreign = str(uuid4()), str(uuid4())
        renderer = ComfyUI('http://127.0.0.1:8188', dedicated=True)
        queue = {'queue_running': [[1, foreign, {}, {}]],
                 'queue_pending': [[2, job, {}, {'incanta_job': job}]]}
        with patch.object(renderer, 'queue', return_value=queue), \
                patch.object(renderer, '_request') as request, \
                patch.object(renderer, 'poll', return_value=('missing', None)):
            self.assertFalse(renderer.cancel_owned(foreign, job))
            request.assert_not_called()
            self.assertTrue(renderer.cancel_owned(job, job))
            request.assert_called_once_with('POST', '/queue', {'delete': [job]})

    def test_timeout_is_uncertain_and_http_body_is_capped(self):
        from unittest.mock import MagicMock, patch

        renderer = ComfyUI('http://127.0.0.1:8188', dedicated=True)
        connection = MagicMock()
        response = connection.getresponse.return_value
        response.status = 200
        response.length = 9
        with patch('backend.rendering.comfyui_adapter.HTTPConnection', return_value=connection):
            with self.assertRaises(AppError):
                renderer._request('GET', '/queue', limit=8)
            response.read1.assert_not_called()
            response.length = None
            response.read1.return_value = b'123456789'
            with self.assertRaises(AppError):
                renderer._request('GET', '/queue', limit=8)
            response.read1.assert_called_once_with(9)
            connection.request.side_effect = TimeoutError
            with self.assertRaises(AppError) as caught:
                renderer.submit({}, str(uuid4()))
            self.assertEqual(caught.exception.code, 'render_uncertain')

    def test_asset_decoding_rejects_type_mismatch_truncation_and_oversize(self):
        from io import BytesIO
        from PIL import Image
        from backend.rendering.assets import decode
        from backend.rendering.comfyui_adapter import MAX_IMAGE

        picture = BytesIO()
        Image.new('RGB', (2, 2)).save(picture, format='PNG')
        data = picture.getvalue()
        self.assertEqual(decode(data, 'image/png'), (2, 2))
        for malformed, claimed in ((data, 'image/jpeg'), (data[:42], 'image/png'),
                                   (b'0' * (MAX_IMAGE + 1), 'image/png')):
            with self.assertRaises(AppError) as caught:
                decode(malformed, claimed)
            self.assertEqual(caught.exception.code, 'asset_invalid')
