import requests
import os
from pb_token import token_get as token_handler
from flask import jsonify

scheduler_url = os.environ.get('PB_SCHEDULER_URL')


def scheduler_update(id, status, last_run):
    print("update scheduler")
    token = token_handler()
    if token_handler == "":
        return jsonify({"message": "Error get pb token!"}), 500
    # lastRun

    data = {
        "lastRun": str(last_run),
        "status": status,
    }
    
    url = scheduler_url + f'/{id}'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    print("url", url)
    print("headers", headers)
    print("data", data)

    try:
        r = requests.patch(url,
                           headers=headers, json=data)

        r.raise_for_status()
        print("Update scheduler successfully", r.json())
    except Exception as e:
        print("Update scheduler unsuccess!")
        print(e)
