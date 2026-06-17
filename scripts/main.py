from flask import Flask, render_template, request
import db_actions as db_actions

app = Flask(__name__, template_folder='../templates')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        selected = request.form.getlist("options")

        print(username, password, selected)
    return render_template('register_page.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

    return render_template('login_page.html')



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=50)
