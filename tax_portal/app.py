from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me"  # In production use a secure value
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tax_portal.db"
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(30), default="uploaded")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        message = "Invalid credentials"
    return render_template("login.html", message=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            if not User.query.filter_by(username=username).first():
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("login"))
            else:
                message = "Username already exists"
    return render_template("register.html", message=message)

@app.route("/dashboard")
@login_required
def dashboard():
    docs = Document.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard.html", username=current_user.username, documents=docs
    )

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        doc_name = request.form.get("doc_name")
        if doc_name:
            doc = Document(user_id=current_user.id, name=doc_name, status="uploaded")
            db.session.add(doc)
            db.session.commit()
            return redirect(url_for("dashboard"))
    return render_template("upload.html")

@app.route("/admin/clients")
@login_required
def admin_clients():
    return render_template("admin_clients.html", users=User.query.all())


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
