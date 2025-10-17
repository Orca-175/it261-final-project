from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/test')
def index():
    return render_template("test.html")