import requests
import os
from datetime import datetime

def restart(kernel, api_url, token):
    now = datetime.now()
    url = f"{api_url}/kernels/{kernel}/restart?{now}"

    try:
        r = requests.post(url, headers={
            'Authorization': f'token {token}'}, json={})
        r.raise_for_status()

        response = r.json()
        print("Restart kernel:", response)
    except Exception as e:
        print(str(e))
