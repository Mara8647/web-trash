from flask import Flask, render_template, request, redirect, session
import transliterate
import random
import string
from db_actions import init_db, get_user, add_user

app = Flask(__name__, template_folder='../templates')
app.secret_key = "qHg3OJ9GKmsfLr"

def create_login(name):
    transliterated = transliterate.translit(name, 'ru', reversed=True)
    last_name, first_name, middle_name = transliterated.lower().split()
    
    login = first_name[0] + '.' + last_name

    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    return temp_password


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        role = request.form.get("role")

        passsword = create_login(name)
        
        add_user(name, passsword, role)

    return render_template('register_page.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        session['role'] = get_user(username, password)

    return render_template('login_page.html')

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=50)
