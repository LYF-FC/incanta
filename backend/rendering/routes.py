"""Visual controls inherit the conversation API's loopback, CSRF and cache policy."""
from flask import Response, jsonify, request

from backend.errors import AppError


def register_visual_routes(app, jobs):
    def body():
        value = request.get_json()
        if not isinstance(value, dict):
            raise AppError('invalid_request')
        return value

    @app.get('/api/visuals/status')
    def visuals_status():
        return jsonify(jobs.status(request.args.get('configuration')))

    @app.put('/api/conversations/<cid>/visuals')
    def visual_identity(cid):
        return jsonify(jobs.set_identity(cid, body()))

    @app.get('/api/conversations/<cid>/images')
    def list_images(cid):
        try:
            cursor = int(request.args['cursor']) if 'cursor' in request.args else None
            limit = int(request.args.get('limit', '50'))
        except ValueError:
            raise AppError('invalid_request') from None
        return jsonify(jobs.list(cid, cursor, limit))

    @app.post('/api/conversations/<cid>/images')
    def submit_image(cid):
        return jsonify(jobs.enqueue(cid, body())), 202

    @app.patch('/api/conversations/<cid>/scene-policy')
    def scene_policy(cid):
        return jsonify(jobs.set_policy(cid, body()))

    @app.get('/api/image-jobs/<jid>')
    def image_job(jid):
        return jsonify(jobs.get(jid))

    @app.post('/api/image-jobs/<jid>/cancel')
    def cancel_image(jid):
        body()
        result = jobs.cancel(jid)
        return jsonify(result), 202 if result['state'] in {'cancel_requested', 'uncertain', 'submitting'} else 200

    @app.post('/api/image-jobs/<jid>/resolve')
    def resolve_image(jid):
        if body().get('confirm_missing') is not True:
            raise AppError('invalid_request')
        return jsonify(jobs.resolve(jid))

    @app.post('/api/visuals/recover-handoff')
    def recover_handoff():
        if body().get('confirm_idle') is not True:
            raise AppError('invalid_request')
        jobs.recover_handoff()
        return jsonify(recovered=True)

    @app.post('/api/conversations/<cid>/portrait')
    def approve_portrait(cid):
        return jsonify(jobs.portrait(cid, body()))

    @app.get('/api/assets/<aid>')
    def visual_asset(aid):
        data, mime = jobs.asset(aid)
        return Response(data, mimetype=mime, headers={'Cross-Origin-Resource-Policy': 'same-origin'})
