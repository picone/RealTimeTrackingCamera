# -*- coding: utf-8 -*-
import cv2
import unittest

from utils.image_utils import ImageUtils


class TestImageFilter(unittest.TestCase):

    def setUp(self):
        self.__image = cv2.imread("result/gaussian_1.jpg")
        if self.__image is None:
            self.fail("读取样本失败")

    def test_dilate(self):
        """
        膨胀
        """
        ret = ImageUtils.morphology(self.__image, cv2.MORPH_DILATE, 2)
        _, ret = ImageUtils.binary(ret, threshold_type=cv2.THRESH_OTSU)
        cv2.imwrite("result/dilate.jpg", ret)

    def test_erode(self):
        """
        腐蚀
        """
        ret = ImageUtils.morphology(self.__image, cv2.MORPH_ERODE, 2)
        _, ret = ImageUtils.binary(ret, threshold_type=cv2.THRESH_OTSU)
        cv2.imwrite("result/erode.jpg", ret)

    def test_close(self):
        """
        闭运算
        """
        ret = ImageUtils.morphology(self.__image, cv2.MORPH_CLOSE, 8)
        _, ret = ImageUtils.binary(ret, threshold_type=cv2.THRESH_OTSU)
        cv2.imwrite("result/close.jpg", ret)
