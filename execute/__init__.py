import websockets
import json
import uuid
from datetime import datetime
import time
import requests
import asyncio
from flask import jsonify
import os
from solr import handler as solr_handler
from elastic import handler as elastic_handler

from kernel import restart as restart_kernel

jupyterhub_url = os.environ.get('JUPYTERHUB_URL')
jupyterhub_ws = os.environ.get('JUPYTERHUB_WS')
token = os.environ.get('JUPYTERHUB_TOKEN')

api_url = f"{jupyterhub_url}/hub/api"


async def execute_ws(index, username, cell_source, kernel):
    uuid4 = uuid.uuid4()
    msg_id = uuid.uuid4()
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    uri = f"{jupyterhub_ws}/user/{username}/api/kernels/{kernel}/channels?session_id={uuid4}&token={token}"
    print("uri", uri)

    message = {
        "header": {
            "date": formatted_date,
            "msg_id": f"{msg_id}",
            "msg_type": "execute_request",
            "session": f"{uuid4}",
            "username": "",
            "version": "5.2"
        },
        "parent_header": {},
        "metadata": {
            "editable": True,
            "slideshow": {
                "slide_type": ""
            },
            "tags": [],
            "trusted": True,
            "deletedCells": [],
            "recordTiming": False
        },
        "content": {
            "code": cell_source,
            "silent": False,
            "store_history": True,
            "user_expressions": {},
            "allow_stdin": True,
            "stop_on_error": True
        },
        "buffers": []
    }

    # print(message)
    message_json = json.dumps(message)
    # print(message_json)

    async with websockets.connect(uri) as websocket:
        await websocket.send(message_json)
        # print(f"Sent: {message_json}")

        # Subscribe to incoming messages
        while True:
            response = await websocket.recv()
            response_json = json.loads(response)
            content = response_json['content']
            msg_state = response_json["header"]["msg_type"]
            # print("Msg type:", msg_state)
            # print("Response", response)
            # print("Content", content)

            if msg_state == 'input_request':
                restart_kernel(kernel, username)
                return {'status': 'error', 'msg': 'input promt:'}

            if msg_state == 'error':
                err_msg = content['traceback']
                # print(err_msg)
                return {'status': 'error', 'msg': err_msg}

            if 'status' in content:
                # print(content['status'])
                status = content['status']
                return {'status': status, 'msg': content['traceback'] if status == 'error' else 'ok'}
                # asyncio.get_event_loop().run_until_complete(handler())


def handler(request):
    if jupyterhub_url is None:
        return jsonify({"message": "JUPYTERHUB_URL is required!"})

    if jupyterhub_ws is None:
        return jsonify({"message": "JUPYTERHUB_WS is required!"})

    if token is None:
        return jsonify({"message": "JUPYTERHUB_TOKEN is required!"})

    body = request.get_json()

    if body is None:
        return jsonify({"message": "Request body is required!"}), 400

    if "user" not in body:
        return jsonify({"message": "user is required!"}), 400

    if "notebook-name" not in body:
        return jsonify({"message": "notebook-name is required!"}), 400

    if "scheduler-id" not in body:
        return jsonify({"message": "scheduler-id is required!"}), 400

    user = body["user"]
    notebook_name = body["notebook-name"]
    scheduler_id = body["scheduler-id"]

    if user is None:
        return jsonify({"message": "user is required!"}), 400

    if notebook_name is None:
        return jsonify({"message": "notebook-name is required!"}), 400

    if scheduler_id is None:
        return jsonify({"message": "scheduler-id is required!"}), 400

    try:
        r = requests.get(api_url + '/users',
                         headers={
                             'Authorization': f'token {token}',
                         }
                         )

        r.raise_for_status()
        users = r.json()

        try:
            notebooks_url = f'{jupyterhub_url}/user/{user}/api/contents'
            r = requests.get(notebooks_url, headers={
                'Authorization': f'token {token}'})
            r.raise_for_status()
            notebooks = r.json()

            # print(notebooks)

            try:
                execute_url = f'{jupyterhub_url}/user/{user}/api/contents/{notebook_name}'
                r = requests.get(execute_url, headers={
                    'Authorization': f'token {token}'}, json={})
                r.raise_for_status()

                response = r.json()
                # print(response)

                now = datetime.now()

                try:
                    sessions_uri = f"{jupyterhub_url}/user/{user}/api/sessions?{now}"
                    # print(sessions_uri)

                    rr = requests.get(sessions_uri, headers={
                        'Authorization': f'token {token}'}, json={})
                    rr.raise_for_status()

                    responser = rr.json()
                    # print(responser)

                    if not len(responser):
                        return jsonify({"message": "Unable get sessions!, no sessions!"}), 400

                    kernel_ids = [item["kernel"]["id"]
                                  for item in responser if item["path"] == notebook_name]
                    print(kernel_ids)

                    if not len(kernel_ids):
                        return jsonify({"message": "Unable get sessions!, no kernels!"}), 400
                    else:
                        kernel = kernel_ids[0]

                except Exception as e:
                    return jsonify({"message": "Unable get sessions!"}), 400

                cells = response['content']['cells']
                # print(cells)

                results = []

                for index, cell in enumerate(cells):
                    cell_source = cell['source']
                    cell_type = cell['cell_type']

                    # print("cell_type", cell_type)

                    if cell_type == "code":
                        # print(cell_source)

                        async def abc():
                            res = await execute_ws(index, user, cell_source, kernel)
                            print(res)
                            results.append({'cell': index + 1, **res})
                        asyncio.run(abc())
                    else:
                        if index+1 != len(cells):
                            pass
                        else:
                            elastic_handler(
                                {"scheduler_id": scheduler_id, "date": f"{datetime.now()}", "results": json.dumps(
                                    results, indent=4, sort_keys=True, default=str)})
                            return jsonify({"message": "Finished", "total": len(cells), "results": results}), 200

                    if results[-1]['status'] == 'error':
                        break

                elastic_handler(
                    {"scheduler_id": scheduler_id, "date": f"{datetime.now()}", "results": json.dumps(
                        results, indent=4, sort_keys=True, default=str)})
                return jsonify({"message": "Finished", "total": len(cells), "results": results}), 200

            except Exception as e:
                print(str(e))
                return jsonify({"message": str(e)}), 400

        except Exception as e:
            print(str(e))
            return jsonify({"message": str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({"message": str(e)}), 400
