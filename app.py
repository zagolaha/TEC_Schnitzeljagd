from flask import Flask, render_template, request, session, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = "cf7afb909ccf7fc842f44eaf70bfbc9360fa80832e3f9b457586a74b46d0e35f"

# styling components
answer_btn = "shadow-lg text-xl md:text-2xl font-semibold text-center rounded-lg w-10/12 bg-Lightgray h-14 transition-all ease-in duration-500"
json_questions = json.load(open("static/questions.json"))
quiz_length = len(json_questions["questions"])

def getStringScore():
    global quiz_length
    if 'counter' in session:
        return str((session['counter']/quiz_length)*100) + "%"

def checkIDs(qr_id):
     if 'answer_ids' in session:
        return qr_id in list(filter(None, session['answer_ids'].split('/')))

def addID(qr_id):
    if 'answer_ids' in session:
        session['answer_ids'] += qr_id+"/"

@app.route("/")
def index():
    if 'counter' not in session:
        session['counter'] = 0
    if 'answer_ids' not in session:
        session['answer_ids'] = ""
    return render_template("index.html")

@app.route("/handle_answer", methods=['POST']) # rename data to answer
def handle_data():
    answer = int(request.form.get("answer"))
    qr_id = request.form.get("qr-id")
    if answer == 1:
        session['counter'] += 1
    addID(qr_id)
    if len(session['answer_ids']) == (quiz_length-1)+quiz_length:
        return redirect(url_for("end"))
    return redirect(url_for("scan"))
    # verarbeite antwort hier

@app.route("/scan")
def scan():
    return render_template("scan.html")

@app.route("/question",methods=['POST'])
def question():
    try:
        qr_val = int(request.form.get("qr-value"))
    except:
        return redirect(url_for("error", error="Dieser QR-Code ist falsch"))
    if checkIDs(str(qr_val)):
        return redirect(url_for("error", error="Dieser Code wurde bereits abgescannt"))
    json_values = json_questions["questions"][qr_val]
    return render_template("question.html", qr_id = qr_val, btn_style=answer_btn, max_questions = quiz_length, prog=getStringScore(), json=json_values)

@app.route('/resetSession')
def logout():
   session.pop('counter', None)
   session.pop('answer_ids', None)
   return redirect(url_for('index'))

@app.route("/error")
def error():
    reason = request.args['error']
    return render_template("error.html", error = reason)

@app.route("/end")
def end():
    return render_template("end.html")

if __name__ == '__main__':
   app.run(ssl_context='adhoc') # Use adhoc SSL to serve over HTTPS