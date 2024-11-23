from flask import Flask, render_template
from flask_socketio import SocketIO
import socketio

# Flask App for Web Frontend
app = Flask(__name__)
socketio = SocketIO(app)

# Socket.IO Client to Connect to Raspberry Pi
sio = socketio.Client()

# Raspberry Pi Server Address
PI_SERVER = "http://192.168.0.0:5000"  # Replace with Raspberry Pi's IP

# store latest knee data
latest_knee_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@sio.on('connect')
def on_connect():
    print("Connected to Raspberry Pi server")

@sio.on('disconnect')
def on_disconnect():
    print("Disconnected from Raspberry Pi server")

@sio.on('knee_data')
def handle_knee_data(data):
    global latest_knee_data
    latest_knee_data = data
    print("Received data:", data)
    socketio.emit('knee_data', data)  # Emit data to the frontend

@socketio.on('connect')
def handle_web_connect():
    print("Frontend connected")

@socketio.on('disconnect')
def handle_web_disconnect():
    print("Frontend disconnected")

def main():
    try:
        # Connect to Raspberry Pi server
        sio.connect(PI_SERVER)
        sio.wait()  # Keep the client running
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Start Flask-SocketIO server for the frontend
    socketio.run(app, host='0.0.0.0', port=5000)

    # Start the Raspberry Pi connection
    main()