from flask import Blueprint, request, jsonify
import hashlib
from backend.models.db import add_user, get_user_by_vault_id, insert_intruder

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

    existing_user = get_user_by_vault_id(vault_id)
    if existing_user:
        return jsonify({'error': 'Vault ID already exists'}), 409

    hashed_password = hash_password(password)
    add_user(vault_id, hashed_password)
    return jsonify({'message': 'Signup successful'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    vault_id = data.get('vault_id')
    password = data.get('password')

    if not vault_id or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    user = get_user_by_vault_id(vault_id)

    if user and user['password'] == hash_password(password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        # Log intruder attempt (blank image path for now)
        insert_intruder(vault_id or '(none)', '')
        return jsonify({'error': 'Invalid credentials'}), 401
