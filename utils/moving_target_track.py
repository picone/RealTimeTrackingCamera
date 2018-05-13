# -*- coding: utf-8 -*-
import cv2

from models.Point import Point
from utils.camera import Camera
from utils.image_utils import ImageUtils


class MovingTargetTrack:
    """
    模板跟踪
    """
    __match_points_ratio = 70

    def __init__(self, target, mask):
        """
        构造函数
        :param numpy.ndArray target: 要跟踪的目标
        """
        self.__last_frame = None
        # self.__target_ratio, self.__target = ImageUtils.scale_image(target, 1080, 720)
        self.__target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        _, self.__mask = ImageUtils.binary(mask, threshold_type=cv2.THRESH_OTSU)
        self.__target_key_points, self.__target_descriptors = ImageUtils.get_key_points(self.__target, self.__mask)
        self.__target_key_points_len = len(self.__target_key_points)
        self.__position = Point()
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
                _, mask = cv2.findHomography(src_key_points, points, cv2.RHO)
                if mask is not None:
                    points = points[mask.ravel() == 1]
                    if len(points) > 0:
                        # points = ImageUtils.scale_points(points, self.__target_ratio)
                        points = ImageUtils.duplicate_points(points)
                        if len(points) * self.__match_points_ratio > self.get_key_points_count():
                            old_position = self.__position
                            self.__position = ImageUtils.get_centroid(points)
                            return old_position, self.__position, points
        # 匹配到的特征点较少
        return self.__position, self.__position, ()

    def get_key_points_count(self):
        """
        获取关键点数
        :return int:
        """
        return self.__target_key_points_len
