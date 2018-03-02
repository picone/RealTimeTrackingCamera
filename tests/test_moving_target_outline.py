# -*- coding: utf-8 -*-
import cv2
import unittest
from utils.moving_target_outline import MovingTargetOutline


class TestMovingTargetOutline(unittest.TestCase):

    def setUp(self):
        cap = cv2.VideoCapture(0)
        if cap is None or not cap.isOpened():
            self.fail("启动摄像头失败")
        self.__cap = cap

    def test_get_max_difference_frame(self):
        outline = MovingTargetOutline()
        for i in range(1, 5):
            ret, img = self.__cap.read()
            if not ret:
                break
            outline.add_frame(img)
        max_difference_frame = outline.get_max_difference_frame()
        self.assertIsNotNone(max_difference_frame)
