import requests
import os
pb_login_url = os.environ.get('PB_LOGIN_URL')
pb_mail = os.environ.get('PB_MAIL')
pb_password = os.environ.get('PB_PASSWORD')


def token_get():
    # lastRun
    try:
        r = requests.post(pb_login_url,
                          json={
                              "identity": pb_mail,
                              "password": pb_password
                          }
                          )

        r.raise_for_status()
        data = r.json()
        token = data["token"]
        print(token)
        return token
    except Exception as e:
        print(str(e))
        return ""
