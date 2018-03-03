# -*- coding: utf-8 -*-
import cv2
import multiprocessing
from utils.image_utils import ImageUtils


class MovingTargetOutline:
    """
    对连续帧运动目标提取轮廓
    """

    def __init__(self):
        self.__video_frames = []

    def add_frame(self, frame):
        """
        添加一帧
        :param frame: 一帧
        """
        self.__video_frames.append(frame)

    def set_frames(self, frames):
        """
        设置帧序列（会重置帧）
        :type frames: tuple
        :param frames: 帧序列
        """
        self.__video_frames = frames

    def reset(self):
        """
        重置所有帧
        """
        self.__video_frames = []

    def get_max_difference_frame(self):
        """
        使用三帧差分法
        :rtype: numpy.ndarray, numpy.ndarray
        :return: 差分帧像素最多的一帧
        """
        frame_len = len(self.__video_frames)
        # 帧数大于1才能差分
        if frame_len <= 1:
            return False
        # 每帧之间求差分,结果要求按顺序
        # 多进程使用cvtColor会崩溃？？？
        result_difference_frame = []
        for i in range(0, (frame_len - 2) if frame_len % 2 == 0 else (frame_len - 1)):
            difference_frame = self._get_difference_frame(self.__video_frames[i], self.__video_frames[i + 1])
            result_difference_frame.append(difference_frame)
        with multiprocessing.Pool() as pool:
            # 对差分帧每帧之间与运算
            max_none_zero = 0
            max_difference_frame = None
            max_difference_frame_index = None
            for none_zero, frame_index, and_frame in pool.imap_unordered(
                self._get_and_frame,
                map(
                    lambda x: (x, result_difference_frame[x], x + 1, result_difference_frame[x + 1]),
                    range(0, len(result_difference_frame) - 1)
                )
            ):
                if none_zero > max_none_zero:
                    max_none_zero = none_zero
                    max_difference_frame = and_frame
                    max_difference_frame_index = frame_index + 1
            if max_difference_frame_index:
                return self.__video_frames[max_difference_frame_index], max_difference_frame
        return None, None

    @staticmethod
    def _get_difference_frame(pre_frame, next_frame):
        """
        帧进行差分并二值化，二值化使用OTSU算法
        :param numpy.ndarray pre_frame: 前一帧
        :param numpy.ndarray next_frame: 后一帧
        :rtype: numpy.ndarray
        :returns: 差分帧
        """
        img = cv2.absdiff(pre_frame, next_frame)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = ImageUtils.binary(img, threshold_type=cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        return img

    @staticmethod
    def _get_and_frame(args):
        """
        帧进行与运算
        :param tuple args: args[0]前一帧下标, args[1]前一帧, args[2]后一帧下标, args[3]后一帧
        :rtype: (int, numpy.ndarray)
        :return: (非0像素个数，帧与运算结果)
        """
        img = cv2.bitwise_and(args[1], args[3])
        return cv2.countNonZero(img), args[0], img
