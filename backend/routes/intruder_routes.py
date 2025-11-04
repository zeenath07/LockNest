import base64
import os
import time
from flask import Blueprint, request, jsonify
from backend.models.db import get_db_connection

intruder_bp = Blueprint('intruder', __name__)

# Get absolute path to static/intruders/ at project root
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

    # Remove base64 header if present
    if ',' in image_base64:
        image_base64 = image_base64.split(',', 1)[1]
    image_bytes = base64.b64decode(image_base64)
    filename = f'{vault_id}_intruder_{int(time.time())}.jpg'
    filepath = os.path.join(INTRUDER_IMAGE_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(image_bytes)

    conn = get_db_connection()
    cur = conn.cursor()
    relative_path = f"/static/intruders/{filename}"
    cur.execute('INSERT INTO intruders (vault_id, image_path) VALUES (?, ?)', (vault_id, relative_path))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Intruder image captured'})

@intruder_bp.route('/logs', methods=['GET'])
def get_intruder_logs():
    vault_id = request.args.get('vault_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT image_path, timestamp FROM intruders WHERE vault_id = ? ORDER BY timestamp DESC', (vault_id,))
    intruders = [{'image': row[0], 'timestamp': row[1]} for row in cur.fetchall()]
    conn.close()
    return jsonify({'intruders': intruders})
