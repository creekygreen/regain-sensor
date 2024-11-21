# Imports
from flask import Flask, render_template
from flask_socketio import SocketIO
from knee_data import get_knee_data

app = Flask(__name__)
socketio = SocketIO(app) 

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('start_data_stream')
def stream_knee_data():
    while True:
        # try to catch exception in knee_data
        try:
            data = get_knee_data()
            if data:
                socketio.emit('knee_data', data)
            else:
                print("No data to emit")
        except Exception as e:
            print(f"Error in stream_knee_data: {e}")
        socketio.sleep(0.1)

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True) # allow_unsafe_werkzeug=True in order to run on thonny shell
    
# If in Raspberry Pi
# 1. source regain/bin/activate
# 2. cd regain-sensor
# 3. python3 app.py

