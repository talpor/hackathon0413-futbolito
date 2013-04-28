from __future__ import absolute_import

from datetime import datetime

from . import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    twitter = db.Column(db.String(80), unique=True)
    position = db.Column(db.String(20), unique=False)

    # relationships
    barca1  = db.relationship('Game', backref='barca1', lazy='dynamic')
    barca2  = db.relationship('Game', backref='barca2', lazy='dynamic')
    madrid1 = db.relationship('Game', backref='madrid1', lazy='dynamic')
    madrid2 = db.relationship('Game', backref='madrid2', lazy='dynamic')
    goal    = db.relationship('Goal', backref='player', lazy='dynamic')

    def __init__(self, name=None, position=''):
        self.name = name
        self.position = position

    def __repr__(self):
        return '<Player %r>' % (self.name)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    ended   = db.Column(db.DateTime)
    paused  = db.Column(db.Boolean, default=False)

    # players
    barca1_id  = db.Column(db.Integer, db.ForeignKey('player.id'))
    barca2_id  = db.Column(db.Integer, db.ForeignKey('player.id'))
    madrid1_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    madrid2_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    # relationships
    game = db.relationship('Goal', backref='game', lazy='dynamic')


    def __init__(self, created=None):
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<Game %s: %s>' % (self.id, self.created)

    def toggle_pause(self):
        self.paused = not self.paused


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)  # seconds after game started
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    # snapshots
    barca1_position  = db.Column(db.String(20), unique=False)
    barca2_position  = db.Column(db.String(20), unique=False)
    madrid1_position = db.Column(db.String(20), unique=False)
    madrid2_position = db.Column(db.String(20), unique=False)

    def __init__(self, player, game):
        self.player = player
        self.game   = game
        self.time   = datetime.utcnow() - self.game.created
        self.barca1_position  = game.barca1
        self.barca2_position  = game.barca1
        self.madrid1_position = game.madrid1
        self.madrid2_position = game.madrid2

    def __repr__(self):
        return '<Goal %s -> %s (%s)>' % (self.player, self.game, self.time)
