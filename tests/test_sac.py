# -*- coding: utf-8 -*-
import cv2
import unittest

import time

from utils.camera import Camera
from utils.image_utils import ImageUtils


class TestImageFilter(unittest.TestCase):

    def setUp(self):
        target = cv2.imread("result/track_target.jpg")
        mask = cv2.imread("result/mask.jpg")
        self.__target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        _, self.__mask = ImageUtils.binary(mask, threshold_type=cv2.THRESH_OTSU)
        self.__target_key_points, self.__target_descriptors = ImageUtils.get_key_points(self.__target, self.__mask)

    def test_ransac(self):
        """
        随机抽样一致
        """
        Camera.reset()
        self.__last_frame = None
        print("RANSAC")
        for i in range(1, 30):
            start = time.clock()
            _, frame = Camera.get_frame()
            if self.__last_frame is None:
                self.__last_frame = frame
                continue
            img = cv2.absdiff(frame, self.__last_frame)
            self.__last_frame = frame
            img = cv2.GaussianBlur(img, (5, 5), 2.5)
            img = ImageUtils.morphology(img, cv2.MORPH_DILATE, 16)
            _, img = ImageUtils.binary(img, threshold_type=cv2.THRESH_OTSU)
            # 计算特征点
            key_points, descriptors = ImageUtils.get_key_points(frame, img)
            matches = ImageUtils.knn_match(self.__target_descriptors, descriptors)
            if len(matches) > 0:
                # 匹配到合适的特征点
                points = ImageUtils.get_matches_points(key_points, matches)
                src_key_points = ImageUtils.get_matches_points(self.__target_key_points, matches, 1)
                # RANSAC去除错误点
                _, mask = cv2.findHomography(src_key_points, points, cv2.RANSAC)
                if mask is not None:
                    points_after = points[mask.ravel() == 1]
                    end = time.clock()
                    print("%d\t%d\t%d\t%f" % (i, len(points), len(points_after), end-start))

    def test_prosac(self):
        """
        改进抽样一致
        """
        Camera.reset()
        self.__last_frame = None
        print("PROSAC")
        for i in range(1, 30):
            start = time.clock()
            _, frame = Camera.get_frame()
            if self.__last_frame is None:
                self.__last_frame = frame
                continue
            img = cv2.absdiff(frame, self.__last_frame)
            self.__last_frame = frame
            img = cv2.GaussianBlur(img, (5, 5), 2.5)
            img = ImageUtils.morphology(img, cv2.MORPH_DILATE, 16)
            _, img = ImageUtils.binary(img, threshold_type=cv2.THRESH_OTSU)
            # 计算特征点
            key_points, descriptors = ImageUtils.get_key_points(frame, img)
            matches = ImageUtils.knn_match(self.__target_descriptors, descriptors)
            if len(matches) > 0:
                # 匹配到合适的特征点
                points = ImageUtils.get_matches_points(key_points, matches)
                src_key_points = ImageUtils.get_matches_points(self.__target_key_points, matches, 1)
                # PROSAC去除错误点
                _, mask = cv2.findHomography(src_key_points, points, cv2.RHO)
                if mask is not None:
                    points_after = points[mask.ravel() == 1]
                    end = time.clock()
                    print("%d\t%d\t%d\t%f" % (i, len(points), len(points_after), end - start))
