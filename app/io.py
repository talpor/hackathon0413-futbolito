from __future__ import absolute_import

import json, redis
from datetime import datetime

from socketio.namespace import BaseNamespace

from .models import Game, Goal, db


class PubSubMixin(object):
    """In charge of common redis PubSub initialization. defines the gevent listener
    and the `on_subscribe` method.
    """
    def listener(self):
        r = redis.StrictRedis()
        r = r.pubsub()
        # subscribe to the user's room and to a global channel
        self.subscribe_to_channels(r)

        for msg in r.listen():
            self.process_pubsub_msg(msg)

    def on_subscribe(self, *args, **kwargs):
        self.spawn(self.listener)

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


class IONamespace(BaseNamespace, PubSubMixin):
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

        print msg
        msg = json.loads(msg['data'])
        if msg.has_key('event_name'):
            self.emit(msg['event_name'], msg['args'])

    def publish_to_room(self, event_name, **args):
        """Handles the redis connection to publish a message to our room
        channel.
        """
        pkt = json.dumps({
            'event_name': event_name,
            'args': args
        })
        r = redis.StrictRedis()
        r.publish('futbolito', pkt)

    #
    # event listeners
    def on_subscribe(self):
        """Announces every other player in the room (if any) that a new user
        has arrived.
        """
        super(IONamespace, self).on_subscribe()
        game = db.session.query(Game).filter(Game.ended != None).first()
        if game is not None:
            self.publish_to_room('game board',
                                 time=datetime.utcnow() - game.created,
                                 teams=game.teams, score=game.score_board)

    def on_goal(self, team, position, own=False):
        """Updates the board according to the given action."""
        game = db.session.query(Game).filter(Game.ended != None).first()
        if game is None:
            return
        # update stuff
        player1 = getattr(game, '%s1' % team)
        player2 = getattr(game, '%s2' % team)
        scorer = player1 if player1.position == position else player2
        team   = team if not own \
                      else [t for t in ['barca', 'madrid'] if t != team][0]
        goal   = Goal(scorer, game, team)
        db.session.add(goal)
        db.commit()
        # update boards
        self.publish_to_room('game board',
                             teams=game.teams, score=game.score_board)

    def on_undo(self):
        game = db.session.query(Game).filter(Game.ended != None).first()
        if game is None:
            return
        # update stuff
        db.session.delete(game.goals.query.order_by(Goal.time).first())
        db.session.commit()
        # update boards
        self.publish_to_room('game board',
                             teams=game.teams, score=game.score_board)
