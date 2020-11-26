import sqlite3
from flask import Flask, render_template, request

db = sqlite3.connect('database.db')

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        worker1 = request.form.get("worker1")
        # db.execute("INSERT INTO transactions (type, userid, share, qty, price) VALUES (?,?,?,?,?)", ("buy", int(session.get("user_id")), share["symbol"], int(request.form.get("shares")), price))
        return render_template('index.html', page='home', worker1 = worker1)
    return render_template('index.html', page='home')

@app.route('/workers')
def workers():
    return render_template('workers.html', page='workers')

@app.route('/cars')
def cars():
    return render_template('cars.html', page='cars')

@app.route('/history')
def history():
    return render_template('history.html', page='history')