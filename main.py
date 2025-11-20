import requests

url = "http://31.173.81.24:5000/upload"

print("hello")
with open("img/image.png", "rb") as f:
    image_data = f.read()

# Важно: отправлять как бинарные данные, а не через multipart/form-data
response = requests.post(
    url,
    data=image_data,
    headers={"Content-Type": "image"}
)

print(response.text)
