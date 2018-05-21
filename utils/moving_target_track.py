# -*- coding: utf-8 -*-
import cv2
import numpy

from models.Point import Point
from utils.camera import Camera
from utils.image_utils import ImageUtils


class MovingTargetTrack:
    """
    模板跟踪
    """
    __match_points_ratio = 100

    def __init__(self, target, mask):
        """
        构造函数
        :param numpy.ndArray target: 要跟踪的目标
        """
        self.__last_frame = None
        # self.__target_ratio, self.__target = ImageUtils.scale_image(target, 1080, 720)
        self.__target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        _, mask_binary = ImageUtils.binary(mask, threshold_type=cv2.THRESH_OTSU)
        self.__target_key_points, self.__target_descriptors = ImageUtils.get_key_points(self.__target, mask_binary)
        self.__target_key_points_len = len(self.__target_key_points)
        # 查找mask重心
        _, contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.__mask_contour = contours[0]
        moments = cv2.moments(self.__mask_contour)
        self.__position = Point(moments['m10'] / moments['m00'], moments['m01'] / moments['m00'])
        # 计算颜色直方图
        # target_mask = cv2.bitwise_and(target, mask)
        # target_hsv = cv2.cvtColor(target_mask, cv2.COLOR_BGR2HSV)
        # target_hist = cv2.calcHist(target_hsv, [0, 1], None, [50, 60], [0, 256, 0, 180])
        # self.__target_hist = None
        # cv2.normalize(target_hist, self.__target_hist)
        print("特征点数:%d" % self.__target_key_points_len)

    def track(self, frame):
        """
        更新目标的新坐标，并返回新旧质心坐标
        通过差分获取轮廓，Hu矩匹配
        :param numpy.ndArray frame:
        :return (Point, Point, list|None): 新旧坐标
        """
        # _, frame = ImageUtils.scale_image(frame, ratio=self.__target_ratio)
        if self.__last_frame is None:
            self.__last_frame = frame
            return self.__position, self.__position, ()

        img = cv2.absdiff(frame, self.__last_frame)
        self.__last_frame = frame
        img = cv2.GaussianBlur(img, (5, 5), 2.5)
        img = ImageUtils.morphology(img, cv2.MORPH_DILATE, 16)
        _, img = ImageUtils.binary(img, threshold_type=cv2.THRESH_OTSU)
        # 计算特征点
        key_points, descriptors = ImageUtils.get_key_points(frame, img)
        if len(key_points) * self.__match_points_ratio > self.get_key_points_count():
            matches = ImageUtils.knn_match(self.__target_descriptors, descriptors)
            if len(matches) > 0:
                # 匹配到合适的特征点
                points = ImageUtils.get_matches_points(key_points, matches)
                src_key_points = ImageUtils.get_matches_points(self.__target_key_points, matches, 1)
                # PROSAC去除错误点
                h, mask = cv2.findHomography(src_key_points, points, cv2.RHO)
                if mask is not None:
                    points = points[mask.ravel() == 1]
                    if len(points) > 0:
                        # points = ImageUtils.scale_points(points, self.__target_ratio)
                        points = ImageUtils.duplicate_points(points)
                        old_position = self.__position
                        self.__position = ImageUtils.affinity_point(old_position, h)
                        return old_position, self.__position, points

        # 匹配到的特征点较少
        return self.__position, self.__position, ()

    def get_key_points_count(self):
        """
        获取关键点数
        :return int:
        """
        return self.__target_key_points_len
