from flask import Flask, render_template
from flask_socketio import SocketIO
from get_knee_data import get_knee_data  # Import your function
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Serve a simple page for testing (optional)
@app.route('/')
def index():
    return "<h1>Raspberry Pi Server is Running</h1>"

# Background thread to emit data continuously
def emit_knee_data():
    while True:
        data = get_knee_data()
        if data:
            socketio.emit('knee_data', data)
            print(f"Sent data: {data}")  # Debug log
        time.sleep(0.1)  # Adjust data sending rate as needed

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == "__main__":
    # Start the background thread for sending data
    thread = threading.Thread(target=emit_knee_data)
    thread.daemon = True
    thread.start()

    # Run the Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000)