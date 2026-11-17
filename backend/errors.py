"""Public error categories; never include raw exceptions, paths or dialogue."""
ERRORS = {
    'invalid_configuration': (503, 'Check the local runtime settings, then restart.'),
    'model_unavailable': (503, 'Connect or configure the local model, then try again.'),
    'personality_unavailable': (503, 'Configure a readable character JSON object, then try again.'),
    'storage_unavailable': (503, 'Check access to the local history folder, then try again.'),
    'history_unreadable': (500, 'The existing history could not be read. Preserve it for repair.'),
    'persistence_failed': (500, 'The turn could not be saved. Previous history was preserved.'),
    'generation_failed': (500, 'The local model could not complete this turn. Try again.'),
    'conversation_busy': (409, 'A reply is already being processed. Wait and try again.'),
    'invalid_request': (400, 'Send a nonempty text message.'),
    'unsupported_media_type': (415, 'Send the request as JSON.'),
    'input_too_large': (413, 'Keep the message within 8,000 characters and the request within 64 KiB.'),
}


class AppError(Exception):
    def __init__(self, code):
        self.code = code
        self.status, self.message = ERRORS[code]
        super().__init__(self.message)
