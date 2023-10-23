import os

from sys import stderr
from flask import Flask, request
from flask_cors import CORS
from execute import handler as execute_handler

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_geek():
    return '<h1>Hello from jupyterhub executor</h1>'

@app.route('/execute', methods=['POST'])
def api_endpoint():
    return execute_handler(request)

if __name__ == "__main__":
    # Load SSL certificate and key
    ssl_context = ("cert.pem", "key.pem")
    app.run(debug=True, ssl_context=ssl_context)
