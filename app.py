from flask import Flask, request, redirect, url_for, render_template_string
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Document, Status

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
login_manager = LoginManager(app)
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_first_request
def create_tables():
    db.create_all()
    if not Status.query.first():
        db.session.add(Status(name='new'))
        db.session.add(Status(name='processed'))
        db.session.commit()


@app.route('/')
def index():
    if current_user.is_authenticated:
        docs = Document.query.filter_by(user_id=current_user.id).all()
    else:
        docs = []
    return render_template_string(
        """
        <h1>Documents</h1>
        {% if current_user.is_authenticated %}
        <p>Logged in as {{ current_user.username }} - <a href="{{ url_for('logout') }}">Logout</a></p>
        <form method="post" action="{{ url_for('create_document') }}">
            <textarea name="content" placeholder="Document text"></textarea>
            <button type="submit">Save</button>
        </form>
        {% else %}
        <a href="{{ url_for('login') }}">Login</a> or
        <a href="{{ url_for('register') }}">Register</a>
        {% endif %}
        <ul>
        {% for doc in docs %}
            <li>{{ doc.content }} - {{ doc.status.name }}</li>
        {% endfor %}
        </ul>
        """,
        docs=docs,
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'User already exists', 400
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template_string(
        """
        <form method="post">
            <input name="username" placeholder="Username">
            <input name="password" type="password" placeholder="Password">
            <button type="submit">Register</button>
        </form>
        """
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        return 'Invalid credentials', 400
    return render_template_string(
        """
        <form method="post">
            <input name="username" placeholder="Username">
            <input name="password" type="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
        """
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/document', methods=['POST'])
@login_required
def create_document():
    content = request.form['content']
    status = Status.query.filter_by(name='new').first()
    doc = Document(content=content, user_id=current_user.id, status=status)
    db.session.add(doc)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
