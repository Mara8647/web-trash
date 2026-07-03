from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask import session as sess
import transliterate
import random
import string
from functools import wraps
from py_scripts.db import init_db, add_employee, add_user, get_user, SessionLocal, engine, User, Employee, Role, AuditLog, Access, Resource
from py_scripts.integrations import run_demo_step, MODULE_TITLE, disable_employee
from sqlalchemy import desc, select
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

app_key = os.getenv("APP_KEY")
app = Flask(__name__, template_folder='templates')
app.secret_key = app_key
app.config['SESSION_PERMANENT'] = False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access' not in sess:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

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
    sess.clear()
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        user = get_user(login, password)
        if user == False:
            return render_template('index_wrong.html')
        else:
            access = user

        sess['access'] = access

        if access == 'admin' or access == "hr":
            with SessionLocal() as session:
                total = session.query(Employee).count()
                active = session.query(Employee).filter(Employee.status != "Уволен / отключен").count()
                ready = session.query(Employee).filter(Employee.status == "Готово").count()
                errors = session.query(Employee).filter(Employee.status == "Ошибка").count()
                employees = session.query(Employee).order_by(desc(Employee.created_at)).limit(6).all()
                logs = session.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(8).all()
                roles = session.query(Role).filter(Role.is_active == True).order_by(Role.name).all()  # noqa: E712
                return render_template(
                    "dashboard.html",
                    total=total,
                    active=active,
                    ready=ready,
                    errors=errors,
                    employees=employees,
                    logs=logs,
                    roles=roles,
                    access=access
                )
        else:
            return render_template('index_wrong.html')

    return render_template('index.html')

@app.route("/dashboard")
@login_required
def dashboard():
    with SessionLocal() as session:
        total = session.query(Employee).count()
        active = session.query(Employee).filter(Employee.status != "Уволен / отключен").filter(Employee.request_status == "done").count()
        ready = session.query(Employee).filter(Employee.status == "Готово").count()
        errors = session.query(Employee).filter(Employee.status == "Ошибка").count()
        employees = session.query(Employee).filter(Employee.request_status == "done").order_by(desc(Employee.created_at)).limit(6).all()
        logs = session.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(8).all()
        roles = session.query(Role).filter(Role.is_active == True).order_by(Role.name).all()  # noqa: E712
        return render_template(
            "dashboard.html",
            total=total,
            active=active,
            ready=ready,
            errors=errors,
            employees=employees,
            logs=logs,
            roles=roles,
            access=sess['access']
        )
    
@app.route("/users")
@login_required
def users():
    with SessionLocal() as session:
        users = session.query(User)
    return render_template('users.html', users=users)

@app.route("/create_user", methods=['POST', 'GET'])
@login_required
def create_user():
    if request.method == 'POST':
        login = request.form.get("login")
        password = request.form.get("password")
        access = request.form.get("role_id")

        add_user(login, password, access)
    return render_template('create_user.html', access=sess["access"])
    
@app.route("/integrations")
@login_required
def integrations():
    return render_template('integrations.html', access=sess["access"])

@app.route("/requests")
@login_required
def requests():
    with SessionLocal() as session:
        requests = session.query(Employee).filter(Employee.request_status == "pending")
    return render_template('requests.html', requests=requests, access=sess["access"])

@app.route('/api/handle_request', methods=['POST', 'GET'])
@login_required
def handle_request():
    action = request.args.get('action', '').strip()
    request_id = request.args.get('request_id', '').strip()

    with SessionLocal() as session:
        if action == 'accept':
            req = session.get(Employee, request_id)
            req.request_status = 'done'
        elif action == 'reject':
            req = session.get(Employee, request_id)
            session.delete(req)
        
        session.commit()
    
    return redirect(url_for("requests", requests=requests, access=sess['access']))

@app.route("/employees")
@login_required
def employees():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    with SessionLocal() as session:
        query = session.query(Employee).filter(Employee.request_status == "done").join(Role).order_by(desc(Employee.created_at))
        if q:
            like = f"%{q}%"
            query = query.filter((Employee.full_name.ilike(like)) | (Employee.login.ilike(like)) | (Employee.department.ilike(like)))
        if status:
            query = query.filter(Employee.status == status)
        items = query.all()
        return render_template("employees.html", employees=items, q=q, status=status)

@app.route("/create_employee", methods=["POST", "GET"])
@login_required
def create_employee():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        department = request.form.get("department")
        position = request.form.get("position")
        manager = request.form.get("manager")
        start_date = request.form.get("start_date")
        need_email = request.form.get("need_email") == "on"
        need_vpn = request.form.get("need_vpn") == "on"
        need_onec = request.form.get("need_onec") == "on"
        need_bitrix = request.form.get("need_bitrix") == "on"
        email_domain = request.form.get("email_domain")
        role_id = request.form.get("role_id")
        actor = sess['access']
        
        login, temp_password = create_login(full_name)
        
        email = f"{login}@{email_domain}"

        start_date = start_date.split("-")
        start_date = datetime.datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))

        role = add_employee(full_name, login, department, position, manager, start_date, need_email, need_vpn, need_onec, need_bitrix, email, role_id, actor)

        return render_template('employee_created.html', login=login, email=email, temp_password=temp_password, role=role)

    return render_template('create_employee.html')

@app.route("/employees/<int:employee_id>")
@login_required
def employee_detail(employee_id: int):
    with SessionLocal() as session:
        employee = session.get(Employee, employee_id)
        if not employee:
            flash("Сотрудник не найден.", "warning")
            return redirect(url_for("employees"))
        logs = (
            session.query(AuditLog)
            .filter(AuditLog.employee_id == employee.id)
            .order_by(desc(AuditLog.created_at))
            .all()
        )
        return render_template("employee_detail.html", employee=employee, logs=logs)

@app.post("/employees/<int:employee_id>/run/<module>")
@login_required
def employee_run_step(employee_id: int, module: str):
    try:
        run_demo_step(employee_id, module)
        flash(f"Этап '{MODULE_TITLE.get(module, module)}' выполнен в демо-режиме.", "success")
    except Exception as exc:
        flash(f"Ошибка выполнения этапа: {exc}", "danger")
    return redirect(url_for("employee_detail", employee_id=employee_id))

@app.post("/employees/<int:employee_id>/disable")
@login_required
def employee_disable(employee_id: int):
    try:
        disable_employee(employee_id)
        flash("Сотрудник отключен в MVP-режиме.", "success")
    except Exception as exc:
        flash(f"Ошибка отключения: {exc}", "danger")
    return redirect(url_for("employee_detail", employee_id=employee_id))

@app.route("/access_matrix", methods=['POST', 'GET'])
@login_required
def access_matrix():
    with engine.connect() as conn:
        with SessionLocal() as session:
            query = session.query(Access)
            q = request.args.get("q", "")
            department = request.args.get("department", "")
            position = request.args.get("position", "")
            resource_type = request.args.get("resource_type", "")
            automation = request.args.get("automation", "")

            resources = session.query(Resource).all()
            print(resources)

            if request.method == "POST":
                new_dep = request.form.get("department")
                new_pos = request.form.get("position")
                new_access = request.form.get("access_name")
                new_res_id = request.form.get("resource_id")

                stmt = select(Resource).where(Resource.id == new_res_id)
                result = conn.execute(stmt).fetchone()[1]

                new_res = result

                new_con = request.form.get("connect_responsible")
                new_discon = request.form.get("disconnect_responsible")
                new_auto = request.form.get("automation_level")
                new_term = request.form.get("due_stage")
                new_com = request.form.get("comment")

                new_rule = Access(
                    department=new_dep,
                    position=new_pos,
                    access=new_access,
                    resource=new_res,
                    connect_responsible=new_con,
                    disconnect_responsible=new_discon,
                    auto=new_auto,
                    term=new_term,
                    comment=new_com
                )

                session.add(new_rule)
                session.commit()

            if q:
                like = f"%{q}%"
                query = query.filter((Access.department.ilike(like)) | (Access.position.ilike(like)))

            if department:
                query = query.filter(Access.department == department)
            if position:
                query = query.filter(Access.position == position)
            if resource_type:
                query = query.filter(Access.resource == resource_type)
            if automation:
                query = query.filter(Access.auto == automation)
            
            items = query.all()

            return render_template("access_matrix.html", accesses=items, q=q, d=department, p=position, r=resource_type, a=automation, resources=resources)

@app.route("/roles")
@login_required
def roles():
    with SessionLocal() as session:
        items = session.query(Role).order_by(Role.name).all()
        return render_template("roles.html", roles=items)
    
@app.route("/logout")
def logout():
    sess.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=500, ssl_context=('cert.pem', 'key.pem'))
