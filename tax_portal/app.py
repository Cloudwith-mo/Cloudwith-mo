import os
=======

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# In-memory "database" for demonstration
users = {}
clients = {}
admin_credentials = {'username': 'admin', 'password': 'adminpass'}

# Utilities

def get_client(username):
    return clients.setdefault(username, {
        'documents': [],
        'status': 'Uploaded',
        'notifications': []
    })

# Auth endpoints (simplified)
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if username in users:
        return jsonify({'error': 'User exists'}), 400
    users[username] = password
    get_client(username)  # init client record
    return jsonify({'message': 'Registered'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if users.get(username) != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({'message': 'Logged in', 'username': username})

# Document upload
@app.route('/client/upload', methods=['POST'])
def upload():
    username = request.form.get('username')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    client = get_client(username)
    client['documents'].append({'filename': filename, 'status': 'uploaded'})
    client['notifications'].append(f'Document {filename} uploaded')
    return jsonify({'message': 'File uploaded'})

# Client status
@app.route('/client/status', methods=['GET'])
def status():
    username = request.args.get('username')
    client = get_client(username)
    return jsonify({'status': client['status'], 'documents': client['documents']})

# Client notifications
@app.route('/client/notifications', methods=['GET'])
def notifications():
    username = request.args.get('username')
    client = get_client(username)
    return jsonify({'notifications': client['notifications']})

# Admin endpoints
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('username') == admin_credentials['username'] and data.get('password') == admin_credentials['password']:
        return jsonify({'message': 'Admin logged in'})
    return jsonify({'error': 'Invalid admin credentials'}), 401

@app.route('/admin/clients', methods=['GET'])
def list_clients():
    return jsonify({'clients': list(clients.keys())})

@app.route('/admin/client/<username>', methods=['GET'])
def view_client(username):
    client = get_client(username)
    return jsonify(client)

@app.route('/admin/client/<username>/status', methods=['POST'])
def update_status(username):
    client = get_client(username)
    new_status = request.json.get('status')
    if new_status:
        client['status'] = new_status
        client['notifications'].append(f'Status updated to {new_status}')
    return jsonify({'status': client['status']})

if __name__ == '__main__':
=======
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

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.pardir, "templates"),
    static_folder=os.path.join(os.path.pardir, "static"),
)
=======
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
