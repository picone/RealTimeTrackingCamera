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
        :rtype: numpy.ndarray
        :return: 差分帧像素最多的一帧
        """
        frame_len = len(self.__video_frames)
        # 帧数大于1才能差分
        if frame_len <= 1:
            return False
        with multiprocessing.Pool() as pool:
            result_difference_frame = []
            # 每帧之间求差分,结果要求按顺序
            for difference_frame in pool.imap(
                self._get_difference_frame,
                map(
                    lambda x: (self.__video_frames[x], self.__video_frames[x + 1]),
                    range(0, (frame_len - 2) if frame_len % 2 == 0 else (frame_len - 1))
                ),
            ):
                result_difference_frame.append(difference_frame)
            # 对差分帧每帧之间与运算
            max_none_zero = 0
            max_difference_frame = None
            for none_zero, and_frame in pool.imap_unordered(
                self._get_and_frame,
                map(
                    lambda x: (result_difference_frame[x], result_difference_frame[x + 1]),
                    range(0, len(result_difference_frame) - 1)
                )
            ):
                if none_zero > max_none_zero:
                    max_none_zero = none_zero
                    max_difference_frame = and_frame
        return max_difference_frame

    @staticmethod
    def _get_difference_frame(args):
        """
        帧进行差分并二值化，二值化使用OTSU算法
        :type args: list
        :param args: args[0]前一帧， args[1]后一帧
        :rtype: numpy.ndarray
        :returns: 差分帧
        """
        img = cv2.absdiff(args[0], args[1])
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, img = ImageUtils.binary(img, threshold_type=cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        return img

    @staticmethod
    def _get_and_frame(args):
        """
        帧进行与运算
        :type args: list
        :param args: args[0]前一帧，args[1]后一帧
        :rtype: (int, numpy.ndarray)
        :return: (非0像素个数，帧与运算结果)
        """
        img = cv2.bitwise_and(args[0], args[1])
        return cv2.countNonZero(img), img
