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
    def get_centroid(points):
        """
        计算质心
        :param points:
        :return Point:
        """
        points = numpy.array(points)
        return Point(points[:, 0].mean(), points[:, 1].mean())

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

    @staticmethod
    def get_key_points(img, mask=None, hessian_threshold=100):
        """
        计算特征点
        :param numpy.ndarray img:
        :param numpy.ndarray mask:
        :param int hessian_threshold:
        :return list, list:
        """
        surf = cv2.xfeatures2d.SURF_create(hessian_threshold)
        return surf.detectAndCompute(img, mask)

    @staticmethod
    def knn_match(descriptors_a, descriptors_b, good_distance=0.7):
        """
        匹配descriptors
        :param list descriptors_a:
        :param list descriptors_b:
        :param int k: 至少匹配特征值
        :param float good_distance: 距离阈值
        :return list:
        """
        FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=3)
        search_params = dict(checks=100)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        try:
            matches = flann.knnMatch(descriptors_a, descriptors_b, 2)
        except Exception:
            return ()
        if good_distance > 0:
            ret = []
            for m, n in matches:
                if m.distance < good_distance * n.distance:
                    ret.append(m)
            return ret
        else:
            return matches

    @staticmethod
    def get_matches_points(points, matches, idx=0):
        """
        获取匹配的点坐标
        :param list points:
        :param list(DMatch) matches:
        :param int idx:
        :return numpy.ndarray:
        """
        if idx == 0:
            return numpy.float32([points[m.trainIdx].pt for m in matches])
        else:
            return numpy.float32([points[m.queryIdx].pt for m in matches])

    @staticmethod
    def draw_points(img, points, radius, color):
        """
        绘制一系列点在图片上
        :param numpy.ndarray img:
        :param list points:
        :param int radius:
        :param tuple color:
        :return:
        """
        for point in points:
            cv2.circle(img, point, radius, color, cv2.FILLED)

    @staticmethod
    def scale_image(img, max_width=0, max_height=0, keep_ratio=True, ratio=1):
        """
        缩放图像
        :param numpy.ndarray img:
        :param int max_width:
        :param int max_height:
        :param bool keep_ratio:
        :param int ratio:
        :return int:
        """
        if ratio != 1:
            height, width, _ = img.shape
            return ratio, cv2.resize(img, (int(width / ratio), int(height / ratio)))
        elif keep_ratio and max_width > 0 and max_height > 0:
            height, width, _ = img.shape
            width_ratio = width / max_width
            height_ratio = height / max_height
            ratio = max(width_ratio, height_ratio)
            return ratio, cv2.resize(img, (int(width / ratio), int(height / ratio)))
        else:
            return 0, cv2.resize(img, (max_width, max_height))

    @staticmethod
    def scale_points(points, ratio):
        return numpy.array(points) * ratio

    @staticmethod
    def duplicate_points(points):
        visited = dict()
        ret = list()
        for point in points:
            x, y = int(point[0]), int(point[1])
            if x not in visited:
                visited[x] = {}
            if y not in visited[x]:
                visited[x][y] = 1
                ret.append((x, y))
        return ret
