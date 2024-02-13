from execute import handler as execute_handler
from flask_cors import CORS
from sys import stderr
import os

from flask import Flask, request, jsonify
from pb_token import token_get as token_handler

# List of required environment variables
required_env_vars = ["JUPYTER_URL",
                     "JUPYTER_WS", "JUPYTER_TOKEN", "ELASTIC_URL", "PB_LOGIN_URL", "PB_MAIL", "PB_PASSWORD", "PB_SCHEDULER_URL", "EVENT_URL"]

def validate_envs():
    for env_var in required_env_vars:
        if env_var not in os.environ:
            raise EnvironmentError(
                f"Required environment variable {env_var} is not set.")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_geek():
    return '<h1>Hello from jupyter executor</h1>'

@app.route('/execute', methods=['POST'])
def api_endpoint():
    validate_envs()
    return execute_handler(request)

if __name__ == "__main__":
    # Load SSL certificate and key
    # ssl_context = ("cert.pem", "key.pem")
    app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(debug=True, ssl_context=ssl_context)
