"""
Read all readings for a single plant from Firestore and print them.

Requirements:
    pip install firebase-admin
"""

import firebase_admin
from firebase_admin import credentials, firestore

# === CONFIG ===
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"  # same file as before
PLANT_ID = "pbl-team5-app"                             # same plant id


# === INIT FIREBASE ===
cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
firebase_admin.initialize_app(cred)

db = firestore.client()


# === READ DATA ===

# Path: plants/{PLANT_ID}/readings
readings_ref = (
    db.collection("plants")
      .document(PLANT_ID)
      .collection("readings")
)

# get() returns all documents in this collection
docs = readings_ref.get()

print(f"Found {len(docs)} readings for plant '{PLANT_ID}':\n")

for doc in docs:
    data = doc.to_dict()
    print(f"Doc ID: {doc.id}")
    print(f"  timestamp     : {data.get('timestamp')}")
    print(f"  temperature   : {data.get('temperature')}")
    print(f"  humidity      : {data.get('humidity')}")
    print(f"  soil_moisture : {data.get('soil_moisture')}")
    print(f"  image_url     : {data.get('image_url')}")
    print()
