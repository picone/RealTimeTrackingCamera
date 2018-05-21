# -*- coding: utf-8 -*-
import cv2


class Camera:

    #_cap = cv2.VideoCapture(0)
    _cap = cv2.VideoCapture("TUD-Stadtmitte.mp4")

    @classmethod
    def get_frame(cls):
        return cls._cap.read()

    @classmethod
    def reset(cls):
        cls._cap.retrieve()
