from __future__ import absolute_import

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

#
# configuration
# -----------------------------------------------------------------------------

DEBUG = True
DATABASE_URL = 'postgresql://futbolito:ttaallppoorr@/futbolito'
SECRET_KEY = 'A0Zr98j/3yXsdr R~XHXFG!jmN]ASSR/,?RT'
SQLALCHEMY_DATABASE_URI = DATABASE_URL

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
db  = SQLAlchemy(app)


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
