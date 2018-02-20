# -*- coding: utf-8 -*-
import cv2
import unittest
from utils.moving_target_outline import MovingTargetOutline


class TestMovingTargetOutline(unittest.TestCase):

    def setUp(self):
        cap = cv2.VideoCapture("demo.avi")
        if cap is None or not cap.isOpened():
            self.fail("demo.avi不存在")
        self.__cap = cap

    def test_get_max_difference_frame(self):
        outline = MovingTargetOutline()
        while True:
            ret, img = self.__cap.read()
            if not ret:
                break
            outline.add_frame(img)
        max_difference_frame = outline.get_max_difference_frame()
        self.assertIsNotNone(max_difference_frame)
