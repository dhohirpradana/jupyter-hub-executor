from execute import handler as execute_handler
from flask_cors import CORS
from sys import stderr
import os
from flask import Flask, request, jsonify

# List of required environment variables
required_env_vars = ["JUPYTERHUB_URL",
                     "JUPYTERHUB_WS", "JUPYTERHUB_TOKEN", "ELASTIC_URL"]
# raise EnvironmentError(f"Required environment variable {env_var} is not set.")


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def hello_geek():
    return '<h1>Hello from jupyterhub executor</h1>'


@app.route('/execute', methods=['POST'])
def api_endpoint():
    # Check if all required environment variables are set
    for env_var in required_env_vars:
        if env_var not in os.environ:
            return jsonify({"message": f"Required environment variable {env_var} is not set."})

    return execute_handler(request)


if __name__ == "__main__":
    # Load SSL certificate and key
    ssl_context = ("cert.pem", "key.pem")
    app.run(debug=True, ssl_context=ssl_context)
