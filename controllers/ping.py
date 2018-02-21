# -*- coding: utf-8 -*-
from controllers.base_controller import BaseController


class Ping(BaseController):

    @classmethod
    async def execute(cls, websocket):
        await websocket.send("pong")
