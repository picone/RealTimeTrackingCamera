# -*- coding: utf-8 -*-
import json
import threading
import cv2
from controllers.base_controller import BaseController
from utils.moving_target_outline import MovingTargetOutline
from utils.response import Response


class Detect(BaseController):

    def __init__(self):
        self.__outline = MovingTargetOutline()
        self.__is_capturing = False

    async def execute(self, websocket):
        try:
            thread = threading.Thread(target=self._capture)
            self.__is_capturing = True
            thread.start()
            response = await websocket.recv()
            response = json.loads(response)
            if response["cmd"] == "stop":
                self.__is_capturing = False
                max_difference_frame = self.__outline.get_max_difference_frame()
                await websocket.send(Response.get(1, {"outline": max_difference_frame.tolist()}))
        except json.decoder.JSONDecodeError:
            await websocket.send(Response.get(10))

    def _capture(self):
        # TODO 接入摄像头
        cap = cv2.VideoCapture("demo.avi")
        while self.__is_capturing:
            ret, img = cap.read()
            if not ret:
                break
            self.__outline.add_frame(img)
