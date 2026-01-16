# import the inference-sdk
from inference_sdk import InferenceHTTPClient
import cv2
import json

# load config from JSON file
with open("config.json", "r") as f:
    config = json.load(f)

image_path = "./images/20260114_183734.jpg"
image = cv2.imread(image_path)

# initialize the client
CLIENT = InferenceHTTPClient(
    api_url=config["api_url"],
    api_key=config["api_key"]
)

# infer on a local image
result = CLIENT.infer(image_path, model_id=config["model_id"])
print(result)

for pred in result["predictions"]:
    x = int(pred["x"])
    y = int(pred["y"])
    w = int(pred["width"])
    h = int(pred["height"])
    label = pred["class"]
    conf = pred["confidence"]

    # konversi dari center ke corner
    x1 = int(x - w / 2)
    y1 = int(y - h / 2)
    x2 = int(x + w / 2)
    y2 = int(y + h / 2)

    # draw bounding box
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # label text
    text = f"{label} {conf:.2f}"
    cv2.putText(
        image,
        text,
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

cv2.imwrite("output_bbox=2.png", image)
print("Bounding box saved as output_bbox.png")
