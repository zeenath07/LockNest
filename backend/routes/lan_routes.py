from flask import Blueprint, request, jsonify, send_from_directory
import socket
import subprocess
import threading
import platform
import os

lan_bp = Blueprint('lan', __name__)

# Device scan (discovery) logic
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

def ping_worker(ip, found):
    try:
        arg = "-n" if platform.system().lower() == "windows" else "-c"
        cmd = ["ping", arg, "1", ip]
        completed = subprocess.run(cmd, capture_output=True, text=True)
        if ("TTL=" in completed.stdout) or ("ttl=" in completed.stdout):
            try:
                name = socket.gethostbyaddr(ip)[0]
            except Exception:
                name = ""
            found.append({'ip': ip, 'name': name})
    except Exception:
        pass

@lan_bp.route('/devices', methods=['GET'])
def devices():
    base_ip = get_local_ip().rsplit('.', 1)[0]
    threads = []
    found = []
    for i in range(1, 255):  # full /24 subnet
        ip = f"{base_ip}.{i}"
        t = threading.Thread(target=ping_worker, args=(ip, found))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return jsonify({"devices": found, "base": base_ip})

# --- FILE TRANSFER/QUEUE LOGIC ---
RECEIVE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'incoming_files')
os.makedirs(RECEIVE_FOLDER, exist_ok=True)

incoming_files = []

@lan_bp.route('/file/receive', methods=['POST'])
def receive_file():
    if 'file' not in request.files:
        return {'error': 'No file uploaded'}, 400
    file = request.files['file']
    file.save(os.path.join(RECEIVE_FOLDER, file.filename))
    incoming_files.append({
        'filename': file.filename,
        'size': os.path.getsize(os.path.join(RECEIVE_FOLDER, file.filename))
    })
    return {'message': 'Received', 'filename': file.filename}, 200

@lan_bp.route('/incoming_files', methods=['GET'])
def list_incoming_files():
    return jsonify(incoming_files)

@lan_bp.route('/incoming_files/<filename>', methods=['GET'])
def serve_incoming_file(filename):
    print("Request to serve:", filename)
    print("Files present now:", os.listdir(RECEIVE_FOLDER))
    return send_from_directory(RECEIVE_FOLDER, filename)


@lan_bp.route('/incoming_files/accept/<filename>', methods=['POST'])
def accept_file(filename):
    global incoming_files
    # ONLY remove from the queue — DO NOT delete file from disk!
    incoming_files = [f for f in incoming_files if f['filename'] != filename]
    return {'message': f'Accepted {filename}'}


@lan_bp.route('/incoming_files/reject/<filename>', methods=['POST'])
def reject_file(filename):
    global incoming_files
    try:
        os.remove(os.path.join(RECEIVE_FOLDER, filename))
    except FileNotFoundError:
        pass
    incoming_files = [f for f in incoming_files if f['filename'] != filename]
    return {'message': f'Rejected {filename}'}
