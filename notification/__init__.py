import os
import requests

event_url = os.environ.get('EVENT_URL')

from database import notification_create as notification_create_handler

def send_event(event, event_data, email, cx, scheduler_id):
    print({
        "event": event,
        "email": email,
        "event-data": event_data,
        "cx": cx,
        "scheduler_id": scheduler_id
    })

    try:
        r = requests.post(event_url,
                            json={
                                "event": event,
                                "email": email,
                                "event-data": event_data
                            }, verify=False
                            )
    
        r.raise_for_status()
        print("Send event successfully")
    except Exception as e:
        print(str(e))
        
    if cx and (event == "sjduler-finish" or event == "sjduler-error"):
        notification_create_handler(scheduler_id, "scheduler", "success" if event == "scheduler-finish" else "failed", event_data["msg"], True)
    elif event == "sjduler-finish" or event == "sjduler-error":
        notification_create_handler(scheduler_id, "scheduler", "success" if event == "scheduler-finish" else "failed",  event_data["msg"], False)