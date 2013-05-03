import os

from app import app
from gevent import monkey; monkey.patch_all()
from socketio.server import SocketIOServer
from werkzeug.serving import run_with_reloader

@run_with_reloader
def server():
    port = int(os.environ.get('PORT', 5000))
    SocketIOServer(('0.0.0.0', port), app, policy_server=False).serve_forever()
    # app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    server()
