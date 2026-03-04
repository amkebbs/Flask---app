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
<p>Your account is secure now.</p>
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
            session["user"] = user.username
            return redirect("/dashboard")
    return render_template_string(login_page)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template_string(dashboard_page, user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

app.run(host="0.0.0.0", port=5000)