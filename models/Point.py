# -*- coding: utf-8 -*-


class Point(object):
    def __init__(self, x=-1, y=-1):
        """
        构造函数
        """
        self.__x = x
        self.__y = y

    @property
    def x(self):
        """
        设置横坐标
        :rtype: float|int
        :return:
        """
        return self.__x

    @property
    def y(self):
        """
        设置纵坐标
        :rtype: float|int
        :return:
        """
        return self.__y

    def set(self, x, y):
        """
        设置点坐标
        :param float|int x:
        :param float|int y:
        """
        self.__x = x
        self.__y = y

    def is_point(self):
        """
        判断是否合法坐标
        :rtype: bool
        :return:
        """
        return self.__x < 0 or self.__y < 0

    def __str__(self):
        return "x:%f,y%s" % (self.__x, self.__y)

    __repr__ = __str__
