# -*- coding: utf-8 -*-
import cv2


class ImageUtils:

    @staticmethod
    def binary(src, threshold=0, maxval=255, threshold_type=cv2.THRESH_OTSU):
        """ 二值化图像
        :type src: numpy.ndarray
        :param src: 待处理图像
        :type threshold: int
        :param threshold: 阈值
        :type maxval: int
        :param maxval: 最大值，与THRESH_BINARY和THRESH_BINARY_INV一起使用
        :type threshold_type: int
        :param threshold_type: 自动选择阈值的算法，可选值:
            THRESH_BINARY
            THRESH_BINARY_INV
            THRESH_TRUNC
            THRESH_TOZERO
            THRESH_TOZERO_INV
            THRESH_MASK
            THRESH_OTSU 大律法
            THRESH_TRIANGLE 三角法
        参考https://docs.opencv.org/master/d7/d1b/group__imgproc__misc.html#gaa9e58d2860d4afa658ef70a9b1115576
        :rtype: (int, numpy.ndarray)
        :returns: (阈值，类型与src相同)
        """
        return cv2.threshold(src, threshold, maxval, threshold_type)
