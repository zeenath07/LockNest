from flask import Blueprint, request, jsonify
from backend.models.db import get_db_connection
import hashlib

user_bp = Blueprint('user', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    vault_id = data.get('vault_id')
    password = data.get('password')

    if not vault_id or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    # Check if vault_id exists
    cur.execute('SELECT * FROM users WHERE vault_id = ?', (vault_id,))
    if cur.fetchone():
        conn.close()
        return jsonify({'error': 'Vault ID already exists'}), 409

    hashed_password = hash_password(password)
    cur.execute('INSERT INTO users (vault_id, password) VALUES (?, ?)', (vault_id, hashed_password))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Signup successful'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    vault_id = data.get('vault_id')
    password = data.get('password')

    if not vault_id or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT password FROM users WHERE vault_id = ?', (vault_id,))
    row = cur.fetchone()

    # Check for correct password
    if row and row['password'] == hash_password(password):
        conn.close()
        return jsonify({'message': 'Login successful'}), 200
    else:
        # Log intruder attempt (fail with blank image path for now)
        cur.execute('INSERT INTO intruders (vault_id, image_path) VALUES (?, ?)', (vault_id or '(none)', ''))
        conn.commit()
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401
