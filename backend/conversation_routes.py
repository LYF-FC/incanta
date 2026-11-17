"""Same-origin local conversation API; no content in cookies, errors or logs."""
import secrets
from flask import jsonify, request, session
from backend.errors import AppError
from backend.legacy_import import LegacyImporter


def register_routes(app,service):
    app.secret_key=secrets.token_bytes(32)
    app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Strict')
    importer=LegacyImporter(service.store,service.settings.import_path)
    app.extensions['incanta_importer']=importer

    @app.before_request
    def local_mutations():
        if request.path.startswith('/api/') and request.method not in {'GET','HEAD','OPTIONS'}:
            if request.path=='/api/chat':return None
            token=request.headers.get('X-CSRF-Token','')
            expected=session.get('csrf_token')
            if (request.headers.get('Origin')!=request.host_url.rstrip('/')
                    or not isinstance(expected,str) or not secrets.compare_digest(token,expected)):
                raise AppError('forbidden')
            if not request.is_json:raise AppError('unsupported_media_type')

    @app.after_request
    def local_headers(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        return response

    def body():
        value=request.get_json()
        if not isinstance(value,dict):raise AppError('invalid_request')
        return value

    @app.get('/api/bootstrap')
    def bootstrap():
        if 'csrf_token' not in session:session['csrf_token']=secrets.token_urlsafe(32)
        return jsonify(csrf_token=session['csrf_token'],legacy_import_configured=importer.path is not None)

    @app.get('/api/conversations')
    def conversations():
        return jsonify(conversations=service.store.list_conversations())

    @app.post('/api/conversations')
    def create_conversation():
        if not service.settings.valid:raise AppError('invalid_configuration')
        return jsonify(service.store.create_conversation(body())),201

    @app.get('/api/conversations/<cid>')
    def conversation(cid):
        try:
            limit=int(request.args.get('limit','50'))
            cursor=int(request.args['cursor']) if 'cursor' in request.args else None
        except ValueError:raise AppError('invalid_request') from None
        return jsonify(service.store.get_conversation(cid,limit,cursor))

    @app.patch('/api/conversations/<cid>/settings')
    def settings(cid):return jsonify(service.store.update_settings(cid,body()))

    @app.post('/api/conversations/<cid>/turns')
    def turn(cid):
        value=body()
        return jsonify(service.process(cid,value.get('message'),value.get('request_id')))

    @app.get('/api/conversations/<cid>/facts')
    def facts(cid):return jsonify(facts=service.facts.list(cid))

    @app.post('/api/conversations/<cid>/facts')
    def create_fact(cid):return jsonify(service.facts.create(cid,body())),201

    @app.patch('/api/facts/<fid>')
    def edit_fact(fid):return jsonify(service.facts.edit(fid,body()))

    @app.delete('/api/facts/<fid>')
    def delete_fact(fid):return jsonify(service.facts.edit(fid,body(),delete=True))

    @app.put('/api/facts/<fid>/grants/<cid>')
    def grant(fid,cid):return jsonify(service.facts.grant(fid,cid,body()))

    @app.delete('/api/facts/<fid>/grants/<cid>')
    def revoke(fid,cid):return jsonify(service.facts.grant(fid,cid,body(),revoke=True))

    @app.post('/api/imports/preview')
    def preview_import():return jsonify(importer.preview(body()))

    @app.post('/api/imports/confirm')
    def confirm_import():
        result,created=importer.confirm(body())
        return jsonify(result),201 if created else 200
