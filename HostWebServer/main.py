# server.py
from flask import Flask, request

app = Flask(__name__)

@app.route('/debug', methods=['POST'])
def handle_debug():
    # Check the mimetype directly
    if request.mimetype == 'text/plain':
        data = request.get_data(as_text=True)
        print(f"Received message: {data}")
        # Process the message here (e.g., log it, trigger an action, etc.)
        return {'status': 'Message received'}, 200
    else:
        return {'error': 'Invalid content type, expecting plain text'}, 400

if __name__ == 'main':
    # Run on all interfaces, port 5000
    # Ensure your firewall allows connections on this port
    app.run(host='0.0.0.0', port=5000)
