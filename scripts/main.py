from flask import Flask, render_template, request, redirect
import db_actions

# 
app = Flask(__name__, template_folder='../templates')

db_actions.init_db()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        selected = request.form.getlist("options")

        return redirect('main_admin')
    return render_template('register_page.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

    return render_template('login_page.html')

@app.route("/main_admin", methods=["POST", "GET"])
def main_admin():
    return render_template("main_page_admin.html")



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=50)
