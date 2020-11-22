from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
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