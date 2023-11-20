from flask import Flask, render_template, request, session, redirect, url_for, Response, g
import datetime
import json
import time
import sqlite3
import html

app = Flask(__name__)
app.secret_key = "cf7afb909ccf7fc842f44eaf70bfbc9360fa80832e3f9b457586a74b46d0e35f"
DATABASE = 'static/leaderboard.db'

# styling components
json_questions = json.load(open("static/questions.json", encoding='utf-8'))
quiz_length = len(json_questions["questions"])

# functions
def getStringScore():
    global quiz_length
    if 'counter' in session:
        return str((session['counter']/quiz_length)*100) + "%"

def getStringOverallScore():
    global quiz_length
    if 'counter' in session:
        return str(session['counter']) + "/" + str(quiz_length)

def checkIDs(qr_id):
     if 'answer_ids' in session:
        return qr_id in list(filter(None, session['answer_ids'].split('/')))
    
def checkEnd():
    return len(list(filter(None, session['answer_ids'].split('/')))) == quiz_length

def addID(qr_id):
    if 'answer_ids' in session:
        session['answer_ids'] += qr_id+"/"

def checkTime():
    if 'start_time' in session:
        user_time = int(json_questions["time"][0])*60 + int(json_questions["time"][1])
        if round(time.time() - session['start_time']) >= round(user_time):
            return True 
    return False     
        

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
# functions

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Startseite
@app.route("/")
def index():
    if 'counter' not in session:
        session['counter'] = 0
    if 'answer_ids' not in session:
        session['answer_ids'] = ""
    max_min = json_questions["time"][0]
    max_sec = json_questions["time"][1]
    return render_template("index.html", max_min = max_min, max_sec = max_sec)

# Verarbeite antwort
@app.route("/handle_answer", methods=['POST']) # rename data to answer
def handle_data():
    answer = int(request.form.get("answer"))
    qr_id = request.form.get("qr-id")
    # right answer check
    if answer == 1:
        session['counter'] += 1
    addID(qr_id)
    # final answer check
    if checkEnd():
        return redirect(url_for("end"))
    else:
        return redirect(url_for("scan"))
    # verarbeite antwort hier

# Scanseite
@app.route("/scan")
def scan():
    return render_template("scan.html")

# Frageseite
@app.route("/question",methods=['POST'])
def question():
    try:
        qr_id = int(request.form.get("qr-value"))
    except:
        return redirect(url_for("error", error="Dieser QR-Code ist falsch"))
    if checkIDs(str(qr_id)):
        return redirect(url_for("error", error="Dieser Code wurde bereits abgescannt"))
    json_values = json_questions["questions"][qr_id]
    return render_template("question.html", qr_id = qr_id, max_questions = quiz_length, 
                           progress=getStringScore(), json=json_values, score = getStringOverallScore())

# clear session (remove when needed)
@app.route('/resetSession')
def resetSession():
   session.pop('counter', None)
   session.pop('answer_ids', None)
   session.pop('start_time', None)
   session.pop("username", None)
   return redirect(url_for('index'))

# Zeiterfassung start
@app.route('/start',methods=['POST'])
def start():
    if 'start_time' not in session:
       session['start_time'] = time.time()
    if 'username' not in session:
       session['username'] = html.escape(request.form.get("username"))
    return redirect(url_for('scan'))

# Hinweisseite
@app.route("/error")
def error():
    reason = request.args['error']
    return render_template("error.html", error = reason)

# Endseite
@app.route("/end")
def end():
    if checkEnd() or checkTime():
        seconds = time.time() - session['start_time']
        minutes = round(seconds // 60)
        seconds %= 60
        seconds = round(seconds)
        if minutes < 10:
            minutes = "0" + str(minutes)
        if seconds < 10:
            seconds = "0" + str(seconds)
        ende = str(minutes) + ":" + str(seconds)
        return render_template("end.html", score=getStringOverallScore(),time=ende)
    else:
        return redirect(url_for("error", error="Bitte beende erst das Quiz"))

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM leaderboard ORDER BY score DESC').fetchall()
    user_id = conn.execute('SELECT ID FROM leaderboard WHERE username = ?', (session['username'],)).fetchone()
    if user_id == None:
        return redirect(url_for("error", error="Benutzername nicht gefunden"))
    conn.close()
    return render_template("leaderboard.html", data=posts, user_id = user_id['ID'])

if __name__ == '__main__':
    context = ('localhost.pem', 'localhost-key.pem')
    app.run(host='0.0.0.0', debug=True, ssl_context=context)
    # TODO: Adhoc certificates are invalid due to the missing CA signature.
    # To resolve this, a certificate with a domain name is needed.