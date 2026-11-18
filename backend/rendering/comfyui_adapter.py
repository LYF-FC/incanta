"""Bounded loopback HTTP for a dedicated ComfyUI instance."""
from hashlib import sha256
from http.client import HTTPConnection, HTTPException
import json
import re
from time import monotonic
from urllib.parse import quote, urlencode, urlsplit

from backend.conversation_store import identifier
from backend.errors import AppError
from backend.rendering.workflow import relative_parts

MAX_IMAGE = 20 * 1024 * 1024
MAX_JSON = 8 * 1024 * 1024
BARRIER = {
    '1': {'class_type': 'EmptyImage', 'inputs': {'width': 16, 'height': 16, 'batch_size': 1, 'color': 0}},
    '2': {'class_type': 'PreviewImage', 'inputs': {'images': ['1', 0]}},
}


def output_descriptor(data):
    try:
        filename = data['filename']
        if (data['type'] != 'output' or len(relative_parts(filename)) != 1
                or len(relative_parts(data['subfolder'])) != 1):
            raise ValueError
        return {'filename': filename, 'subfolder': data['subfolder'], 'type': 'output'}
    except (KeyError, TypeError, ValueError):
        raise AppError('asset_invalid') from None


class ComfyUI:
    def __init__(self, url, dedicated=False, *, timeout=3):
        try:
            parts = urlsplit(url)
            if (parts.scheme != 'http' or parts.hostname not in {'localhost', '127.0.0.1', '::1'}
                    or parts.path not in {'', '/'} or parts.query or parts.fragment
                    or parts.username is not None or parts.password is not None or not parts.port):
                raise ValueError
            self.host = '127.0.0.1' if parts.hostname == 'localhost' else parts.hostname
            self.port = parts.port
        except (AttributeError, TypeError, ValueError):
            raise AppError('renderer_incompatible') from None
        self.key = sha256(f'{self.host}:{self.port}'.encode()).hexdigest()
        self.dedicated = dedicated
        self.timeout = timeout

    def _request(self, method, route, body=None, *, limit=MAX_JSON):
        connection = HTTPConnection(self.host, self.port, timeout=self.timeout)
        try:
            payload = None if body is None else json.dumps(body, allow_nan=False).encode()
            connection.request(method, route, payload, {'Content-Type': 'application/json'})
            response = connection.getresponse()
            if method == 'POST' and route == '/prompt' and response.status == 400:
                raise AppError('render_rejected')
            if response.status != 200:
                raise AppError('renderer_unavailable')
            if response.length is not None and response.length > limit:
                raise AppError('asset_invalid' if limit == MAX_IMAGE else 'renderer_incompatible')
            data = bytearray()
            deadline = monotonic() + self.timeout
            while len(data) <= limit:
                if monotonic() >= deadline:
                    raise AppError('renderer_unavailable')
                chunk = response.read1(min(64 * 1024, limit + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            if len(data) > limit:
                raise AppError('asset_invalid' if limit == MAX_IMAGE else 'renderer_incompatible')
            if response.length not in {0, None}:
                raise AppError('renderer_unavailable')
            return bytes(data), response.headers.get_content_type()
        except (OSError, HTTPException):
            raise AppError('renderer_unavailable') from None
        finally:
            connection.close()

    def _get(self, route):
        try:
            value = json.loads(self._request('GET', route)[0])
            if isinstance(value, dict):
                return value
        except (ValueError, RecursionError):
            pass
        raise AppError('renderer_incompatible')

    def inspect_capabilities(self):
        stats = self._get('/system_stats')
        system = stats.get('system')
        version = system.get('comfyui_version') if isinstance(system, dict) else None
        if not self.dedicated or not isinstance(version, str):
            raise AppError('renderer_incompatible')
        return version

    def validate_workflow(self, workflow):
        if self.inspect_capabilities() != workflow.comfyui_version:
            raise AppError('renderer_incompatible')
        nodes = {}
        for node in workflow.prompt.values():
            name = node['class_type']
            if name not in nodes:
                nodes.update(self._get('/object_info/' + quote(name, safe='')))
        workflow.validate_nodes(nodes)
        for name in ('EmptyImage', 'PreviewImage'):
            if name not in self._get('/object_info/' + name):
                raise AppError('renderer_incompatible')

    def submit(self, prompt, job_id):
        identifier(job_id)
        try:
            result = self._request('POST', '/prompt', {
                'prompt': prompt, 'prompt_id': job_id, 'client_id': job_id,
                'extra_data': {'incanta_job': job_id},
            })
            return identifier(json.loads(result[0])['prompt_id'])
        except AppError as error:
            if error.code == 'render_rejected':
                raise
        except (TypeError, KeyError, ValueError, RecursionError):
            pass
        raise AppError('render_uncertain')

    def queue(self):
        queue = self._get('/queue')
        for name in ('queue_running', 'queue_pending'):
            entries = queue.get(name)
            if (not isinstance(entries, list) or any(not isinstance(entry, list)
                    or len(entry) < 4 for entry in entries)):
                raise AppError('renderer_incompatible')
        return queue

    @staticmethod
    def _owned(entry, job):
        return (isinstance(entry, list) and len(entry) >= 4
                and isinstance(entry[3], dict) and entry[3].get('incanta_job') == job)

    def idle(self):
        queue = self.queue()
        return not (queue['queue_running'] or queue['queue_pending'])

    def locate(self, job):
        identifier(job)
        direct = self._get('/history/' + job)
        item = direct.get(job)
        if isinstance(item, dict) and self._owned(item.get('prompt'), job):
            return job
        queue = self.queue()
        matches = [entry[1] for entry in queue['queue_running'] + queue['queue_pending']
                   if self._owned(entry, job)]
        if not matches:
            recent = self._get('/history?max_items=20')
            matches = [handle for handle, entry in recent.items()
                       if isinstance(entry, dict) and self._owned(entry.get('prompt'), job)]
        return identifier(matches[0]) if len(matches) == 1 else None

    def poll(self, handle, job, output_node):
        identifier(handle)
        record = self._get('/history/' + handle).get(handle)
        if isinstance(record, dict) and self._owned(record.get('prompt'), job):
            status = record.get('status')
            if not isinstance(status, dict):
                raise AppError('renderer_incompatible')
            if status.get('status_str') == 'error':
                return 'failed', None
            if status.get('status_str') != 'success' or status.get('completed') is not True:
                return 'missing', None
            if output_node is None:
                return 'succeeded', None
            outputs = record.get('outputs')
            if not isinstance(outputs, dict) or not isinstance(outputs.get(output_node), dict):
                raise AppError('asset_invalid')
            images = outputs[output_node].get('images')
            if not isinstance(images, list) or len(images) != 1:
                raise AppError('asset_invalid')
            output = output_descriptor(images[0])
            if output['subfolder'] != 'incanta' or not re.fullmatch(re.escape(job) + r'_[0-9]+_?\.png', output['filename']):
                raise AppError('asset_invalid')
            return 'succeeded', output
        queue = self.queue()
        for endpoint, state in (('queue_running', 'running'), ('queue_pending', 'queued')):
            if any(self._owned(entry, job) and entry[1] == handle for entry in queue[endpoint]):
                return state, None
        # The worker can move the job from the queue to history between reads.
        if record is None and self._get('/history/' + handle).get(handle) is not None:
            return 'running', None
        return 'missing', None

    def cancel_owned(self, handle, job):
        identifier(handle)
        pending = self.queue()['queue_pending']
        if not any(self._owned(entry, job) and entry[1] == handle for entry in pending):
            return False
        self._request('POST', '/queue', {'delete': [handle]})
        return self.poll(handle, job, None)[0] == 'missing'

    def release_owned_resources(self):
        if not self.dedicated or not self.idle():
            raise AppError('render_handoff')
        self._request('POST', '/free', {'unload_models': True, 'free_memory': True})

    def fetch(self, descriptor):
        return self._request('GET', '/view?' + urlencode(output_descriptor(descriptor)), limit=MAX_IMAGE)
