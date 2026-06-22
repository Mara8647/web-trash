from flask import Flask, render_template, request, redirect, session
import transliterate
import random
import string
from db import init_db, add_employee, get_user, SessionLocal, Employee
import datetime

app = Flask(__name__, template_folder='../templates')
app.secret_key = "qHg3OJ9GKmsfLr"

def create_login(name):
    transliterated = transliterate.translit(name, 'ru', reversed=True)
    last_name, first_name, _ = transliterated.lower().split()
    
    base = first_name[0] + '.' + last_name

    existing_logins = {row[0] for row in SessionLocal().query(Employee.login).all()}

    counter = 2

    base = base.strip(".-") or "user"
    login = base
    counter = 2
    while login in existing_logins:
        login = f"{base}{counter}"
        counter += 1

    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    return login, temp_password


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        salt, access = get_user(login, password)

        if access == 'admin':
            return render_template('main_admin.html')

    return render_template('index.html')

@app.route("/create_employee", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        department = request.form.get("department")
        position = request.form.get("position")
        manager = request.form.get("manager")
        start_date = request.form.get("start_date")
        email_domain = request.form.get("email_domain")
        role_id = request.form.get("role_id")
        
        login, temp_password = create_login(full_name)
        
        email = f"{login}@{email_domain}"

        start_date = start_date.split("-")
        start_date = datetime.datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))

        role = add_employee(full_name, login, department, position, manager, start_date, email, role_id)

        return render_template('employee_created.html', login=login, email=email, temp_password=temp_password, role=role)

    return render_template('create_employee.html')

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=50)
