# -*- coding: utf-8 -*-
import cv2
import unittest

from utils.image_utils import ImageUtils


class TestImageFilter(unittest.TestCase):

    def setUp(self):
        self.__image = cv2.imread("outputs/1_0.jpg")
        if self.__image is None:
            self.fail("读取样本失败")
        _, img = ImageUtils.binary(self.__image, threshold_type=cv2.THRESH_OTSU)
        cv2.imwrite("result/origin.jpg", img)

    def test_median_blur(self):
        """
        中值滤波
        """
        ret = cv2.medianBlur(self.__image, 1)
        cv2.imwrite("result/median_0.jpg", ret)
        _, ret = ImageUtils.binary(ret, threshold_type=cv2.THRESH_OTSU)
        cv2.imwrite("result/median_1.jpg", ret)

    def test_gaussian_blur(self):
        """
        高斯滤波
        """
        ret = cv2.GaussianBlur(self.__image, (3, 3), 0.8)
        cv2.imwrite("result/gaussian_0.jpg", ret)
        _, ret = ImageUtils.binary(ret, threshold_type=cv2.THRESH_OTSU)
        cv2.imwrite("result/gaussian_1.jpg", ret)

    def test_mean_blur(self):
        """
        均值滤波
        """
        ret = cv2.pyrMeanShiftFiltering(self.__image, 3, 3)
        cv2.imwrite("result/mean_0.jpg", ret)
        _, ret = ImageUtils.binary(ret, threshold_type=cv2.THRESH_OTSU)
        cv2.imwrite("result/mean_1.jpg", ret)
