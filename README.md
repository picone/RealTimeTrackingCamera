## RealTimeTrackingCamera: 基于[OpenCV](https://github.com/opencv/opencv)的物体追踪摄像头

### 特性

1. 先让跟踪的目标运动一下，通过三帧差分的方法找到二值化后非0像素最多的图，也就是运动轮廓最清晰的一帧取得轮廓。
2. 通过轮廓匹配在实时的视频流中找到目标的运动轨迹。
3. 发送控制命令给舵机控制摄像头旋转。

### 依赖库

请阅读[requirements.txt](requirements.txt)。

### Contributing

提交代码前请阅读[contribution guidelines](https://github.com/opencv/opencv/wiki/How_to_contribute)。

### LICENSE

你可以在[GPL 3.0](LICENSE)许可下自由使用本项目。
