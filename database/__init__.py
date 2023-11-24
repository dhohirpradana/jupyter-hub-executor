import requests
import os
from pb_token import token_get as token_handler
from flask import jsonify
from datetime import datetime
from croniter import croniter

scheduler_url = os.environ.get('PB_SCHEDULER_URL')
notification_url = os.environ.get('PB_NOTIFICATION_URL')

def scheduler_update(id, status, last_run, cron_expression):
    print("update scheduler")
    token = token_handler()
    if token_handler == "":
        # return jsonify({"message": "Error get pb token!"}), 500
        print("Error get pb token!")

    if not cron_expression:
        cron = croniter(cron_expression, last_run)

        next_run = cron.get_next(datetime)
        print("Next run time:", next_run)
        
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

def notification_create(scheduler, type, status, msg, is_cron, user):
    print("create notification")
    token = token_handler()
    if token_handler == "":
        # return jsonify({"message": "Error get pb token!"}), 500
        print("Error get pb token!")
        
    url = notification_url
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    try:
        r = requests.post(url,
                          headers=headers, json={
                              "scheduler": scheduler,
                              "type": type,
                              "status": status,
                              "message": msg,
                              "isCron": is_cron,
                              "user": user
                          })

        r.raise_for_status()
        print("Create notification successfully", r.json())
    except Exception as e:
        print("Create notification unsuccess!")
        print(e)