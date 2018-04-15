# -*- coding: utf-8 -*-
import cv2

from utils.image_utils import ImageUtils


class MovingTargetTrack:
    """
    模板跟踪
    """

    def __init__(self, target):
        """
        构造函数
        :param numpy.ndArray target: 要跟踪的目标
        """
        self.__last_frame = None
        _, self.__target = ImageUtils.binary(target, threshold_type=cv2.THRESH_OTSU)
        self.__target_moments = cv2.moments(self.__target, True)
        self.__target_hu_moments = cv2.HuMoments(self.__target_moments)
        self.__position = ImageUtils.get_centroid(self.__target_moments)

    def track(self, frame):
        """
        更新目标的新坐标，并返回新旧质心坐标
        通过差分获取轮廓，Hu矩匹配
        :param numpy.ndArray frame:
        :return (Point, Point, list|None): 新旧坐标
        """
        if self.__last_frame is None:
            self.__last_frame = frame
            return self.__position, self.__position, None
        else:
            img = cv2.absdiff(frame, self.__last_frame)
            # 灰度处理后再高斯滤波，降低计算量
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.GaussianBlur(img, (5, 5), 2.5)
            _, img = ImageUtils.binary(img, threshold_type=cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
            _, contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            min_semblance = -1
            min_moments = None
            min_index = -1
            # 计算特征的相似度
            for i, feature in enumerate(self._get_feature(contours)):
                moments, hu_moments = feature
                semblance = ImageUtils.compare_hu_moments(self.__target_hu_moments, hu_moments)
                if semblance is not False and (semblance < min_semblance or min_semblance == -1):
                    min_semblance = semblance
                    min_moments = moments
                    min_index = i
            self.__last_frame = frame
            if min_moments:
                old_position = self.__position
                self.__position = ImageUtils.get_centroid(min_moments)
                return old_position, self.__position, contours[min_index]
            else:
                return self.__position, self.__position, None

    @staticmethod
    def _get_feature(contours):
        """
        计算图像的矩和hu矩
        :param list contours:
        :return list:
        """
        ret = []
        # TODO: 并行计算
        for contour in contours:
            moments = cv2.moments(contour)
            hu_moments = cv2.HuMoments(moments)
            ret.append((moments, hu_moments))
        return ret
