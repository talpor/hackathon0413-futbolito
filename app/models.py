from __future__ import absolute_import

from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy

from .helpers import player_to_dict

db = SQLAlchemy()


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    twitter = db.Column(db.String(80), unique=True)
    position = db.Column(db.String(20), unique=False)

    # relationships
    goal    = db.relationship('Goal', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<Player %r>' % (self.name)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type    = db.Column(db.Integer)
    created = db.Column(db.DateTime)
    ended   = db.Column(db.DateTime)
    paused  = db.Column(db.Boolean, default=False)

    # players
    barca1_id  = db.Column(db.Integer, db.ForeignKey('player.id'))
    barca2_id  = db.Column(db.Integer, db.ForeignKey('player.id'))
    madrid1_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    madrid2_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    # relationships
    goals   = db.relationship('Goal', backref='game', lazy='dynamic')
    barca1  = db.relationship('Player', backref='barca1_games',
                              foreign_keys=[barca1_id])
    barca2  = db.relationship('Player', backref='barca2_games',
                              foreign_keys=[barca2_id])
    madrid1 = db.relationship('Player', backref='madrid1_games',
                              foreign_keys=[madrid1_id])
    madrid2 = db.relationship('Player', backref='madrid2_games',
                              foreign_keys=[madrid2_id])

    def __init__(self, created=None, *args, **kwargs):
        super(Game,self).__init__(*args, **kwargs)
        self.created = created or datetime.utcnow()

    def __repr__(self):
        return '<Game %s: %s>' % (self.id, self.created)

    @property
    def score_board(self):
        """Returns the score board with the following format::
            {
                'barca': <int>,
                'madrid': <int>,
            }
        """
        return {
            'barca': 0,
            'madrid': 0
        }

    def swype(self, team):
        """Swypes position on both members of the given `team`. Team should be
        'barca' or 'madrid', otherwise an exception will be raised. After
        swyping, an broadcast notification will be sent to all the clients.
        """
        if team not in ['barca', 'madrid']:
            raise ValueError('Invalid team: %s' % team)
        member1 = getattr(self, '%s1' % team)
        member2 = getattr(self, '%s2' % team)
        member1.position = 'forward' if member1.position == 'defense' \
                                     else 'defense'
        member2.position = 'forward' if member2.position == 'defense' \
                                     else 'defense'
        db.session.add(member1)
        db.session.add(member2)
        db.session.commit()
        # notify.

    @property
    def teams(self):
        """Returns the team list for this game with every player position."""
        teams = {'barca': {}, 'madrid': {}}
        teams['barca'][self.barca1.position]   = player_to_dict(self.barca1)
        teams['barca'][self.barca2.position]   = player_to_dict(self.barca2)
        teams['madrid'][self.madrid1.position] = player_to_dict(self.madrid1)
        teams['madrid'][self.madrid2.position] = player_to_dict(self.madrid2)
        return teams

    def terminate(self):
        """Ends the game and notifies via broadcasts all the clients that a new
        game has to start.
        """
        if self.ended:
            return
        self.ended = datetime.utcnow()
        db.session.commit()

    def toggle_pause(self):
        self.paused = not self.paused
        db.session.commit()


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)  # seconds after game started
    team = db.Column(db.String(6))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    # snapshots
    barca1_position  = db.Column(db.String(20), unique=False)
    barca2_position  = db.Column(db.String(20), unique=False)
    madrid1_position = db.Column(db.String(20), unique=False)
    madrid2_position = db.Column(db.String(20), unique=False)

    def __init__(self, player, game, team):
        if team not in ['barca', 'madrid']:
            raise ValueError(
                'Attempting to add a goal to something weird: %s' % team
            )
        self.player = player
        self.game   = game
        self.team   = team
        self.time   = datetime.utcnow() - self.game.created
        self.barca1_position  = game.barca1.position
        self.barca2_position  = game.barca1.position
        self.madrid1_position = game.madrid1.position
        self.madrid2_position = game.madrid2.position

    def __repr__(self):
        return '<Goal %s -> %s (%s)>' % (self.player, self.game, self.time)


class Next(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return self.text
