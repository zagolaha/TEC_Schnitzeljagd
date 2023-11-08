from flask import Flask, render_template, request, session, redirect, url_for, Response
import json
import time

app = Flask(__name__)
app.secret_key = "cf7afb909ccf7fc842f44eaf70bfbc9360fa80832e3f9b457586a74b46d0e35f"
# styling components
btn_style = "shadow-lg text-xl md:text-2xl font-semibold text-center rounded-lg w-10/12 bg-Lightgray h-14 transition-all ease-in duration-500"
json_questions = json.load(open("static/questions.json"))
quiz_length = len(json_questions["questions"])

def getStringScore():
    global quiz_length
    if 'counter' in session:
        return str((session['counter']/quiz_length)*100) + "%"

def checkIDs(qr_id):
     if 'answer_ids' in session:
        return qr_id in list(filter(None, session['answer_ids'].split('/')))
    
def checkEnd():
    return len(list(filter(None, session['answer_ids'].split('/')))) == quiz_length

def addID(qr_id):
    if 'answer_ids' in session:
        session['answer_ids'] += qr_id+"/"

# Startseite
@app.route("/")
def index():
    if 'counter' not in session:
        session['counter'] = 0
    if 'answer_ids' not in session:
        session['answer_ids'] = ""
    return render_template("index.html")

# Verarbeite antwort
@app.route("/handle_answer", methods=['POST']) # rename data to answer
def handle_data():
    answer = int(request.form.get("answer"))
    qr_id = request.form.get("qr-id")
    if answer == 1:
        session['counter'] += 1
    addID(qr_id)
    if checkEnd():
        end_time = time.time() -session['start_time']
        end_time = round(end_time)
        return render_template("end.html", ende = str(end_time))
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
        qr_val = int(request.form.get("qr-value"))
    except:
        return redirect(url_for("error", error="Dieser QR-Code ist falsch"))
    if checkIDs(str(qr_val)):
        return redirect(url_for("error", error="Dieser Code wurde bereits abgescannt"))
    json_values = json_questions["questions"][qr_val]
    return render_template("question.html", qr_id = qr_val, btn_style=btn_style, max_questions = quiz_length, prog=getStringScore(), json=json_values)

# clear session
@app.route('/resetSession')
def logout():
   session.pop('counter', None)
   session.pop('answer_ids', None)
   session.pop('start_time', None)
   return redirect(url_for('index'))

# Zeiterfassung start
@app.route('/start',methods=['POST'])
def start():
   if 'start_time' not in session:
       session['start_time'] = time.time()
   return redirect(url_for('scan'))

# Hinweisseite
@app.route("/error")
def error():
    reason = request.args['error']
    return render_template("error.html", error = reason)

# Endseite
@app.route("/end")
def end():
    end_time = time.time() - session['start_time'];
    return render_template("end.html", ende = str(end_time))



if __name__ == '__main__':
   app.run(host='0.0.0.0', debug = True,ssl_context='adhoc') # Use adhoc SSL to serve over HTTPS