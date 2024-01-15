import requests
import os
from pb_token import token_get as token_handler
from flask import jsonify
from datetime import datetime
from croniter import croniter

scheduler_url = os.environ.get('PB_SCHEDULER_URL')
notification_url = os.environ.get('PB_NOTIFICATION_URL')

def scheduler_update(id, status, last_run, pb_last_run, cron_expression):
    print("update scheduler")
    
    # set last_run second to 0
    # last_run = last_run.replace(second=0)
    now_time = last_run
    
    # change now_time to timestamp
    now_time = now_time.timestamp()
    
    # validate last_run null
    if pb_last_run == None or pb_last_run == "":
        pb_last_run = now_time
    
    print({
        "id": id,
        "status": status,
        "pb_last_run": pb_last_run,
        "cron_expression": cron_expression
    })
    
    token = token_handler()
    if token == "":
        # return jsonify({"message": "Error get pb token!"}), 500
        print("Error get pb token!")

    if cron_expression == False:
        data = {
            "lastRun": str(last_run),
            "status": status,
        }
    else:
        # pb_last_run = pb_last_run.strptime(pb_last_run, '%Y-%m-%d %H:%M:%S.%fZ')
        
        # pb lastrun set second to 0
        # pb_last_run = pb_last_run.replace(second=0)
        
        # Create a croniter object
        cron = croniter(cron_expression, pb_last_run)

        # Get the next run time after the current time
        # next_run = cron.get_next(datetime)
        next_run = "-"
        # while next_run < now_time:
        #     cron = croniter(cron_expression, next_run)
        #     next_run = cron.get_next(datetime)
            
        print("Next run time:", next_run)
        
        data = {
            "lastRun": str(last_run),
            # "nextRun": str(next_run),
            "nextRun": str(next_run.timestamp()),
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
    print({
        "scheduler": scheduler,
        "type": type,
        "status": status,
        "msg": msg,
        "is_cron": is_cron,
        "user": user
    })
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