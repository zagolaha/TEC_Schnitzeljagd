from flask import *
import datetime
import json
import time
import sqlite3
import html

app = Flask(__name__)
app.secret_key = "cf7afb909ccf7fc842f44eaf70bfbc9360fa80832e3f9b457586a74b46d0e35f"
DATABASE = 'static/leaderboard.db'

json_questions = json.load(open("static/questions.json", encoding='utf-8'))
quiz_length = len(json_questions["questions"])

# functions
def getStringScore():
    global quiz_length
    if 'counter' in session:
        return str((session['counter']/quiz_length)*100) + "%"

def getStringOverallScore():
    # global quiz_length
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
        user_time = int(json_questions["time"]) * 60
        time_diff = time.time() - session['start_time']
        if time_diff >= user_time:
            return True 
    return False    

def getTimeFormat(seconds):
        minutes = round(seconds // 60)
        seconds %= 60
        seconds = round(seconds)
        if minutes < 10:
            minutes = "0" + str(minutes)
        if seconds < 10:
            seconds = "0" + str(seconds)
        if seconds == 60:
            minutes += 1
            seconds = 0
        return str(minutes) + ":" + str(seconds)
        

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def insertUser(name, time, score):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO leaderboard(username, time, score) VALUES (?, ?, ?)"
        data = (name, time, score)
        cursor.execute(sql, data)
        conn.commit()
        cursor.close()
        conn.close()
    except sqlite3.Error as error:
        return False

def getLeaderboard():
    conn = get_db_connection()
    leaderboard = conn.execute('SELECT * FROM leaderboard ORDER BY score DESC').fetchall()
    conn.close()
    return leaderboard

def getUserID():
    if 'username' in session:
        conn = get_db_connection()
        user_id = conn.execute('SELECT ID FROM leaderboard WHERE username = ?', (session['username'],)).fetchone()
        conn.close()
        return user_id['ID']
    else:
        return None

def UserAlreadyExist(username):
    if(len(username) >= 2):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM leaderboard WHERE username = ?', (username,)).fetchall()
        conn.close()
        if len(user) > 0:
            return "Benutzername bereits vergeben"
        else:
            return "Benutzername ist frei"
    else:
        return "Benutzername muss min. 2 Zeichen haben"
    
def calculateScore(seconds):
    return round((json_questions["time"] * 60 - seconds) * session['counter'])
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
    max_min = json_questions["time"]
    return render_template("index.html", max_min = max_min)

# Verarbeite antwort
@app.route("/handle_answer", methods=['POST'])
def handle_data():
    answer = int(request.form.get("answer"))
    qr_id = request.form.get("qr-id")
    # right answer check
    if answer == 1:
        session['counter'] += 1
    addID(qr_id)
    # final answer check
    if checkEnd() or checkTime():
        return redirect(url_for("end"))
    else:
        return render_template("zwischenBildschirm.html")

# for debugging purposes, remove on deployment
@app.route("/zwischenBildschirm")
def zwischen_bildschirm():
    return render_template("zwischenBildschirm.html", score=getStringOverallScore())

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
   session.clear()
   return redirect(url_for('index'))

# Zeiterfassung start
@app.route('/start',methods=['POST'])
def start():
    if 'start_time' not in session:
       session['start_time'] = time.time()
    if 'username' not in session:
       session['username'] = html.escape(request.form.get("username"))
    return redirect("/zwischenBildschirm")

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
        score = calculateScore(seconds)
        insertUser(session['username'], getTimeFormat(seconds), score)
        return render_template("end.html", right_answers=getStringOverallScore(), time=getTimeFormat(seconds), score=score)
    else:
        return redirect(url_for("error", error="Bitte beende erst das Quiz"))
    
@app.route("/abort")
def abort():
    # copy & pasted from above, change both occurences if needed
    seconds = time.time() - session['start_time']
    score = calculateScore(seconds)
    insertUser(session['username'], getTimeFormat(seconds), calculateScore(seconds))
    return render_template("end.html", right_answers=getStringOverallScore(), time=getTimeFormat(seconds), score=score)

# Leaderboard
@app.route("/leaderboard")
def leaderboard():
    user_id = getUserID()
    leaderboard = getLeaderboard()
    if user_id == None:
        return redirect(url_for("error", error="Benutzername nicht gefunden"))
    return render_template("leaderboard.html", dataset=leaderboard, user_id = user_id)

# validate user
@app.route("/validUser", methods=['POST'])
def validUser():
    username = request.get_json().get('username', '')
    is_taken = UserAlreadyExist(username)
    return jsonify({'taken': is_taken})

@app.route('/delete/<user_name>', methods=['DELETE'])
def delete(user_name):
    try:
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        command = f"DELETE FROM leaderboard WHERE username = \"{user_name}\""
        print(command)
        cur.execute(command)
        cur.close()
        con.commit()
        con.close()
        return "Success\r\n"
    except sqlite3.Error as error:
        return "Error\r\n"

if __name__ == '__main__':
    context = ('localhost.pem', 'localhost-key.pem')
    app.run(host='0.0.0.0', debug=True, ssl_context=context)
