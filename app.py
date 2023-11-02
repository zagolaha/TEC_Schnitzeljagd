from flask import Flask, render_template, request
import json

app = Flask(__name__)

# styling components
answer_btn = "text-5xl rounded-xl min-h-fit w-3/4 p-10 bg-Lightgray font-semibold"
answers = ["24 000", "2 453", "4 500", "7 500"]

questions = json.load(open("static/questions.json"))

@app.route("/<num>")
def index(num):
    return render_template("question.html", btn_style=answer_btn, content=answers)

@app.route("/handle_data", methods=['POST']) # rename data to answer
def handle_data():
    answer = request.form.get("buttonClicked")
    return answer
    # verarbeite antwort hier

@app.route("/scan")
def scan():
    return render_template("scan.html")

if __name__ == '__main__':
   app.run(ssl_context='adhoc') # Use adhoc SSL to serve over HTTPS