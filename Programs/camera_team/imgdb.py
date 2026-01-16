import requests

API_KEY = ""
url = "https://api.imgbb.com/1/upload"

with open(r"img.jpg", "rb") as f:
    r = requests.post(
        url,
        params={"key": API_KEY},
        files={"image": f}
    )

print(r.json()["data"]["url"])
