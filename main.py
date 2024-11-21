# Imports
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ in '__main__':
    app.run(debug=True, host='0.0.0.0')

# 1. Activate the virtual environment: regain
# Command: source regain/bin/activate to activate virtual environment

# 2. Run the the python application
# Command: cd webdb
# Command: python3 app.py
