# -*- coding: utf-8 -*-
import cv2


class Camera:

    _cap = cv2.VideoCapture(0)

    @classmethod
    def get_frame(cls):
        return cls._cap.read()
