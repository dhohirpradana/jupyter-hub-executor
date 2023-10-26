import requests
import os
from pb_token import token_get as token_handler
from flask import jsonify

scheduler_url = os.environ.get('SCHEDULER_URL')


def scheduler_update(id, status, last_run):
    token = token_handler()
    if token_handler == "":
        return jsonify({"message": "Error get pb token!"}), 500
    # lastRun

    data = {
        "lastRun": last_run,
        "status": status,
    }

    try:
        r = requests.patch(scheduler_url + f'/{id}',
                           headers={
                               'Authorization': f'Bearer {token}',
                           }, json=data)

        r.raise_for_status()
        print("Update scheduler successfully", r.json())
    except Exception as e:
        print("Update scheduler unsuccess!")
        print(str(e))
