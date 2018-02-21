# -*- coding: utf-8 -*-
import json


class Response:

    _response_msg = {
        1: "OK",
        10: "JSON解析失败",
        11: "未知错误",
        12: "路径不存在",
    }

    @classmethod
    def get(cls, code, data=None, msg=None):
        """
        获取消息响应json
        :type code: int
        :param code: 消息代码
        :type data: Dict | None
        :param data: 附加数据
        :type msg: string
        :param msg: 附加消息
        :rtype: string
        :return: 返回的json
        """
        response = {"code": code, "data": data}
        if msg is None and cls._response_msg[code]:
            response["msg"] = cls._response_msg[code]
        return json.dumps(response)
