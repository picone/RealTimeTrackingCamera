# -*- coding: utf-8 -*-
import asyncio
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers import base as scheduler_base
from controllers.base_controller import BaseController
from message import request_pb2
from message import response_pb2
from utils.camera import Camera
from utils.image_utils import ImageUtils
from utils.moving_target_outline import MovingTargetOutline


class Detect(BaseController):
    __capture_scheduler = AsyncIOScheduler()

    def __init__(self):
        self.__outline = MovingTargetOutline()
        self.__is_capturing = False
        self.__capture_job_id = str(uuid.uuid1())
        if self.__capture_scheduler.state == scheduler_base.STATE_STOPPED:
            self.__capture_scheduler.start()

    async def execute(self, websocket):
        self.__capture_scheduler.add_job(
            self._capture, 'interval', [websocket], id=self.__capture_job_id, max_instances=3, seconds=1/7)
        await asyncio.wait([
            asyncio.ensure_future(self._wait_stop(websocket)),
        ])
        # 直到收到停止命令
        background, max_difference_frame = self.__outline.get_max_difference_frame()
        response_frame = response_pb2.FrameResponse()
        response_frame.code = 1
        response_frame.type = response_pb2.FrameResponse.OUTLINE
        response_frame.frame = ImageUtils.img2bytes(max_difference_frame)
        await websocket.send(response_frame.SerializeToString())
        response_frame.type = response_pb2.FrameResponse.BACKGROUND
        response_frame.frame = ImageUtils.img2bytes(background)
        await websocket.send(response_frame.SerializeToString())

    async def _capture(self, websocket):
        response_frame = response_pb2.FrameResponse()
        response_frame.code = 1
        response_frame.type = response_pb2.FrameResponse.VIDEO
        ret, img = Camera.get_frame()
        if ret:
            response_frame.frame = ImageUtils.img2bytes(img)
            await websocket.send(response_frame.SerializeToString())
            self.__outline.add_frame(img)

    async def _wait_stop(self, websocket):
        response = await websocket.recv()
        command = request_pb2.CommandRequest()
        command.ParseFromString(response)
        if command.code == 1:
            self.__capture_scheduler.remove_job(self.__capture_job_id)
