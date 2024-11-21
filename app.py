# Imports
from flask import Flask, render_template
from flask_socketio import SocketIO
from knee_data import get_knee_data

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
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    
"""
1. cd regain-sensor
2. source regain_env/bin/activate
3. python3 app.py

"""

