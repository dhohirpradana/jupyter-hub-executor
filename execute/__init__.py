import websockets
import json
import uuid
from datetime import datetime
import requests
import asyncio
from flask import jsonify
import os

jupyterhub_url = os.environ.get('JUPYTERHUB_URL')
jupyterhub_ws = os.environ.get('JUPYTERHUB_WS')
token = os.environ.get('JUPYTERHUB_TOKEN')
kernel = os.environ.get('JUPYTERHUB_KERNEL')

api_url = f"{jupyterhub_url}/hub/api"

async def execute(index, username, cell_source):
    uuid4 = uuid.uuid4()
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    uri = f"{jupyterhub_ws}/user/{username}/api/kernels/{kernel}/channels?session_id={uuid4}&token={token}"
    print("uri", uri)

    async with websockets.connect(uri) as websocket:
        message = {
            "header": {
                "date": f"{formatted_date}",
                "msg_id": f"{index}",
                "msg_type": "scheduled_execute",
                "session": f"{uuid4}",
                "username": f"{username}",
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
                "code": f"{cell_source}",
                "silent": False,
                "store_history": True,
                "user_expressions": {},
                "allow_stdin": True,
                "stop_on_error": False
            },
            "buffers": []
        }

        message_json = json.dumps(message)
        await websocket.send(message_json)

        # Receive a response if needed
        response = await websocket.recv()

        print(f"Received response: {response}")

# asyncio.get_event_loop().run_until_complete(handler())


def handler(request):
    if jupyterhub_url is None:
        return jsonify({"message": "JUPYTERHUB_URL is required!"})

    if jupyterhub_ws is None:
        return jsonify({"message": "JUPYTERHUB_WS is required!"})

    if token is None:
        return jsonify({"message": "JUPYTERHUB_TOKEN is required!"})

    if kernel is None:
        return jsonify({"message": "JUPYTERHUB_KERNEL is required!"})

    body = request.get_json()
    
    if body is None:
        return jsonify({"message": "Request body is required!"}), 400

    if "user" not in body:
        return jsonify({"message": "user is required!"}), 400
    
    if "notebook-name" not in body:
        return jsonify({"message": "notebook-name is required!"}), 400
    
    user = body["user"]
    notebook_name = body["notebook-name"]
    
    if user is None:
        return jsonify({"message": "user is required!"}), 400

    if notebook_name is None:
        return jsonify({"message": "notebook-name is required!"}), 400

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

                cells = response['content']['cells']
                # print(cells)

                for index, cell in enumerate(cells):
                    cell_source = cell['source']
                    cell_type = cell['cell_type']
                    
                    print("cell_type", cell_type)

                    if cell_type == "code":
                        async def execute():
                            await execute(index, user, cell_source)

                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(execute())
                    else:
                        pass

                return jsonify({"message": "Finished"}), 200

            except Exception as e:
                print(str(e))
                return jsonify({"message": str(e)}), 400

        except Exception as e:
            print(str(e))
            return jsonify({"message": str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({"message": str(e)}), 400
