import base64
import os
import time
from flask import Blueprint, request, jsonify
# Import the new Supabase helpers
from backend.models.db import insert_intruder, get_intruders

intruder_bp = Blueprint('intruder', __name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTRUDER_IMAGE_DIR = os.path.join(PROJECT_ROOT, 'static', 'intruders')
os.makedirs(INTRUDER_IMAGE_DIR, exist_ok=True)

@intruder_bp.route('/report', methods=['POST'])
def report_intruder():
    data = request.json
    vault_id = data.get('vault_id')
    image_base64 = data.get('image_base64')
    if not vault_id or not image_base64:
        return jsonify({'error': 'Missing data'}), 400

    if ',' in image_base64:
        image_base64 = image_base64.split(',', 1)[1]
    image_bytes = base64.b64decode(image_base64)
    filename = f'{vault_id}_intruder_{int(time.time())}.jpg'
    filepath = os.path.join(INTRUDER_IMAGE_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(image_bytes)

    relative_path = f"/static/intruders/{filename}"
    # Use the new Supabase DB helper - timestamp set inside insert_intruder
    insert_intruder(vault_id, relative_path)

    return jsonify({'message': 'Intruder image captured'})

@intruder_bp.route('/logs', methods=['GET'])
def get_intruder_logs():
    vault_id = request.args.get('vault_id')
    # Use new Supabase helper
    logs = get_intruders(vault_id)
    intruders = [{'image': row['image_path'], 'timestamp': row['timestamp']} for row in logs]
    return jsonify({'intruders': intruders})
