"""
Simple plant monitor with loop:
- Sends one reading to Firestore every hour
- Optional: uploads one image to Firebase Storage

Requirements:
    pip install firebase-admin

Before running:
    1. Put your serviceAccountKey.json in this folder
    2. Set SERVICE_ACCOUNT_FILE and STORAGE_BUCKET below
"""

import os
import time
from datetime import datetime

import cv2
import firebase_admin
from firebase_admin import credentials, firestore, storage

# ================== CONFIG ==================

SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"

PLANT_ID = "pbl-team5-app"

# If True: upload image to Firebase Storage and save image_url in Firestore
# If False: no upload, image_url will be None
USE_IMAGE_UPLOAD = False

# Only needed if USE_IMAGE_UPLOAD = True
STORAGE_BUCKET = "your-project-id.appspot.com"

# Camera settings
CAMERA_INDEX = 0          # 0 usually works; try 1 if not
LOCAL_IMAGE_NAME = "latest.jpg"

# Loop interval
INTERVAL_SECONDS = 3600   # set to 5 for testing

# ============================================


def init_firebase():
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)

    if USE_IMAGE_UPLOAD:
        firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})
        bucket = storage.bucket()
    else:
        firebase_admin.initialize_app(cred)
        bucket = None

    db = firestore.client()
    return db, bucket


def take_photo(image_path: str) -> bool:
    """
    Capture one photo from the camera and save it to image_path.
    Returns True if success, False if failed.
    """
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[ERROR] Cannot open camera. Try CAMERA_INDEX = 1 or check camera permissions.")
        return False

    # Warm up camera a bit (sometimes first frame is black)
    for _ in range(5):
        cap.read()

    ok, frame = cap.read()
    cap.release()

    if not ok or frame is None:
        print("[ERROR] Failed to capture image from camera.")
        return False

    ok = cv2.imwrite(image_path, frame)
    if not ok:
        print("[ERROR] Failed to write image to file:", image_path)
        return False

    return True


def upload_image(bucket, local_path: str, storage_path: str) -> str | None:
    """
    Upload local file to Firebase Storage, make it public, return public URL.
    """
    if not os.path.exists(local_path):
        print("[WARN] Image file not found:", local_path)
        return None

    blob = bucket.blob(storage_path)
    blob.upload_from_filename(local_path)
    blob.make_public()  # simple for school demo
    return blob.public_url


def send_one_reading(db, bucket):
    # Dummy sensor values (replace later with real sensors)
    temperature = 27.5
    humidity = 60.0
    soil_moisture = 430

    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    image_url = None
    if USE_IMAGE_UPLOAD:
        # 1) Take photo
        ok = take_photo(LOCAL_IMAGE_NAME)
        if ok:
            # 2) Upload photo
            storage_path = f"plants/{PLANT_ID}/{timestamp}.jpg"
            image_url = upload_image(bucket, LOCAL_IMAGE_NAME, storage_path)
            print("[INFO] Image URL:", image_url)
        else:
            print("[WARN] Image capture failed, sending data without image.")

    data = {
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture,
        "image_url": image_url,
    }

    readings_ref = (
        db.collection("plants")
          .document(PLANT_ID)
          .collection("readings")
    )

    readings_ref.add(data)
    print("[INFO] Sent:", data)


def main():
    db, bucket = init_firebase()
    print("[INFO] Started loop.")
    print("[INFO] Image upload:", USE_IMAGE_UPLOAD)
    print("[INFO] Interval seconds:", INTERVAL_SECONDS)

    while True:
        try:
            send_one_reading(db, bucket)
        except Exception as e:
            print("[ERROR] Failed to send reading:", e)

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
