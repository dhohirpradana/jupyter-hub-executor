import requests
import os
from pb_token import token_get as token_handler
from flask import jsonify
from datetime import datetime
from croniter import croniter

scheduler_url = os.environ.get('PB_SCHEDULER_URL')


def scheduler_update(id, status, last_run, cron_expression):
    print("update scheduler")
    token = token_handler()
    if token_handler == "":
        return jsonify({"message": "Error get pb token!"}), 500

    if not cron_expression:
        data = {
            "lastRun": str(last_run),
            "status": status,
        }
    else:
        cron = croniter(cron_expression, last_run)

        next_run = cron.get_next(datetime)
        print("Next run time:", next_run)
        
        data = {
            "lastRun": str(last_run),
            "nextRun": str(next_run),
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
