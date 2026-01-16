# Integrated Plant Monitoring System

Integrated plant monitoring system that combines sensors, camera, AI detection, and cloud storage.

## 🌟 Features

- ✅ Automatic image capture every hour
- ✅ Plant disease detection using Roboflow AI
- ✅ Temperature & humidity sensor reading (DHT11)
- ✅ Soil moisture sensor reading
- ✅ Upload inference result images to imgbb
- ✅ Data storage to Firebase Firestore
- ✅ Health status: "healthy" if all plants are healthy, "disease" if there's any disease

## 📋 Requirements

### Hardware
- Raspberry Pi (for sensors)
- USB Camera or Pi Camera
- DHT11 Sensor (Temperature & Humidity)
- Soil Moisture Sensor
- Internet Connection

### Software
```bash
pip install firebase-admin opencv-python inference-sdk requests RPi.GPIO gpiozero dht11
```

## 🚀 Setup

### 1. Clone Repository
```bash
cd Programs/integrated_system
```

### 2. Configure JSON Files

#### config_firebase.json
```json
{
  "service_account_file": "serviceAccountKey.json",
  "storage_bucket": "your-project-id.appspot.com",
  "plant_id": "pbl-team5-app"
}
```

#### config_roboflow.json
```json
{
  "api_url": "https://detect.roboflow.com",
  "api_key": "YOUR_ROBOFLOW_API_KEY",
  "model_id": "your-model-id/version"
}
```

#### config_imgbb.json
```json
{
  "api_key": "YOUR_IMGBB_API_KEY"
}
```

### 3. Download Service Account Key
- Go to Firebase Console → Project Settings → Service Accounts
- Generate new private key
- Save as `serviceAccountKey.json` in this folder

### 4. Get API Keys

**Roboflow:**
- Login to [roboflow.com](https://roboflow.com)
- Open workspace → API → Copy API key
- Also copy the model ID from your model

**imgbb:**
- Login/Register di [imgbb.com](https://imgbb.com)
- Pergi ke [API](https://api.imgbb.com/)
- Copy API key

## 📂 File Structure

```
integrated_system/
├── integrated_monitor.py       # Main program
├── config_firebase.json        # Firebase configuration
├── config_roboflow.json        # Roboflow configuration
├── config_imgbb.json           # imgbb configuration
├── serviceAccountKey.json      # Firebase credentials (don't commit!)
├── captured_images/            # Original images folder (auto-created)
├── inference_results/          # Inference result images folder (auto-created)
└── README.md                   # This documentation
```

## ▶️ Running the Program

### Normal Mode (Raspberry Pi with sensors)
```bash
python integrated_monitor.py
```

### Simulation Mode (PC without sensors)
The program will automatically detect if RPi.GPIO is not available and use dummy data for sensors.
```bash
python integrated_monitor.py
```

## 🔄 Program Workflow

1. **Every hour**, the program will:
   - Read data from DHT11 sensor (temperature & humidity)
   - Read data from soil moisture sensor
   - Capture photo from camera
   - Run Roboflow inference for disease detection
   - Draw bounding boxes on detection results
   - Save image with bounding boxes to folder
   - Upload image to imgbb
   - Analyze status: 
     - ✅ **"healthy"** if all detections are "Healthy"
     - ⚠️ **"disease"** if at least 1 is not "Healthy"
   - Send all data to Firebase Firestore

## 📊 Data Sent to Firebase

```json
{
  "timestamp": "2026-01-16T10:00:00Z",
  "temperature": 27.5,
  "humidity": 60.0,
  "soil_moisture": "Moisture",
  "plant_status": "healthy",
  "detected_classes": ["Healthy", "Healthy"],
  "image_url": "https://i.ibb.co/xxxxx/image.jpg"
}
```

Data is stored at:
```
Firestore: /plants/{plant_id}/readings/{auto_id}
```

## ⚙️ Configuration

Change constants in `integrated_monitor.py` if needed:

```python
CAMERA_INDEX = 0                # Camera index (0, 1, 2, ...)
INTERVAL_SECONDS = 3600         # Data collection interval (seconds)
SOIL_SENSOR_PIN = 17            # GPIO pin soil sensor
DHT_SENSOR_PIN = 14             # GPIO pin DHT11
```

## 🐛 Troubleshooting

### Camera won't open
- Check if camera is connected: `ls /dev/video*`
- Try changing `CAMERA_INDEX` to 1 or 2
- Make sure camera permissions are granted

### Sensor not readable
- Check GPIO connections
- Make sure pin number matches (BCM mode)
- Test sensor separately

### Firebase error
- Make sure `serviceAccountKey.json` exists and is valid
- Check storage bucket name is correct
- Make sure Firestore is enabled

### Roboflow inference failed
- Check API key is valid
- Make sure model_id format: `workspace/model/version`
- Check internet connection

### imgbb upload failed
- Check API key is valid
- Check image size (max 32 MB)
- Check internet connection

## 📝 Log Output

The program will display complete logs:
```
==================================================
INTEGRATED PLANT MONITORING SYSTEM
==================================================
[INFO] Firebase initialized
[INFO] Roboflow client initialized
[INFO] System initialized
[INFO] Running cycle every 1.0 hours

==================================================
[INFO] Starting new cycle at 2026-01-16 10:00:00
==================================================

[STEP 1] Reading sensors...
[INFO] Temperature: 27.5°C, Humidity: 60.0%
[INFO] Soil: Moisture

[STEP 2] Capturing image...
[INFO] Image captured: captured_images/20260116_100000.jpg

[STEP 3] Running Roboflow inference...
[INFO] Inference completed. Found 2 predictions

[STEP 4] Analyzing health status...
[INFO] Health status: healthy
[INFO] Detected classes: ['Healthy', 'Healthy']

[STEP 5] Drawing bounding boxes...
[INFO] Inference result saved: inference_results/inference_20260116_100000.jpg

[STEP 6] Uploading to imgbb...
[INFO] Image uploaded to imgbb: https://i.ibb.co/xxxxx/image.jpg

[STEP 7] Sending to Firebase...
[INFO] Data sent to Firebase: {...}

[SUCCESS] Cycle completed successfully!

[INFO] Sleeping for 1.0 hours...
[INFO] Next cycle at 2026-01-16 11:00:00
```

## 🔒 Security Notes

- **DO NOT** commit `serviceAccountKey.json` file to Git
- **DO NOT** commit `config_*.json` files with API keys to public repository
- Use `.gitignore` to exclude sensitive files:
  ```
  serviceAccountKey.json
  config_*.json
  *.pyc
  __pycache__/
  captured_images/
  inference_results/
  ```

## 📞 Support

For questions or issues, contact PBL Team 5.

## 📄 License

This project is for PBL Team 5 2025 academic purposes.
