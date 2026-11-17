"""Loopback-only Flask entry point; asset and model access happens on requests."""
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from backend.config import ROOT, Settings
from backend.chat_engine import ChatEngine
from backend.errors import AppError


def create_app(settings=None, inference=None, memory=None, rng=None, legacy=False):
    settings = settings if settings is not None else Settings.from_env()
    app = Flask(__name__, static_url_path='', static_folder=str(ROOT/'frontend'),
                template_folder=str(ROOT/'frontend'))
    app.config.update(MAX_CONTENT_LENGTH=64*1024, DEBUG=False,
                      TRUSTED_HOSTS=['localhost', '127.0.0.1', '[::1]'])
    if legacy:
        engine = ChatEngine(settings, inference=inference, memory=memory, rng=rng)
    else:
        from backend.conversation_service import ConversationService
        engine = ConversationService(settings, inference=inference, rng=rng)
    app.extensions['incanta'] = engine

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/api/status')
    def status():
        return jsonify(engine.status())

    @app.post('/api/chat')
    def chat():
        if not legacy:
            raise AppError('conversation_required')
        if not request.is_json:
            raise AppError('unsupported_media_type')
        data = request.get_json()
        if not isinstance(data, dict):
            raise AppError('invalid_request')
        return jsonify(engine.process(data.get('message')))

    @app.errorhandler(AppError)
    def controlled_error(error):
        return jsonify(error={'code':error.code, 'message':error.message}), error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        categories = {400:'invalid_request', 413:'input_too_large', 415:'unsupported_media_type'}
        if error.code in categories:
            return controlled_error(AppError(categories[error.code]))
        return jsonify(error={'code':'http_error', 'message':'The request could not be completed.'}), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        # Avoid Flask's default traceback logging of raw content/asset paths.
        return controlled_error(AppError('generation_failed'))

    if not legacy:
        from backend.conversation_routes import register_routes
        register_routes(app, engine)
    return app


app = create_app()

if __name__ == '__main__':
    settings = app.extensions['incanta'].settings
    if not settings.valid:
        raise SystemExit('Invalid local settings. Check the documented configuration.')
    app.run(host=settings.host, port=settings.port, debug=False, use_reloader=False)
