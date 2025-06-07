import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.pardir, "templates"),
    static_folder=os.path.join(os.path.pardir, "static"),
)

# Simple in-memory stores for demo purposes
users = []
documents = []

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # placeholder authentication
        return redirect(url_for('dashboard', username=username))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users.append({'username': username, 'password': password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    username = request.args.get('username', 'User')
    return render_template('dashboard.html', username=username, documents=documents)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        doc_name = request.form.get('doc_name')
        if doc_name:
            documents.append(doc_name)
        return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/admin/clients')
def admin_clients():
    return render_template('admin_clients.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
