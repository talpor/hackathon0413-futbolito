from __future__ import absolute_import

import os

from flask import Flask, render_template

from app.models import db

#
# configuration
# -----------------------------------------------------------------------------

DEBUG = True
DATABASE_URL = 'postgresql://futbolito:ttaallppoorr@/futbolito'
SECRET_KEY = 'A0Zr98j/3yXsdr R~XHXFG!jmN]ASSR/,?RT'
SQLALCHEMY_DATABASE_URI = DATABASE_URL

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '../templates')

app = Flask(__name__, template_folder=template_dir)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
db.init_app(app)


#
# views
# -----------------------------------------------------------------------------
@app.route('/')
def home(room_id=None):
    return render_template('index.html')

#
# browser API
# -----------------------------------------------------------------------------


#
# RaspberryPy API
# -----------------------------------------------------------------------------