# -*- coding: utf-8 -*-
import asyncio
import cv2

from controllers.base_controller import BaseController
from message import request_pb2
from message import response_pb2
from utils.camera import Camera
from utils.image_utils import ImageUtils
from utils.moving_target_outline import MovingTargetOutline
from websockets import ConnectionClosed


class Detect(BaseController):

    def __init__(self):
        self.__outline = MovingTargetOutline()
        self.__is_capturing = False

    async def execute(self, websocket):
        self.__is_capturing = True
        await asyncio.wait([
            asyncio.ensure_future(self._capture(websocket)),
            asyncio.ensure_future(self._wait_stop(websocket)),
        ])
        # 直到收到停止命令
        background, max_difference_frame = self.__outline.get_max_difference_frame()
        if max_difference_frame is not None:
            response_frame = response_pb2.FrameResponse()
            response_frame.code = 1
            response_frame.type = response_pb2.FrameResponse.OUTLINE
            # 进行开运算连接孤立点
            max_difference_frame = ImageUtils.morphology(max_difference_frame, cv2.MORPH_OPEN, 3)
            response_frame.frame = ImageUtils.img2bytes(max_difference_frame)
            await websocket.send(response_frame.SerializeToString())
            response_frame.type = response_pb2.FrameResponse.BACKGROUND
            response_frame.frame = ImageUtils.img2bytes(background)
            await websocket.send(response_frame.SerializeToString())

    async def _capture(self, websocket):
        response_frame = response_pb2.FrameResponse()
        response_frame.code = 1
        response_frame.type = response_pb2.FrameResponse.VIDEO
        while self.__is_capturing:
            ret, img = Camera.get_frame()
            if ret:
                response_frame.frame = ImageUtils.img2bytes(img)
                try:
                    await websocket.send(response_frame.SerializeToString())
                except ConnectionClosed:
                    self.__is_capturing = False
                self.__outline.add_frame(img)
            await asyncio.sleep(1 / 10)

    async def _wait_stop(self, websocket):
        try:
            response = await websocket.recv()
            command = request_pb2.CommandRequest()
            command.ParseFromString(response)
            if command.code == 1:
                self.__is_capturing = False
        except ConnectionClosed:
            self.__is_capturing = False
