import os
import requests

event_url = os.environ.get('EVENT_URL')

from database import notification_create as notification_create_handler

async def send_event(event, event_data, email, cx, scheduler_id):
    status = None
    if event == "scheduler-error":
        status = "failed"
        
    elif event == "scheduler-finish":
        status = "success"

    try:
        r = requests.post(event_url,
                            json={
                                "event": event,
                                "email": email,
                                "event-data": event_data
                            }
                            )
    
        r.raise_for_status()
        print("Send event successfully")
    except Exception as e:
        print(str(e))
        
    if cx and status:
        notification_create_handler(scheduler_id, "scheduler", status)
    else:
        print("Not cron job or status is None")