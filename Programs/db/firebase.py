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

import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import time
import os

# ========== CONFIGURATION ==========

# Path to your service account JSON
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"

# Firestore plant ID (you only have one plant)
PLANT_ID = "pbl-2025-bde03"

# Enable or disable image upload
USE_IMAGE_UPLOAD = False          # set to True if you want to upload images
IMAGE_PATH = "plant.jpg"          # image file on your device

# Firebase Storage bucket (only needed if USE_IMAGE_UPLOAD = True)
# Example: "your-project-id.appspot.com"
STORAGE_BUCKET = "your-project-id.appspot.com"

# Interval between readings (in seconds)
INTERVAL_SECONDS = 3600           # 3600 = 1 hour; use smaller value for testing


# ========== INITIALIZE FIREBASE ==========

cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)

if USE_IMAGE_UPLOAD:
    # Initialize with Storage bucket
    firebase_admin.initialize_app(cred, {
        "storageBucket": STORAGE_BUCKET
    })
    bucket = storage.bucket()
else:
    # Firestore only
    firebase_admin.initialize_app(cred)
    bucket = None

db = firestore.client()


# ========== HELPER FUNCTION ==========

def send_one_reading():
    """Send one reading to Firestore, optionally with image."""

    # Example sensor values (replace with real sensor readings later)
    temperature = 27.5      # °C
    humidity = 60.0         # %
    soil_moisture = 430     # arbitrary units

    # Timestamp (UTC)
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Optional image upload
    image_url = None
    if USE_IMAGE_UPLOAD:
        if IMAGE_PATH and os.path.exists(IMAGE_PATH):
            storage_path = f"plants/{PLANT_ID}/{timestamp}.jpg"
            blob = bucket.blob(storage_path)
            blob.upload_from_filename(IMAGE_PATH)
            blob.make_public()  # for demo: easy to open in browser
            image_url = blob.public_url
            print("Image uploaded:", image_url)
        else:
            print("Image upload enabled, but file not found:", IMAGE_PATH)

    # Data to send
    data = {
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture,
        "image_url": image_url,   # will be None if no image
    }

    # Firestore path: plants/{PLANT_ID}/readings/{auto_id}
    readings_ref = (
        db.collection("plants")
          .document(PLANT_ID)
          .collection("readings")
    )

    readings_ref.add(data)
    print("Data sent to Firestore:", data)


# ========== MAIN LOOP ==========

if __name__ == "__main__":
    print("Starting plant monitor loop...")
    print(f"Plant ID: {PLANT_ID}")
    print(f"Image upload enabled: {USE_IMAGE_UPLOAD}")
    print(f"Interval: {INTERVAL_SECONDS} seconds\n")

    while True:
        try:
            send_one_reading()
        except Exception as e:
            print("Error while sending data:", e)

        print(f"Waiting {INTERVAL_SECONDS} seconds...\n")
        time.sleep(INTERVAL_SECONDS)
