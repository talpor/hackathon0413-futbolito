from __future__ import absolute_import

import os

from flask import Flask, Response, jsonify, render_template, request
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView

from .helpers import player_to_dict
from .io import IONamespace
from .models import db, Game, Next, Player, Goal

#
# configuration
# -----------------------------------------------------------------------------

DEBUG = True
DATABASE_URL = 'postgresql://futbolito:ttaallppoorr@/futbolito'
SECRET_KEY = 'A0Zr98j/3yXsdr R~XHXFG!jmN]ASSR/,?RT'
SEND_FILE_MAX_AGE_DEFAULT = 0
SQLALCHEMY_DATABASE_URI = DATABASE_URL

root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

app = Flask(__name__,
            static_folder=os.path.join(root_dir, 'static'),
            template_folder=os.path.join(root_dir, 'templates'))
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
db.init_app(app)


#
# admin
# -----------------------------------------------------------------------------
admin = Admin(app)
admin.add_view(ModelView(Player, db.session))
admin.add_view(ModelView(Game, db.session))
admin.add_view(ModelView(Goal, db.session))


#
# views
# -----------------------------------------------------------------------------
@app.route('/')
def home(room_id=None):
    game = db.session.query(Game).filter(Game.ended == None).first()
    return render_template('index.html', game=game)

#
# browser API
# -----------------------------------------------------------------------------
GAME_TYPES = (
    (0, 'Simple'),
    (1, 'Intercambiado')
)

@app.route('/games', methods=['POST'])
def create_game():
    """Creates a new game. Checks that there's no game currently active.

    Expects a json request with the following format::
        {
            'type': <integer>,
            'teams': {
                'barca':  {
                    'defense': <integer: player id>,
                    'forward': <integer: player id>
                },
                'madrid': {
                    'defense': <integer: player id>,
                    'forward': <integer: player id>
                }
            }
        }
    """
    if db.session.query(Game).filter(Game.ended == None).first() is not None:
        # there's a game in place
        return jsonify({
            'success': False,
            'reason': 'Currently there\'s an active game'
        })
    if not request.json.has_key('type'):
        return 'no game type', 400
    if request.json['type'] not in [gt[0] for gt in GAME_TYPES]:
        return 'invalid game type', 400
    # teams
    barca  = [request.json['teams']['barca']['defense'],
              request.json['teams']['barca']['forward']]
    madrid = [request.json['teams']['madrid']['defense'],
              request.json['teams']['madrid']['forward']]

    barca_defense = Player.query.get(barca[0])
    barca_forward = Player.query.get(barca[1])
    madrid_defense = Player.query.get(madrid[0])
    madrid_forward = Player.query.get(madrid[1])

    if barca_defense is None and barca_forward is None:
        return 'Barca team malformed', 400
    if madrid_defense is None and madrid_forward is None:
        return 'Madrid team malformed', 400

    game = Game(type=request.json['type'],
                barca1=barca_defense, barca2=barca_forward,
                madrid1=madrid_defense, madrid2=madrid_forward)
    db.session.add(game)
    db.session.commit()
    return jsonify({'success': True, 'id': game.id})

@app.route('/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    game = db.session.query(Game).filter(Game.id != game_id).first_or_404()
    if game.ended is not None:
        return {'success': False, 'reason': 'Game already terminated.'}
    if request.json.get('pause'):
        game.toggle_pause()
    if request.json.get('cancel'):
        game.terminate()
    if request.json.get('swype') and \
       request.json['swype'] in ['barca', 'madrid']:
        game.swype(team=request.json['swype'])
    return jsonify({'success': True})

@app.route('/games/types', methods=['GET'])
def game_type_list():
    return jsonify(GAME_TYPES)

@app.route('/nexts', methods=['GET'])
def next_list():
    return jsonify({
        'results': [{'id': next.id, 'text': next.text} \
                    for next in Next.query.all()]
    })

@app.route('/nexts', methods=['POST'])
def add_next():
    db.session.add(Next(text=request.json['next']))
    db.session.commit()
    return jsonify({'success': True})

@app.route('/nexts/<int:next_id>', methods=['DELETE'])
def delete_next(next_id):
    next = Next.query.get(id)
    if next is not None:
        db.session.delete(next)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/players', methods=['GET'])
def player_list():
    return jsonify({
        'results': [player_to_dict(player) for player in Player.query.all()]
    })

@app.route('/games', methods=['GET'])
def game_list():
    return jsonify({
        'results': [
            {
                'id': game.id,
                'type': game.type,
                'created': game.created,
                'ended': game.ended,
                'barca1': player_to_dict(game.barca1),
                'barca2': player_to_dict(game.barca2),
                'madrid1': player_to_dict(game.madrid1),
                'madrid2': player_to_dict(game.madrid2),
                'score_board': game.score_board
            }
            for game in Game.query.order_by(Game.created).all()
        ]
    })

#
# SocketIO
# -----------------------------------------------------------------------------
from socketio import socketio_manage

@app.route('/socket.io/<path:path>')
def socket_io(path):
    namespaces = {
        '/board': IONamespace,
    }
    try:
        _real_request = request._get_current_object()
        _real_request._app = app
        socketio_manage(request.environ, namespaces, _real_request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()
