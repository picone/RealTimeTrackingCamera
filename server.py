# -*- coding: utf-8 -*-
import asyncio
import websockets
from utils.response import Response


async def websocket_handler(websocket, path):
    """
    实现websocket命令路由
    """
    path = str(path[1:]).split("/")
    if len(path) == 1:
        path.append("execute")
    try:
        controller = __import__("controllers." + path[0], fromlist=True)
        class_name = str(path[0]).capitalize()
        if hasattr(controller, class_name):
            class_name = getattr(controller, class_name)
            if not hasattr(class_name, path[1]):
                raise ModuleNotFoundError()
        else:
            raise ModuleNotFoundError()
        await class_name.execute(websocket)
    except ModuleNotFoundError:
        await websocket.send(Response.get(12))

start_server = websockets.serve(websocket_handler, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
