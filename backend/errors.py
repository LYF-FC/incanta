"""Public error categories; never include raw exceptions, paths or dialogue."""
ERRORS = {
    'not_found': (404, 'This conversation or memory is unavailable.'),
    'forbidden': (403, 'Refresh Incanta and submit from its local page.'),
    'revision_conflict': (409, 'This item changed. Refresh it before editing again.'),
    'request_conflict': (409, 'This request identifier was already used for different text.'),
    'context_changed': (409, 'Settings or memories changed during the reply. Review them and retry.'),
    'context_too_large': (413, 'Shorten the message or character settings to fit the local model context.'),
    'conversation_required': (400, 'Choose or create a conversation before sending a message.'),
    'import_changed': (409, 'The selected legacy file changed. Preview it again before importing.'),
    'import_unavailable': (400, 'Choose a readable, valid legacy history in local import settings.'),
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
