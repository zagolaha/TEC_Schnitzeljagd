from flask import *
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
def getProgressPercentage():
    return str(int(session['answered_questions'])/quiz_length*100) + "%"

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
        minutes = round(seconds // 60) #🙄
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
    
def calculateScore(time_taken):
    duration = json_questions["time"]
    max_score = 10000
    points_deducted_per_second = max_score // (duration * 60)
    factor = int(session['right_answers']) / quiz_length
    return round((max_score - (time_taken * points_deducted_per_second)) * factor)
# functions

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Startseite
@app.route("/")
def index():
    #if '___' not in session:
    if 'answer_ids' not in session:
        session['answer_ids'] = ""
    if 'answered_questions' not in session:
        session['answered_questions'] = "0"
    if 'right_answers' not in session:
        session['right_answers'] = "0"
    if 'start_timer' not in session:
        session['start_timer'] = 0
    max_min = json_questions["time"]
    leaderboard = getLeaderboard()
    return render_template("index.html", max_min=max_min, dataset=leaderboard, quiz_length=quiz_length, user_id=None)

# Verarbeite antwort
@app.route("/handle_answer", methods=['POST'])
def handle_data():
    answer = int(request.form.get("answer"))
    qr_id = request.form.get("qr-id")
    # right answer check
    if answer == 1:
        session['right_answers'] = str(int(session['right_answers']) + 1)
    addID(qr_id)
    return redirect("/zwischenBildschirm")

@app.route("/zwischenBildschirm")
def zwischen_bildschirm():
    return render_template("zwischenBildschirm.html", progress=getProgressPercentage(), count=session['answered_questions'], quiz_length=quiz_length)

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
        return redirect(url_for("error", error="Dieser QR-Code ist nicht bekannt :/"))
    if checkIDs(str(qr_id)):
        return redirect(url_for("error", error="Dieser Code wurde bereits abgescannt"))
    json_values = json_questions["questions"][qr_id]
    return render_template("question.html", qr_id=qr_id, quiz_length=quiz_length,
                           json=json_values)

@app.route('/resetSession')
def resetSession():
   session.clear()
   session['gay'] = 0
   return redirect("/")

# Zeiterfassung start
@app.route('/start',methods=['POST'])
def start():
    if 'start_time' not in session:
       session['start_time'] = time.time()
    if 'username' not in session:
       session['username'] = html.escape(request.form.get("username"))
    return redirect("/zwischenBildschirm")

# Hinweis-Seite
@app.route("/error")
def error():
    reason = request.args['error']
    return render_template("error.html", error = reason)

@app.route("/end")
@app.route("/abort")
def end():
    seconds = time.time() - session['start_time']
    score = calculateScore(seconds)
    insertUser(session['username'], getTimeFormat(seconds), score)
    return render_template("end.html", time=getTimeFormat(seconds), right_answers=session['right_answers'], quiz_length=quiz_length, score=score)

@app.route("/leaderboard")
def leaderboard():
    user_id = getUserID()
    leaderboard = getLeaderboard()
    if user_id == None:
        return redirect(url_for("error", error="Benutzername nicht gefunden"))
    return render_template("leaderboard.html", dataset=leaderboard, user_id = user_id)

@app.route("/validUser", methods=['POST'])
def validUser():
    username = request.get_json().get('username', '')
    is_taken = UserAlreadyExist(username)
    return jsonify({'taken': is_taken})

"""
    Below this are helper functions used by the powershell script for remote management.
"""

@app.route("/getLeaderboardAsJson")
def getLeaderboardAsJson():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM leaderboard ORDER BY score DESC")
    rows = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    data = [dict(zip(column_names, row)) for row in rows]
    cur.close()
    con.close()
    return data

@app.route('/delete/<id>', methods=['DELETE'])
def delete(id):
    try:
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        command = f"DELETE FROM leaderboard WHERE ID = \"{id}\""
        cur.execute(command)
        cur.close()
        con.commit()
        con.close()
        return jsonify(success=True)
    except:
        return jsonify(success=False)
    
@app.route("/time", methods=['GET', 'PATCH'])
def getTime():
    if request.method == 'GET':
        data = json.load(open("static/questions.json", encoding='utf-8'))
        return jsonify(int(data["time"]))
    else:
        global json_questions
        reqData = request.json
        with open("static/questions.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        data['time'] = reqData['value']
        with open("static/questions.json", 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        json_questions = data
        return "Change successfull", 200

@app.route("/frage", methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def frage():
    global json_questions
    global quiz_length
    if request.method == 'GET':
        return json_questions["questions"]
    elif request.method == 'PATCH':
        obj = request.json
        type = obj["type"]
        index = obj["index"]
        content = obj["content"]
        with open("static/questions.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        match type:
            case "question":
                try:
                    data["questions"][index]["question"] = content
                    with open("static/questions.json", 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)
                    json_questions = data
                    return jsonify(success=True)
                except:
                    return jsonify(success=False)
            case "answer":
                try:
                    num = obj["number"]
                    data["questions"][index]["answers"][num] = content
                    with open("static/questions.json", 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)
                    json_questions = data
                    return jsonify(success=True)
                except:
                    return jsonify(success=False)
            case "solution":
                try:
                    data["questions"][index]["solution"] = content
                    with open("static/questions.json", 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)
                    json_questions = data
                    return jsonify(success=True)
                except:
                    return jsonify(success=False)
    elif request.method == 'PUT':
        try:
            obj = request.json
            with open("static/questions.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
            data["questions"].append(obj)
            with open("static/questions.json", 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            quiz_length += 1
            json_questions = data
            return jsonify(success=True)
        except:
            return jsonify(success=False)
    elif request.method == 'DELETE':
        try:
            id = request.json['value']
            with open("static/questions.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
            del data["questions"][id]
            with open("static/questions.json", 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            quiz_length -= 1
            json_questions = data
            return jsonify(success=True)
        except:
            return jsonify(success=False)

if __name__ == '__main__':
    context = ('ssl.pem', 'ssl-key.pem')
    app.run(host='0.0.0.0', debug=True, ssl_context=context)