from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

with app.app_context():
    db.create_all()

signup_page = """
<h2>Signup</h2>
<form method="post">
Username: <input name="username"><br>
Password: <input name="password" type="password"><br>
<button>Signup</button>
</form>
<a href="/login">Login</a>
"""

login_page = """
<h2>Login</h2>
<form method="post">
Username: <input name="username"><br>
Password: <input name="password" type="password"><br>
<button>Login</button>
</form>
"""

dashboard_page = """
<h2>Welcome {{user}}</h2>

<form method="post">
<input name="note" placeholder="Write a note">
<button>Add</button>
</form>

<ul>
{% for n in notes %}
<li>{{n.content}}</li>
{% endfor %}
</ul>

<a href="/logout">Logout</a>
"""

@app.route("/", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        hashed = generate_password_hash(request.form["password"])
        user = User(username=request.form["username"], password=hashed)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template_string(signup_page)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user"] = user.id
            return redirect("/dashboard")
    return render_template_string(login_page)

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        note = Note(content=request.form["note"], user_id=session["user"])
        db.session.add(note)
        db.session.commit()

    notes = Note.query.filter_by(user_id=session["user"]).all()
    return render_template_string(dashboard_page, user=session["user"], notes=notes)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

app.run()
