# -*- coding: utf-8 -*-
from controllers.base_controller import BaseController


class Ping(BaseController):

    async def execute(self, websocket):
        await websocket.send("pong")
