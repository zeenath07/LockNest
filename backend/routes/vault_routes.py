import os
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file
from backend.models.db import get_db_connection
from cryptography.fernet import Fernet

vault_bp = Blueprint('vault', __name__)

# Directory for encrypted vault files (in project root)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vault_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FERNET_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vault-fernet.key')
if os.path.isfile(FERNET_KEY_FILE):
    with open(FERNET_KEY_FILE, 'rb') as f:
        FERNET_KEY = f.read()
else:
    FERNET_KEY = Fernet.generate_key()
    with open(FERNET_KEY_FILE, 'wb') as f:
        f.write(FERNET_KEY)
fernet = Fernet(FERNET_KEY)

@vault_bp.route('/files', methods=['GET'])
def get_files():
    vault_id = request.args.get('vault_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT filename, uploaded_at FROM vault_files WHERE vault_id = ?', (vault_id,))
    files = [{'filename': row[0], 'uploaded_at': row[1]} for row in cur.fetchall()]
    conn.close()
    return jsonify({'files': files})

@vault_bp.route('/upload', methods=['POST'])
def upload_file():
    vault_id = request.form.get('vault_id')
    file = request.files['file']
    filename = file.filename

    # Read and encrypt file content
    original_content = file.read()
    encrypted_content = fernet.encrypt(original_content)

    # Save encrypted file with .enc extension
    enc_filename = filename + '.enc'
    filepath = os.path.join(UPLOAD_FOLDER, enc_filename)
    with open(filepath, 'wb') as f:
        f.write(encrypted_content)

    # Store original filename but save path to encrypted file in DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO vault_files (vault_id, filename, filepath) VALUES (?, ?, ?)',
                (vault_id, filename, filepath))
    conn.commit()
    conn.close()
    return jsonify({'message': 'File uploaded and encrypted successfully'})

@vault_bp.route('/download', methods=['GET'])
def download_file():
    vault_id = request.args.get('vault_id')
    filename = request.args.get('filename')
    enc_filepath = os.path.join(UPLOAD_FOLDER, filename + '.enc')

    if not os.path.exists(enc_filepath):
        return jsonify({'error': 'File not found'}), 404

    # Decrypt encrypted content before sending
    with open(enc_filepath, 'rb') as f:
        encrypted_content = f.read()
    decrypted_content = fernet.decrypt(encrypted_content)

    # Send decrypted file to client with original filename
    return send_file(BytesIO(decrypted_content), as_attachment=True, download_name=filename)

@vault_bp.route('/delete', methods=['POST'])
def delete_file():
    data = request.json
    vault_id = data.get('vault_id')
    filename = data.get('filename')
    if not vault_id or not filename:
        return jsonify({'error': 'Missing vault_id or filename'}), 400

    enc_filename = filename + '.enc'
    file_path = os.path.join(UPLOAD_FOLDER, enc_filename)
    deleted = False

    # Delete from disk
    if os.path.exists(file_path):
        os.remove(file_path)
        deleted = True

    # Delete from DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM vault_files WHERE vault_id = ? AND filename = ?', (vault_id, filename))
    conn.commit()
    conn.close()

    if deleted:
        return jsonify({'message': f'{filename} deleted successfully.'})
    else:
        return jsonify({'error': 'File not found on server.'}), 404
