# Imports
from flask import Flask, render_template
from flask_socketio import SocketIO
import get_knee_data

app = Flask(__name__)
socketio = SocketIO(app) # SocketIO

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('start_data_stream')
def stream_knee_data():
    while True:
        data = get_knee_data.get_knee_data()
        socketio.emit('knee_data', data)
        socketio.sleep(0.1)

if __name__ == "__main__":
    socketio.run(app, debug=True)

