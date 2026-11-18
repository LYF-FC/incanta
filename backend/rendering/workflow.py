"""Load a private, resolved Photoshoot API prompt and bind one scene."""
from copy import deepcopy
from hashlib import sha256
import json
import re

from backend.errors import AppError
from backend.rendering.files import readable

CONFIG_ID = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}')
NODE_ID = re.compile(r'[0-9]+(?::[0-9]+)*')
NODE_CLASS = re.compile(r'[a-zA-Z0-9_ -]{1,96}')
MAX_WORKFLOW = 1024 * 1024
SCENE_MARKER = '{incanta_scene}'


def relative_parts(name):
    if not isinstance(name, str) or len(name) > 240 or '\\' in name:
        raise ValueError
    parts = name.split('/')
    if any(part in {'', '.', '..'} or part != part.strip()
           or any(ord(char) < 32 or char in ':[]' for char in part) for part in parts):
        raise ValueError
    return parts


class Workflow:
    def __init__(self, bundle, reference_root=None):
        try:
            self._validate(bundle, reference_root)
            data = json.dumps([bundle, self.reference_digests], sort_keys=True, allow_nan=False)
            self.digest = sha256(data.encode()).hexdigest()
        except (AttributeError, KeyError, TypeError, ValueError, OSError, RecursionError):
            raise AppError('renderer_incompatible') from None

    @classmethod
    def load(cls, root, reference_root, selection):
        if root is None or not selection:
            raise AppError('renderer_unconfigured')
        if not isinstance(selection, str) or not CONFIG_ID.fullmatch(selection):
            raise AppError('invalid_request')
        try:
            with readable(root, [selection + '.json']) as stream:
                data = stream.read(MAX_WORKFLOW + 1)
            if len(data) > MAX_WORKFLOW:
                raise ValueError
            return cls(json.loads(data), reference_root)
        except (OSError, ValueError, RecursionError):
            raise AppError('renderer_incompatible') from None

    def _validate(self, bundle, reference_root):
        self.prompt = deepcopy(bundle['prompt'])
        self.output_node = bundle['output_node']
        self.scene_input = deepcopy(bundle['scene_input'])
        self.comfyui_version = bundle['comfyui_version']
        comfyui_revision = bundle['comfyui_revision']
        photoshoot_revision = bundle['photoshoot_revision']
        self.photoshoot_state = deepcopy(bundle['photoshoot_state'])
        if (type(bundle['version']) is not int or bundle['version'] != 1
                or not re.fullmatch(r'[\w.+-]{1,64}', self.comfyui_version)
                or not re.fullmatch(r'[a-f0-9]{40}', photoshoot_revision)
                or not re.fullmatch(r'[a-f0-9]{40}', comfyui_revision)
                or not isinstance(self.prompt, dict) or not 1 <= len(self.prompt) <= 256
                or not isinstance(self.photoshoot_state, list) or not self.photoshoot_state):
            raise ValueError
        references = {}
        for node_id, node in self.prompt.items():
            if (not NODE_ID.fullmatch(node_id) or set(node) - {'class_type', 'inputs', '_meta'}
                    or not NODE_CLASS.fullmatch(node['class_type']) or not isinstance(node['inputs'], dict)):
                raise ValueError
            node.pop('_meta', None)
            if node['class_type'] in {'LoadImage', 'LoadImageMask'}:
                reference = relative_parts(node['inputs']['image'])
                reference_id = node['inputs']['image']
                if reference_id not in references:
                    with readable(reference_root, reference) as stream:
                        data = stream.read(20 * 1024 * 1024 + 1)
                    if not 1 <= len(data) <= 20 * 1024 * 1024:
                        raise ValueError
                    references[reference_id] = sha256(data).hexdigest()
            for key, value in node['inputs'].items():
                if key in {'lora_name', 'ckpt_name', 'vae_name', 'unet_name'} and isinstance(value, str):
                    relative_parts(value)
                if isinstance(value, list):
                    if (len(value) != 2 or value[0] not in self.prompt
                            or type(value[1]) is not int or value[1] < 0):
                        raise ValueError
        self.reference_digests = references
        for binding in self.photoshoot_state:
            _, _, state = self.binding(binding)
            if not isinstance(json.loads(state), dict):
                raise ValueError
        if self.scene_input in self.photoshoot_state:
            raise ValueError
        _, _, template = self.binding(self.scene_input)
        if template.count(SCENE_MARKER) != 1:
            raise ValueError
        output = self.prompt[self.output_node]
        if output['class_type'] != 'SaveImage' or not isinstance(output['inputs']['filename_prefix'], str):
            raise ValueError

    def binding(self, binding):
        if not isinstance(binding, list) or len(binding) != 2:
            raise ValueError
        node_id, key = binding
        value = self.prompt[node_id]['inputs'][key]
        if not isinstance(value, str):
            raise ValueError
        return node_id, key, value

    def validate_nodes(self, nodes):
        try:
            for node_id, node in self.prompt.items():
                info = nodes[node['class_type']]
                if info.get('api_node') or (info.get('output_node') and node_id != self.output_node):
                    raise ValueError
                inputs = info['input']
                required = inputs.get('required', {})
                hidden = {key: spec for key, spec in inputs.get('hidden', {}).items()
                          if isinstance(spec, list) and spec and spec[0] == 'STRING'}
                allowed = {**required, **inputs.get('optional', {}), **hidden}
                declared = {key for subject, key in self.photoshoot_state if subject == node_id}
                is_photoshoot = ('photoshoot' in str(info.get('python_module', '')).lower()
                                 or 'photoshoot' in str(info.get('category', '')).lower())
                if is_photoshoot and not hidden.keys() <= declared:
                    raise ValueError
                if declared and (not is_photoshoot or not declared <= hidden.keys()):
                    raise ValueError
                if set(required) - node['inputs'].keys():
                    raise ValueError
                for key, value in node['inputs'].items():
                    kind = allowed[key][0]
                    if isinstance(value, list):
                        source, index = value
                        actual = nodes[self.prompt[source]['class_type']]['output'][index]
                        if actual != '*' and kind != '*' and actual != kind:
                            raise ValueError
                    elif isinstance(kind, list) and value not in kind:
                        raise ValueError
                    elif kind == 'INT' and type(value) is not int:
                        raise ValueError
                    elif kind == 'FLOAT' and type(value) not in (int, float):
                        raise ValueError
                    elif kind == 'STRING' and not isinstance(value, str):
                        raise ValueError
                    elif kind == 'BOOLEAN' and type(value) is not bool:
                        raise ValueError
        except (AttributeError, IndexError, KeyError, TypeError, ValueError):
            raise AppError('renderer_incompatible') from None

    def render(self, description, job_id):
        graph = deepcopy(self.prompt)
        node_id, key, template = self.binding(self.scene_input)
        graph[node_id]['inputs'][key] = template.replace(SCENE_MARKER, description)
        graph[self.output_node]['inputs']['filename_prefix'] = f'incanta/{job_id}'
        return graph
