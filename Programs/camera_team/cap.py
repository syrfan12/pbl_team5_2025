# capture_service.py
import sqlite3
import os
import cv2
from datetime import datetime
import time
import pathlib
import sys

DB_PATH = "captures.db"
IMAGES_DIR = "images"
POLL_INTERVAL_SECONDS = 2
CAMERA_INDEX = 0

def ensure_db_exists():
    if not os.path.exists(DB_PATH):
        print(f"Database '{DB_PATH}' not found. Please run 'python init_db.py' to create it and add a job.")
        sys.exit(1)

def get_pending_rows(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM captures WHERE is_on = 1 ORDER BY id")
    rows = cur.fetchall()
    return [r[0] for r in rows]

def capture_image(camera_index=CAMERA_INDEX):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError(f"Cannot open camera index {camera_index}")
    time.sleep(0.2)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        raise RuntimeError("Failed to read frame from camera")
    return frame

def save_image(frame, row_id):
    pathlib.Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{row_id}_{ts}.jpg"
    path = os.path.join(IMAGES_DIR, filename)
    success = cv2.imwrite(path, frame)
    if not success:
        raise RuntimeError(f"Failed to write image to {path}")
    return os.path.abspath(path)

def process_one(conn, row_id):
    try:
        frame = capture_image()
        image_path = save_image(frame, row_id)
        captured_at = datetime.now().isoformat(timespec='seconds')
        cur = conn.cursor()
        cur.execute("""UPDATE captures
            SET image_path = ?, captured_at = ?, is_on = 0
            WHERE id = ?""", (image_path, captured_at, row_id))
        conn.commit()
        print(f"[OK] row {row_id} -> {image_path} at {captured_at}")
    except Exception as e:
        print(f"[ERROR] row {row_id}: {e}")

def main_loop():
    ensure_db_exists()
    print("Starting capture service. Polling DB every", POLL_INTERVAL_SECONDS, "seconds.")
    while True:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        try:
            pending = get_pending_rows(conn)
            if pending:
                for row_id in pending:
                    process_one(conn, row_id)
        finally:
            conn.close()
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main_loop()
