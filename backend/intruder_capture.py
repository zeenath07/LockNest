import cv2
import os
import datetime
from backend.models.db import insert_intruder

def capture_intruder_image(vault_id):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise Exception("Failed to capture image")

    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    intruder_dir = os.path.join(PROJECT_ROOT, 'static', 'intruders')
    os.makedirs(intruder_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"intruder_{vault_id}_{timestamp}.jpg"
    filepath = os.path.join(intruder_dir, filename)
    cv2.imwrite(filepath, frame)

    image_path = f"/static/intruders/{filename}"  # Don't change this!
    # Save record in Supabase
    insert_intruder(vault_id, image_path)  # Timestamp handled in db helper

    return image_path, timestamp
