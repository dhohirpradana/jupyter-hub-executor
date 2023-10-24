import requests
import os
from datetime import datetime

jupyterhub_url = os.environ.get('JUPYTERHUB_URL')
token = os.environ.get('JUPYTERHUB_TOKEN')


def restart(kernel, user):
    now = datetime.now()
    url = f"{jupyterhub_url}/user/{user}/api/kernels/{kernel}/restart?{now}"

    try:
        r = requests.post(url, headers={
            'Authorization': f'token {token}'}, json={})
        r.raise_for_status()

        response = r.json()
        print("Restart kernel:", response)
    except Exception as e:
        print(str(e))
