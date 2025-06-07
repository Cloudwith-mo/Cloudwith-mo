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
    app.run(debug=True)
