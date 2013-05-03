from __future__ import absolute_import

import json, redis
from datetime import datetime

from socketio.namespace import BaseNamespace

from .models import Game, Goal, Next, db


class PubSubMixin(object):
    """In charge of common redis PubSub initialization. defines the gevent
    listener and the `on_subscribe` method.
    """
    def __init__(self, *args, **kwargs):
        request = kwargs.get('request', None)
        self.ctx = None
        if request:
            self.app = request._app
            self.ctx = self.app.request_context(request.environ)
            self.ctx.push()
            self.app.preprocess_request()
            del kwargs['request']
        super(PubSubMixin, self).__init__(*args, **kwargs)

    def listener(self):
        r = redis.StrictRedis()
        r = r.pubsub()
        # subscribe to the user's room and to a global channel
        self.subscribe_to_channels(r)

        for msg in r.listen():
            self.process_pubsub_msg(msg)

    def on_subscribe(self, *args, **kwargs):
        self.spawn(self.listener)

    def publish_to_room(self, event_name, **kwargs):
        """Handles the redis connection to publish a message to our room
        channel.
        """
        msg = {
            'event_name': event_name,
            'args': kwargs
        }
        pkt = json.dumps(msg)
        r = redis.StrictRedis()
        r.publish('futbolito', pkt)
        # also emit to myself
        self.emit('log', msg)
        self.emit(msg['event_name'], msg['args'])

    def process_pubsub_msg(self, msg):
        """This method should take care of the given message and process it.
        It should be implemented by the subclasses.
        """
        raise NotImplementedError

    def subscribe_to_channels(self, redis_connection):
        """Makes the given redis connection `r` subscribe to a list of
        channels.
        """
        raise NotImplementedError

    def disconnect(self, *args, **kwargs):
        if self.ctx:
            try:
                self.ctx.pop()
            except (IndexError, AttributeError) as e:
                self.app.logger.error('Error popping out context after '
                                      'disconnect: %s' % e)
        super(PubSubMixin, self).disconnect(*args, **kwargs)


class IONamespace(PubSubMixin, BaseNamespace):
    def subscribe_to_channels(self, r):
        """Makes the given redis connection `r` subscribe to a list of
        channels.
        """
        r.subscribe('futbolito')

    def process_pubsub_msg(self, msg):
        # debug
        self.emit('log', msg)

        if msg['type'] != 'message':
            return

        if self.app.debug:
            self.app.logger.info(msg)
        msg = json.loads(msg['data'])
        if msg.has_key('event_name'):
            self.emit(msg['event_name'], msg['args'])

    #
    # Event Listeners
    # -------------------------------------------------------------------------
    def on_subscribe(self):
        """Announces every other player in the room (if any) that a new user
        has arrived.
        """
        super(IONamespace, self).on_subscribe()
        game = db.session.query(Game).filter(Game.ended == None).first()
        if game is not None:
            self.emit('game board',
                      dict(time=(datetime.utcnow() - game.created).seconds,
                           teams=game.teams, score=game.score_board))

    # From raspberrypi buttons
    # ------------------------
    def on_goal(self, team, position, own=False):
        """Updates the board according to the given action."""
        game = db.session.query(Game).filter(Game.ended == None).first()
        if game is None:
            return
        # check if they're terminating the game
        if game.score_board['barca'] == 5 or game.score_board['madrid'] == 5:
            game.terminate()
            self.publish_to_room('game terminated')
            return
        # update stuff
        player1 = getattr(game, '%s1' % team)
        player2 = getattr(game, '%s2' % team)
        scorer  = player1 if player1.position == position else player2
        team    = team if not own \
                       else [t for t in ['barca', 'madrid'] if t != team][0]
        goal    = Goal(scorer, game, team)
        db.session.add(goal)
        db.session.commit()
        # update boards
        self.publish_to_room('game board',
                             teams=game.teams, score=game.score_board)

    def on_undo(self):
        game = db.session.query(Game).filter(Game.ended == None).first()
        if game is None:
            return
        # update stuff
        goal = game.goals.order_by(Goal.time.desc()).first()
        if goal is not None:
            db.session.delete(goal)
            db.session.commit()
        # update boards
        self.publish_to_room('game board',
                             teams=game.teams, score=game.score_board)

    # From browser's interface
    # ------------------------
    def on_add_next(self, text):
        next = Next(text=text)
        db.session.add(Next(text=text))
        db.session.commit()
        self.publish_to_room('next list',
                             results=[{'id': next.id, 'text': next.text} \
                                      for next in Next.query.all()])

    def on_delete_next(self, id):
        next = Next.query.get(id)
        if next is not None:
            db.session.delete(next)
            db.session.commit()
        self.publish_to_room('next list',
                             results=[{'id': next.id, 'text': next.text} \
                                      for next in Next.query.all()])

    def on_swype(self, team):
        game = db.session.query(Game).filter(Game.ended == None).first()
        if game is None:
            return
        game.swype(team)
        self.publish_to_room('game board', teams=game.teams)

    def on_board(self):
        game = db.session.query(Game).filter(Game.ended == None).first()
        if game is None:
            return
        self.emit('game board', teams=game.teams)

    def on_toggle_pause(self):
        game = db.session.query(Game).filter(Game.ended == None).first()
        if game is None:
            return
        game.toggle_pause()
        self.publish_to_room('pause state', state=game.paused)

    def on_cancel(self):
        game = db.session.query(Game).filter(Game.ended == None).first()
        if game is None:
            return
        game.terminate()
        self.publish_to_room('game terminated')
