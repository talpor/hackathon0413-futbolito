from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yXsdr R~XHXFG!jmN]ASSR/,?RT'
app.debug = True

@app.route('/')
def home(room_id=None):
    return render_template('index.html')

#
# browser API
# -----------------------------------------------------------------------------


#
# RaspberryPy API
# -----------------------------------------------------------------------------


if __name__ == '__main__':
    app.run()
