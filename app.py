import sqlite3
from flask import Flask, render_template, request

db = sqlite3.connect('database.db', check_same_thread=False)

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    workers_cur = db.cursor()
    workers_cur.execute("SELECT * from workers")
    workers = workers_cur.fetchall()
    if request.method == "POST":
        worker1 = request.form.get("worker1")
        # db.execute("INSERT INTO transactions (type, userid, share, qty, price) VALUES (?,?,?,?,?)", ("buy", int(session.get("user_id")), share["symbol"], int(request.form.get("shares")), price))
        return render_template('index.html', page='home', worker1 = worker1, workers = workers)
    return render_template('index.html', page='home', workers = workers)

@app.route('/workers', methods=["GET", "POST"])
def workers():
    cur = db.cursor()
    cur.execute("SELECT * from workers")
    workers = cur.fetchall()
    if request.method == "POST":
        if request.form.get("btAction") == "del":
            idNumber = request.form.get("idNumber")
            cur.execute("delete from workers where id=?", (idNumber))
            db.commit()
            formname = "worker deleted!"
            cur.execute("SELECT * from workers")
            workers = cur.fetchall()
            idNumber = ""
            return render_template('workers.html', page='workers', workers = workers, formname = formname)
        
        elif request.form.get("btAction") == "alt":
            formname = "update"

        elif request.form.get("btAction") == "add":
            name = request.form.get("name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            if name == "":
                formname = "insert a name"
                return render_template('workers.html', page='workers', workers = workers, formname = formname)
            elif email == "":
                formname = "insert an email"
                return render_template('workers.html', page='workers', workers = workers, formname = formname)
            elif phone == "":
                formname = "insert a phone number"
                return render_template('workers.html', page='workers', workers = workers, formname = formname)
            else:
                for row in workers:
                    if row[2] == email:
                        formname = "Email already exist"
                        return render_template('workers.html', page='workers', workers = workers, formname = formname)
                    if row[1] == name:
                        formname = "Name already exist"
                        return render_template('workers.html', page='workers', workers = workers, formname = formname)
                    if row[3] == phone:
                        formname = "phone number already exist"
                        return render_template('workers.html', page='workers', workers = workers, formname = formname)

                formname = "new worker added!"
                cur.execute("INSERT INTO workers (name, email, phone) VALUES (?,?,?)", (name, email, phone))
                db.commit()
                cur = db.cursor()
                cur.execute("SELECT * from workers")
                workers = cur.fetchall()
                return render_template('workers.html', page='workers', workers = workers, formname = formname)

            formname = "Add"
        return render_template('workers.html', page='workers', workers = workers, formname = formname)

    formname = "nada"
    return render_template('workers.html', page='workers', workers = workers, formname = formname)

@app.route('/cars')
def cars():
    return render_template('cars.html', page='cars')

@app.route('/history')
def history():
    return render_template('history.html', page='history')