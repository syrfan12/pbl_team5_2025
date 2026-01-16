"""
Integrated Plant Monitoring System
===================================
Combines:
- DHT11 Sensor (temperature & humidity)
- Soil moisture sensor
- Camera capture
- Roboflow inference for plant disease detection
- Image upload to imgbb
- Send all data to Firebase Firestore

Requirements:
    pip install firebase-admin opencv-python inference-sdk requests RPi.GPIO gpiozero dht11

Setup:
    1. Download serviceAccountKey.json from Firebase Console and place it here
    2. Fill config_settings.json with plant_id and other settings
    3. Fill config_roboflow.json with Roboflow API key
    4. Fill config_imgbb.json with imgbb API key (for image uploads)
"""

import os
import time
import json
import cv2
import requests
from datetime import datetime
from pathlib import Path

# Firebase imports
import firebase_admin
from firebase_admin import credentials, firestore

# Roboflow imports
from inference_sdk import InferenceHTTPClient

# Sensor imports (for Raspberry Pi)
try:
    import RPi.GPIO as GPIO
    import dht11
    RASPBERRY_PI = True
except ImportError:
    print("[WARN] RPi.GPIO not available. Running in simulation mode.")
    RASPBERRY_PI = False

# ==================== CONFIG ====================

# Load configurations
with open("config_roboflow.json", "r") as f:
    roboflow_config = json.load(f)

with open("config_imgbb.json", "r") as f:
    imgbb_config = json.load(f)

with open("config_settings.json", "r") as f:
    settings_config = json.load(f)

# Settings from config file
FIREBASE_SERVICE_ACCOUNT = settings_config.get("firebase_service_account_file", "serviceAccountKey.json")
PLANT_ID = settings_config.get("plant_id", "pbl-team5-app")
CAMERA_INDEX = settings_config.get("camera_index", 0)
INTERVAL_SECONDS = settings_config.get("interval_seconds", 3600)  # 1 hour = 3600 seconds
SOIL_SENSOR_PIN = settings_config.get("soil_sensor_pin", 17)
DHT_SENSOR_PIN = settings_config.get("dht_sensor_pin", 14)

# Directory settings
IMAGES_DIR = "captured_images"
INFERENCE_DIR = "inference_results"

# ================================================


def init_gpio():
    """Initialize GPIO for sensors (only on Raspberry Pi)"""
    if RASPBERRY_PI:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SOIL_SENSOR_PIN, GPIO.IN)
        return dht11.DHT11(pin=DHT_SENSOR_PIN)
    return None


def init_firebase():
    """Initialize Firebase Admin SDK"""
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("[INFO] Firebase initialized")
    return db


def init_roboflow():
    """Initialize Roboflow client"""
    client = InferenceHTTPClient(
        api_url=roboflow_config["api_url"],
        api_key=roboflow_config["api_key"]
    )
    print("[INFO] Roboflow client initialized")
    return client


def ensure_directories():
    """Create folders if they don't exist"""
    Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    Path(INFERENCE_DIR).mkdir(parents=True, exist_ok=True)


def capture_image():
    """Capture image from camera"""
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {CAMERA_INDEX}")
    
    # Warm up camera
    for _ in range(5):
        cap.read()
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        raise RuntimeError("Failed to capture image from camera")
    
    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.jpg"
    image_path = os.path.join(IMAGES_DIR, filename)
    cv2.imwrite(image_path, frame)
    
    print(f"[INFO] Image captured: {image_path}")
    return image_path, frame


def run_roboflow_inference(client, image_path):
    """Run inference using Roboflow"""
    result = client.infer(image_path, model_id=roboflow_config["model_id"])
    print(f"[INFO] Inference completed. Found {len(result['predictions'])} predictions")
    return result


def draw_bounding_boxes(image, predictions):
    """Draw bounding boxes on image"""
    for pred in predictions:
        x = int(pred["x"])
        y = int(pred["y"])
        w = int(pred["width"])
        h = int(pred["height"])
        label = pred["class"]
        conf = pred["confidence"]
        
        # Convert from center to corner
        x1 = int(x - w / 2)
        y1 = int(y - h / 2)
        x2 = int(x + w / 2)
        y2 = int(y + h / 2)
        
        # Draw bounding box
        color = (0, 255, 0) if label.lower() == "healthy" else (0, 0, 255)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        # Label text
        text = f"{label} {conf:.2f}"
        cv2.putText(image, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return image


def save_inference_result(image, timestamp):
    """Save image with bounding boxes"""
    filename = f"inference_{timestamp}.jpg"
    output_path = os.path.join(INFERENCE_DIR, filename)
    cv2.imwrite(output_path, image)
    print(f"[INFO] Inference result saved: {output_path}")
    return output_path


def analyze_health_status(predictions):
    """
    Analyze plant health status
    Return: "healthy" if all healthy, "disease" if any not healthy
    """
    if not predictions:
        return "unknown", []
    
    detected_classes = [pred["class"] for pred in predictions]
    
    # Check if all healthy
    all_healthy = all(cls.lower() == "healthy" for cls in detected_classes)
    
    if all_healthy:
        return "healthy", detected_classes
    else:
        return "disease", detected_classes


def upload_to_imgbb(image_path):
    """Upload image to imgbb and return URL"""
    url = "https://api.imgbb.com/1/upload"
    
    try:
        with open(image_path, "rb") as f:
            response = requests.post(
                url,
                params={"key": imgbb_config["api_key"]},
                files={"image": f},
                timeout=30
            )
        
        if response.status_code == 200:
            image_url = response.json()["data"]["url"]
            print(f"[INFO] Image uploaded to imgbb: {image_url}")
            return image_url
        else:
            print(f"[ERROR] imgbb upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to upload to imgbb: {e}")
        return None


def read_sensor_data(dht_instance):
    """Read data from DHT11 and soil moisture sensors"""
    if not RASPBERRY_PI:
        # Simulation mode
        print("[INFO] Simulation mode - generating dummy sensor data")
        return {
            "temperature": 27.5,
            "humidity": 60.0,
            "soil_moisture": "Moisture"
        }
    
    # Real sensor reading
    data = {
        "temperature": None,
        "humidity": None,
        "soil_moisture": None
    }
    
    # Read DHT11
    try:
        result = dht_instance.read()
        if result.is_valid():
            data["temperature"] = result.temperature
            data["humidity"] = result.humidity
            print(f"[INFO] Temperature: {data['temperature']}°C, Humidity: {data['humidity']}%")
        else:
            print("[WARN] DHT11 reading invalid")
    except Exception as e:
        print(f"[ERROR] Failed to read DHT11: {e}")
    
    # Read soil sensor
    try:
        sensor_value = GPIO.input(SOIL_SENSOR_PIN)
        data["soil_moisture"] = "Moisture" if sensor_value == 0 else "Dryness"
        print(f"[INFO] Soil: {data['soil_moisture']}")
    except Exception as e:
        print(f"[ERROR] Failed to read soil sensor: {e}")
    
    return data


def send_to_firebase(db, sensor_data, health_status, detected_classes, image_url):
    """Send all data to Firebase Firestore"""
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    
    data = {
        "timestamp": timestamp,
        "temperature": sensor_data.get("temperature"),
        "humidity": sensor_data.get("humidity"),
        "soil_moisture": sensor_data.get("soil_moisture"),
        "plant_status": health_status,
        "detected_classes": detected_classes,
        "image_url": image_url
    }
    
    # Send to Firestore
    readings_ref = (
        db.collection("plants")
          .document(PLANT_ID)
          .collection("readings")
    )
    
    readings_ref.add(data)
    print(f"[INFO] Data sent to Firebase: {data}")


def main_cycle(db, roboflow_client, dht_instance):
    """One complete data collection cycle"""
    print("\n" + "="*50)
    print(f"[INFO] Starting new cycle at {datetime.now()}")
    print("="*50)
    
    try:
        # 1. Read sensors
        print("\n[STEP 1] Reading sensors...")
        sensor_data = read_sensor_data(dht_instance)
        
        # 2. Capture image
        print("\n[STEP 2] Capturing image...")
        image_path, frame = capture_image()
        
        # 3. Run Roboflow inference
        print("\n[STEP 3] Running Roboflow inference...")
        inference_result = run_roboflow_inference(roboflow_client, image_path)
        predictions = inference_result.get("predictions", [])
        
        # 4. Analyze health status
        print("\n[STEP 4] Analyzing health status...")
        health_status, detected_classes = analyze_health_status(predictions)
        print(f"[INFO] Health status: {health_status}")
        print(f"[INFO] Detected classes: {detected_classes}")
        
        # 5. Draw bounding boxes and save
        print("\n[STEP 5] Drawing bounding boxes...")
        annotated_image = draw_bounding_boxes(frame.copy(), predictions)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        inference_path = save_inference_result(annotated_image, timestamp)
        
        # 6. Upload to imgbb
        print("\n[STEP 6] Uploading to imgbb...")
        image_url = upload_to_imgbb(inference_path)
        
        # 7. Send to Firebase
        print("\n[STEP 7] Sending to Firebase...")
        send_to_firebase(db, sensor_data, health_status, detected_classes, image_url)
        
        print("\n[SUCCESS] Cycle completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Cycle failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main program loop"""
    print("="*50)
    print("INTEGRATED PLANT MONITORING SYSTEM")
    print("="*50)
    
    # Initialize
    ensure_directories()
    dht_instance = init_gpio()
    db = init_firebase()
    roboflow_client = init_roboflow()
    
    print(f"\n[INFO] System initialized")
    print(f"[INFO] Running cycle every {INTERVAL_SECONDS / 3600:.1f} hours")
    print(f"[INFO] Raspberry Pi mode: {RASPBERRY_PI}")
    
    # Main loop
    while True:
        try:
            main_cycle(db, roboflow_client, dht_instance)
        except KeyboardInterrupt:
            print("\n\n[INFO] Program stopped by user")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
        
        # Wait for next cycle
        print(f"\n[INFO] Sleeping for {INTERVAL_SECONDS / 3600:.1f} hours...")
        print(f"[INFO] Next cycle at {datetime.fromtimestamp(time.time() + INTERVAL_SECONDS)}")
        time.sleep(INTERVAL_SECONDS)
    
    # Cleanup
    if RASPBERRY_PI:
        GPIO.cleanup()
    print("[INFO] Program terminated")


if __name__ == "__main__":
    main()
