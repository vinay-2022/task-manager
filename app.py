from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit
import psycopg2
import pandas as pd
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'taskmanager123'

socketio = SocketIO(app, cors_allowed_origins="*")

# Database connection
def get_db():
    return psycopg2.connect(
        host="localhost",
        database="taskmanager",
        user="postgres",
        password="admin123",
        port="5432"
    )
@app.route('/')
def index():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (username, email, password)
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({'message': 'User registered successfully!'})

#login 

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data['email']
    password = data['password']

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user and check_password_hash(user[3], password):
        session['user_id'] = user[0]
        return jsonify({'message': 'Login successful!'})

    return jsonify({'message': 'Invalid credentials!'}), 401

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out!'})


#ADD TASK API
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()

    title = data['title']
    description = data['description']
    priority = data['priority']
    status = data['status']

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'message': 'Please login first'}), 401

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks (title, description, priority, status, user_id) VALUES (%s, %s, %s, %s, %s)",
        (title, description, priority, status, user_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Task added successfully'})

#GET TASKS API

@app.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'message': 'Please login first'}), 401

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, title, description, priority, status, user_id FROM tasks WHERE user_id = %s", (user_id,))
    tasks = cur.fetchall()

    columns = ['id', 'title', 'description', 'priority', 'status', 'user_id']
    tasks_list = [dict(zip(columns, row)) for row in tasks]

    cur.close()
    conn.close()

    return jsonify(tasks_list)

#UPDATE TASK API

@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tasks SET title=%s, description=%s, priority=%s, status=%s WHERE id=%s",
        (data['title'], data['description'], data['priority'], data['status'], id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Task updated successfully'})

#DELETE TASK API

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Task deleted successfully'})

# ANALYTICS API - Pandas & NumPy
@app.route('/analytics', methods=['GET'])
def analytics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Please login first'}), 401

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT status, priority FROM tasks WHERE user_id = %s", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return jsonify({'total': 0, 'completed': 0, 'pending': 0, 'percentage': 0})

    df = pd.DataFrame(rows, columns=['status', 'priority'])
    total = len(df)
    completed = len(df[df['status'] == 'completed'])
    pending = len(df[df['status'] == 'pending'])
    percentage = round(float(np.divide(completed, total) * 100), 2)

    return jsonify({
        'total_tasks': total,
        'completed_tasks': completed,
        'pending_tasks': pending,
        'completion_percentage': percentage
    })

# WEBSOCKET
@socketio.on('connect')
def on_connect():
    emit('connected', {'message': 'Connected!'})

@socketio.on('new_task')
def handle_new_task(data):
    emit('task_update', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)