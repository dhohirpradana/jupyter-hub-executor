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
from database import scheduler_update as scheduler_update_handler
from notification import send_event as send_event_handler
from pb_token import token_get as token_handler

from kernel import restart as restart_kernel

jupyter_url_env = os.environ.get('JUPYTER_URL')
jupyter_ws_env = os.environ.get('JUPYTER_WS')
# token = os.environ.get('JUPYTER_TOKEN')

# api_url = f"{jupyter_url}/api"

async def execute_ws(index, cell_source, kernel, token, jupyter_ws, api_url):
    uuid4 = uuid.uuid4()
    msg_id = uuid.uuid4()
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    uri = f"{jupyter_ws}/api/kernels/{kernel}/channels?session_id={uuid4}&token={token}"
    # print("uri", uri)

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
                restart_kernel(kernel, api_url, token)
                return {'status': 'error', 'msg': 'input promt:'}

            if msg_state == 'error':
                err_msg = content['traceback']
                # print(err_msg)
                return {'status': 'error', 'msg': err_msg}

            if 'status' in content:
                # print(content['status'])
                status = content['status']
                return {'status': status, 'msg': content['traceback'] if status == 'error' else 'Success'}
                # asyncio.get_event_loop().run_until_complete(handler())


def handler(request):
    body = request.get_json()
    cron_param = request.args.get('cron')
    port = request.args.get('port')
    token = request.args.get('token')
    last_run = datetime.now()
    if cron_param == "1":
        cx = True
    else:
        cx = False
        
    if port is None or port == "":
        return jsonify({"message": "Port is required!"}), 400
    
    jupyter_url = f"{jupyter_url_env}:{port}"
    api_url = f"{jupyter_url}/api"
    jupyter_ws = f"{jupyter_ws_env}:{port}"
    
    if token is None or token == "":
        return jsonify({"message": "Token is required!"}), 400

    if body is None:
        return jsonify({"message": "Request body is required!"}), 400
    
    if cx:
        if "cron-expression" not in body:
            cron_expression = False
            return jsonify({"message": "cron-expression is required!"}), 400
        else:
            cron_expression = body["cron-expression"]
    else:
        cron_expression = False

    if "scheduler-id" not in body:
        return jsonify({"message": "scheduler-id is required!"}), 400

    scheduler_id = body["scheduler-id"]

    if scheduler_id is None:
        return jsonify({"message": "scheduler-id is required!"}), 400
    
    
    
    # get detail scheduler
    try:
        pb_token = token_handler()
        print("token", token)
        if pb_token == "":
            return jsonify({"message": "Error get pb token!"}), 500
        r = requests.get(f"{os.environ.get('PB_SCHEDULER_URL')}/{scheduler_id}",
                         headers={
                             "Authorization": f"Bearer {pb_token}"
                         }
        )
        r.raise_for_status()
        scheduler = r.json()
        # print("scheduler", scheduler)
        pb_user = scheduler["user"]
        # print("user", pb_user)
        email = pb_user
        
        # get detail user
        try:
            r = requests.get(f"{os.environ.get('PB_USER_URL')}/{pb_user}",
                            headers={
                                "Authorization": f"Bearer {pb_token}"
                            }
            )
            r.raise_for_status()
            res = r.json()
            
            pb_last_run = scheduler["lastRun"]
            path = scheduler["pathNotebook"]
            
            # validate path
            if path is None or path == "":
                return jsonify({"message": "pathNotebook is None!"}), 400
            
            if email is None or email == "":
                print("Email is None")

            try:
                notebooks_url = f'{api_url}/contents'
                r = requests.get(notebooks_url, headers={
                    'Authorization': f'token {token}'})
                r.raise_for_status()
                notebooks = r.json()

                # print(notebooks)

                try:
                    execute_url = f'{api_url}/contents/{path}'
                    r = requests.get(execute_url, headers={
                        'Authorization': f'token {token}'}, json={})
                    r.raise_for_status()

                    response = r.json()
                    # print(response)

                    now = datetime.now()

                    try:
                        sessions_uri = f"{api_url}/sessions?{now}"
                        # print(sessions_uri)

                        rr = requests.get(sessions_uri, headers={
                            'Authorization': f'token {token}'}, json={})
                        rr.raise_for_status()

                        responser = rr.json()
                        # print(responser)

                        if not len(responser):
                            send_event_handler("sjduler-error", {"msg": "Unable get sessions!, no sessions!"}, email, cx, scheduler_id)
                            return jsonify({"message": "Unable get sessions!, no sessions!"}), 400

                        kernel_ids = [item["kernel"]["id"]
                                    for item in responser if item["path"] == path]
                        # print(kernel_ids)

                        if not len(kernel_ids):
                            send_event_handler("sjduler-error", {"msg": "Unable get sessions!, no kernels!"}, email, cx, scheduler_id)
                            return jsonify({"message": "Unable get sessions!, no kernels!"}), 400
                        else:
                            kernel = kernel_ids[0]

                    except Exception as e:
                        send_event_handler("sjduler-error", {"msg": "Unable get sessions!"}, email, cx, scheduler_id)
                        return jsonify({"message": "Unable get sessions!"}), 400

                    try:
                        cells = response['content']['cells']
                        # print(cells)

                        results = []

                        for index, cell in enumerate(cells):
                            cell_source = cell['source']
                            cell_type = cell['cell_type']

                            # print("cell_type", cell_type)

                            if cell_type == "code" and cell_source:
                                # print(cell_source)

                                async def abc():
                                    res = await execute_ws(index, cell_source, kernel, token, jupyter_ws, api_url)
                                    # print(res)
                                    results.append(
                                        {'cell': index + 1, "cell_type": cell_type, "cell-value": cell_source, **res})
                                asyncio.run(abc())
                            else:
                                results.append(
                                    {'cell': index + 1, "cell_type": cell_type, "cell-value": cell_source, "status": "ok", "msg": "Success"})

                            if results[-1]['status'] == 'error':
                                break

                        # print(results)
                        count_ok = 0
                        count_error = 0
                        count = len(cells)

                        for result in results:
                            if result['status'] == 'Success':
                                count_ok += 1
                            elif result['status'] == 'error':
                                count_error += 1
                        
                        elastic_handler(
                            {"path": path, "scheduler_id": scheduler_id, "date": f"{last_run}", "results": json.dumps(
                                results, indent=4, sort_keys=True, default=str), "sucsess": count_ok, "error": count_error, "executed": len(results), "unexecuted": count-len(results)})
                        status = "success" if count_error == 0 else "failed"
                        
                        scheduler_update_handler(scheduler_id, status, last_run, pb_last_run, cron_expression)
                        
                        msg = "Scheduler finish" if count_error == 0 else "Scheduler error"
                        
                        send_event_handler("sjduler-finish", {"msg": msg}, email, cx, scheduler_id)
                        return jsonify({"path": path, "message": "Finished", "sucsess": count_ok, "error": count_error, "executed": len(results), "unexecuted": count-len(results), "total": count, "results": results}), 200
                    except Exception as e:
                        print("Error get cells")
                        # get error location
                        print(e.__traceback__.tb_lineno)
                        print(str(e))
                        send_event_handler("sjduler-error", {"msg": f'Error get cells {str(e)}'}, email, cx, scheduler_id)
                        return jsonify({"message": str(e)}), 400
                    
                except Exception as e:
                    print("Error get execute")
                    print(str(e))
                    send_event_handler("sjduler-error", {"msg": f'{str(e)}'}, email, cx, scheduler_id)
                    return jsonify({"message": str(e)}), 400

            except Exception as e:
                print("Error get notebooks")
                print(str(e))
                send_event_handler("sjduler-error", {"msg": f'{str(e)}'}, email, cx, scheduler_id)
                return jsonify({"message": str(e)}), 400
            
        except Exception as e:
            print("Error get detail pb user!")
            print(str(e))
            return jsonify({"message": str(e)}), 400
        
    except Exception as e:
        print("Error get detail scheduler")
        print(str(e))
        return jsonify({"message": str(e)}), 400

