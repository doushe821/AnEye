from flask import Flask, request, jsonify
import os
from datetime import datetime

name = "__main__"
app = Flask(name)

@app.route('/upload', methods=['POST'])
def upload_image():
    if request.data and request.content_type:
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        print(request)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uploads/capture_{timestamp}.jpg"

        with open(filename, 'wb') as f:
            f.write(request.data)

        print(f"Image saved as {filename}")
        return f"Image uploaded successfully as {filename}", 200
    else:
        return "No image data received", 400

@app.route('/message', methods=['POST'])
def receive_message():
    print("received message")
    message = None

    if request.form.get('message'):
        message = request.form.get('message')
    elif request.is_json:
        json_data = request.get_json()
        if json_data and 'message' in json_data:
            message = json_data['message']
    elif request.data:
        message = request.data.decode('utf-8')

    if message:
        print(f"Received message: {message}")
        with open("Output.txt") as F:
            F.write(message)
        return f"Message received: {message}", 200
    else:
        return "No message data received", 400

@app.route("/message", methods=["GET"])
def send_message():
    print("h")

    # Optional: Get query parameters from ESP32 request
    message_param = request.args.get('msg')  # e.g., /message?msg=hello
    device_id = request.args.get('device')   # e.g., /message?device=esp32_001

    # Example: Return JSON response
    response_data = {
        "status": "received",
        "message": "Hello from server",
        "timestamp": "2025-11-21T12:00:00Z"
    }

    # For ESP32, you might want to return plain text
    # return "OK", 200

    # Or return JSON
    return jsonify(response_data), 200

if name == "__main__":
    app.run(host='0.0.0.0', port=5000)
