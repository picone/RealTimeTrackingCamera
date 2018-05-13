# -*- coding: utf-8 -*-
import asyncio
import cv2

from controllers.base_controller import BaseController
from message import request_pb2
from message import response_pb2
from utils.camera import Camera
from utils.image_utils import ImageUtils
from utils.moving_target_track import MovingTargetTrack
from websockets import ConnectionClosed


class Track(BaseController):
    def __init__(self):
        self.__capture = False
        self.__target = None
        self.__tracker = None
        self.__mask = None

    async def execute(self, websocket):
        response = await websocket.recv()
        command = request_pb2.CommandRequest()
        command.ParseFromString(response)
        self.__target = ImageUtils.bytes2img(command.frame)
        self.__mask = ImageUtils.bytes2img(command.mask)
        self.__tracker = MovingTargetTrack(self.__target, self.__mask)
        if command.code == 2:
            self.__capture = True
            await asyncio.wait([
                asyncio.ensure_future(self._send_frame(websocket)),
                asyncio.ensure_future(self._wait_stop(websocket)),
            ])

    async def _send_frame(self, websocket):
        response = response_pb2.FrameResponse()
        response.code = 1
        response.type = response_pb2.FrameResponse.VIDEO
        while self.__capture:
            ret, img = Camera.get_frame()
            if ret:
                old_position, new_position, points = self.__tracker.track(img)
                response.position_x = new_position.x
                response.position_y = new_position.y
                response.points_count = len(points)
                # 把轮廓绘制到帧上
                if response.points_count > 0:
                    ImageUtils.draw_points(img, points, 6, (0, 0, 255))
                # 把质心绘制到帧上
                ImageUtils.draw_points(img, [(int(new_position.x), int(new_position.y))], 6, (0, 255, 0))
                response.frame = ImageUtils.img2bytes(img)
                try:
                    await websocket.send(response.SerializeToString())
                except ConnectionClosed:
                    self.__capture = False
            await asyncio.sleep(1 / 100)  # 要加个sleep，不然无法让其他协程运行

    async def _wait_stop(self, websocket):
        try:
            response = await websocket.recv()
            command = request_pb2.CommandRequest()
            command.ParseFromString(response)
            if command.code == 1:
                self.__capture = False
        except ConnectionClosed:
            print("Connection has closed")
