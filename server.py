import os

from app import app
from gevent import monkey; monkey.patch_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if app.debug:
        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
    from socketio.server import SocketIOServer
    SocketIOServer(('0.0.0.0', port), app, policy_server=False).serve_forever()
    # app.run(host='0.0.0.0', port=port)
