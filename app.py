import sqlite3
import dateutil
import json
from dateutil import parser
from datetime import datetime
from flask import Flask, render_template, request

from linebot import LineBotApi
from linebot.models import TextSendMessage

db = sqlite3.connect('database.db', check_same_thread=False)

app = Flask(__name__)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = dateutil.parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format)

@app.route('/', methods=["GET", "POST"])
def index():
    workers_cur = db.cursor()
    workers_cur.execute("SELECT * from workers")
    workers = workers_cur.fetchall()
    cars_cur = db.cursor()
    cars_cur.execute("SELECT * from cars")
    cars = cars_cur.fetchall()
    if request.method == "POST":
        data = request.form
        date = datetime.now()

        daily_cur = db.cursor()
        daily_cur.execute("INSERT INTO daily (date, local, latitude, longitude, notes) VALUES (?,?,?,?,?)",
                         (date, data["local_name"], data["latitude"], data["longitude"], data["local_notes"]))
        db.commit()

        #get total escalation
        get_last = []
        for v in request.form.items():
            get_last.append(v)

        last = get_last[-1]
        last_key, last_valor = last
        max_plan = int(last_key[-1]) + 1
        
        esc_valor = []
        daily_id_cur = db.cursor()
        daily_id_early = daily_id_cur.execute("SELECT id FROM daily WHERE date = ?", (date,))
        
        daily_id = daily_id_early.fetchone()
        for row in daily_id:
            daily_id_fim = row
        
        # ponto = "https://goo.gl/maps/evKtd9K9397s6nGr6"
        #TEXT COMPOSITION

        lat = data["latitude"]
        lng = data["longitude"]
        
        ponto = "https://maps.google.com/?q="+lat+","+lng

        texto = "local: " + data['local_name'] + "\n" + ponto + "\n"
        texto = texto + data['local_notes'] + "\n"

        for esc in range(max_plan):
            for key, value in get_last:
                if key[-1] == str(esc):
                    esc_valor.append(value)
            esc_cur = db.cursor()
            esc_cur.execute("INSERT INTO escalation (worker1, worker2, car, notes, daily_id) VALUES (?,?,?,?,?)" ,
                           (esc_valor[0], esc_valor[1], esc_valor[2], esc_valor[3], daily_id_fim))
            db.commit()
            texto = texto + "\n" + esc_valor[0] + ", " + esc_valor[1] + " -> " + esc_valor[2] + "\nNotes: " + esc_valor[3] + "\n"
            esc_valor = []

        # LINE

        file = open('info.json', 'r')
        info = json.load(file)

        CHANNEL_ACCESS_TOKEN = info['CHANNEL_ACCESS_TOKEN']
        line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

        USER_ID = info['USER_ID']
        messages = TextSendMessage(text=f"{texto}")

        line_bot_api.push_message(USER_ID, messages)




        return render_template('index.html', page='home', data = data, workers = workers, cars = cars, date = daily_id_fim)
    return render_template('index.html', page='home', workers = workers, cars = cars)

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

@app.route('/cars', methods=["GET", "POST"])
def cars():

    cur = db.cursor()
    cur.execute("SELECT * from cars")
    cars = cur.fetchall()
    if request.method == "POST":
        if request.form.get("btAction") == "del":
            idNumber = request.form.get("idNumber")
            cur.execute("delete from cars where id=?", (idNumber))
            db.commit()
            formname = "car deleted!"
            cur.execute("SELECT * from cars")
            cars = cur.fetchall()
            idNumber = ""
            return render_template('cars.html', page='cars', cars = cars, formname = formname)
        
        elif request.form.get("btAction") == "alt":
            formname = "update"

        elif request.form.get("btAction") == "add":
            name = request.form.get("name")
            kind = request.form.get("kind")
            plate = request.form.get("plate")
            if name == "":
                formname = "insert a name"
                return render_template('cars.html', page='cars', cars = cars, formname = formname)
            elif kind == "":
                formname = "insert a kind"
                return render_template('cars.html', page='cars', cars = cars, formname = formname)
            elif plate == "":
                formname = "insert a plate number"
                return render_template('cars.html', page='cars', cars = cars, formname = formname)
            else:
                for row in cars:
                   
                    if row[1] == name:
                        formname = "Name already exist"
                        return render_template('cars.html', page='cars', cars = cars, formname = formname)
                    if row[3] == plate:
                        formname = "plate number already exist"
                        return render_template('cars.html', page='cars', cars = cars, formname = formname)

                formname = "new car added!"
                cur.execute("INSERT INTO cars (name, kind, plate) VALUES (?,?,?)", (name, kind, plate))
                db.commit()
                cur = db.cursor()
                cur.execute("SELECT * from cars")
                cars = cur.fetchall()
                return render_template('cars.html', page='cars', cars = cars, formname = formname)

            formname = "Add"
        return render_template('cars.html', page='cars', cars = cars, formname = formname)

    formname = "nada"
    return render_template('cars.html', page='cars', cars = cars, formname = formname)

@app.route('/history', methods=["GET", "POST"])
def history():
    cur = db.cursor()
    cur.execute("SELECT * from daily")
    daily = cur.fetchall()
    daily.sort(reverse=True)
    return render_template('history.html', page='history', daily = daily)

@app.route('/show', methods=["GET", "POST"])
def show():
    if request.method == "POST":
        daily_number = request.form.get("dailyNumber")
        cur = db.cursor()
        cur.execute("SELECT * from escalation WHERE daily_id = ?", (daily_number,))
        escalation = cur.fetchall()
        cur2 = db.cursor()
        cur2.execute("SELECT * from daily WHERE id = ?", (daily_number,))
        daily = cur2.fetchall()
        return render_template('show.html', page='history', escalation = escalation, daily_number = daily_number, daily = daily)