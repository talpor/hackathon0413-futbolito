from __future__ import absolute_import

from app import app
from app.models import db, Player

def init_database():
    db.app = app
    db.init_app(app)
    db.create_all()

    # add users, if they doesn't exist
    if not db.session.query(Player).filter(Player.name == 'Daniel').all():
        db.session.add(Player(name='Daniel', email='volrath@talpor.com', twitter='volrath'))
    if not db.session.query(Player).filter(Player.name == 'Pedro').all():
        db.session.add(Player(name='Pedro', email='ppinango@talpor.com', twitter='pedrojosep'))
    if not db.session.query(Player).filter(Player.name == 'Julio').all():
        db.session.add(Player(name='Julio', email='jcastillo@talpor.com', twitter='jccb'))
    if not db.session.query(Player).filter(Player.name == 'Kristoffer').all():
        db.session.add(Player(name='Kristoffer', email='kpantic@talpor.com', twitter='kpantic'))
    if not db.session.query(Player).filter(Player.name == 'Alberto').all():
        db.session.add(Player(name='Alberto', email='asanchez@talpor.com', twitter='alb3rto269'))
    if not db.session.query(Player).filter(Player.name == 'German').all():
        db.session.add(Player(name='German', email='gjaber@talpor.com', twitter=''))

    # create.
    db.session.commit()

if __name__ == '__main__':
    init_database()
