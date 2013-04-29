from __future__ import absolute_import

import json, redis
from datetime import datetime

from socketio.namespace import BaseNamespace

from .models import Game, Goal, Next, db


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

    def publish_to_room(self, event_name, **kwargs):
        """Handles the redis connection to publish a message to our room
        channel.
        """
        pkt = json.dumps({
            'event_name': event_name,
            'args': kwargs
        })
        r = redis.StrictRedis()
        r.publish('futbolito', pkt)

    #
    # Event Listeners
    # -------------------------------------------------------------------------
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

    # From raspberrypi buttons
    # ------------------------
    def on_goal(self, team, position, own=False):
        """Updates the board according to the given action."""
        game = db.session.query(Game).filter(Game.ended != None).first()
        if game is None:
            return
        # check if they're terminating the game
        if game.score_board['barca'] == 5 or game.score_board['madrid'] == 5:
            game.terminate()
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
        db.session.delete(Next.query.get(id))
        db.session.commit()
        self.publish_to_room('next list',
                             results=[{'id': next.id, 'text': next.text} \
                                      for next in Next.query.all()])

    def on_swype(self, team):
        game = db.session.query(Game).filter(Game.ended != None).first()
        if game is None:
            return
        game.swype(team)
        self.publish_to_room('game board', teams=game.teams)

    def on_toggle_pause(self):
        game = db.session.query(Game).filter(Game.ended != None).first()
        if game is None:
            return
        game.toggle_pause()
        self.publish_to_room('pause state', state=game.paused)

    def on_cancel(self):
        game = db.session.query(Game).filter(Game.ended != None).first()
        if game is None:
            return
        game.terminate()
        self.publish_to_room('game terminated')
