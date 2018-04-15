# -*- coding: utf-8 -*-
import cv2
import numpy

from models.Point import Point


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
        # 三通道的先灰度处理
        if src.dtype and len(src.shape) == 3 and src.shape[2] == 3:
            src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(src, threshold, maxval, threshold_type)

    @staticmethod
    def img2bytes(img):
        """
        :type img: numpy.ndarray
        :param img: img图像
        :rtype: bytearray | None
        :return: 字节流
        """
        ret, img = cv2.imencode(".jpg", img)
        if ret:
            return numpy.array(img).tobytes()
        else:
            return None

    @staticmethod
    def bytes2img(img):
        buffer = numpy.asarray(bytearray(img), dtype="uint8")
        return cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    @staticmethod
    def get_centroid(moments):
        """
        计算质心
        :param moments:
        :return Point:
        """
        x = moments['m10'] / moments['m00']
        y = moments['m01'] / moments['m00']
        return Point(x, y)

    @staticmethod
    def compare_hu_moments(hu_moments_a, hu_moments_b):
        """
        计算两个hu矩的相似度，相当于cv2.CONTOURS_MATCH_I1
        :param list hu_moments_a:
        :param list hu_moments_b:
        :return float|bool:
        """
        hu_moments_a = numpy.array(hu_moments_a)
        hu_moments_b = numpy.array(hu_moments_b)
        if numpy.count_nonzero(hu_moments_a, 1).sum() != 7 or numpy.count_nonzero(hu_moments_b, 1).sum() != 7:
            return False
        return numpy.sum(numpy.abs(1 / numpy.sign(hu_moments_a) * numpy.log(numpy.abs(hu_moments_a))
                                   - 1 / numpy.sign(hu_moments_b) * numpy.log(numpy.abs(hu_moments_b))))

    @staticmethod
    def morphology(img, operation, iteration=1, kernel_size=(5, 5)):
        """
        进行开运算
        :param numpy.ndarray img:
        :param int operation: 使用的操作
        :param int iteration: 迭代次数
        :param list kernel_size: 卷积核大小
        :return numpy.ndarray:
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        return cv2.morphologyEx(img, operation, kernel, iterations=iteration)
