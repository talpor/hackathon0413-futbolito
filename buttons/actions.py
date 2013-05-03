from socketIO_client import SocketIO, BaseNamespace

__all__ = ('board_players', 'goal', 'undo')

board_players = {
    11: ('barca',  'defense'),
    13: ('barca',  'forward'),
    15: ('madrid', 'defense'),
    16: ('madrid', 'forward'),
}


class BoardNamespace(BaseNamespace):
    """Base namespace for communicating with our gevent-socket.io server."""
    def on_goal_response(self, *args, **kwargs):
        print 'Recv response to goal:', args, kwargs

    def on_undo_response(self, *args, **kwargs):
        print 'Recv response to undo:', args, kwargs


ws = SocketIO('localhost', 5000).define(BoardNamespace, '/board')

def goal(button, own=False):
    """Announces a goal to the web server through a web socket.

    Arguments:
    - `button`: ioin given by clicks module.
    - `own`: was a goal on own net.
    """
    team, position = board_players[button]
    ws.emit('goal', team, position)

def undo(button):
    """Announces an undo to the web server through a web socket.

    Arguments:
    - `button`: ioin given by clicks module.
    """
    ws.emit('undo')
