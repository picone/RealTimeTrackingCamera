## RealTimeTrackingCamera: 基于[OpenCV](https://github.com/opencv/opencv)的物体追踪摄像头

### 特性

1. 先让跟踪的目标运动一下，获取跟踪轮廓。
2. 通过轮廓匹配在实时的视频流中找到目标的运动轨迹。
3. 发送控制命令给舵机控制摄像头旋转。

### 关键点

#### 获取跟踪轮廓

1. 通过一系列差分帧，两两差分直接进行与运算，找出与运算结果最大的一帧。
2. 通过用户选择精细化轮廓。

#### 实时图像传输

1. 通过APScheduler定时发起帧抓取请求（这个方法可能会造成帧乱序，不要在意细节）。
2. 抓取到的帧使用jpeg编码成二进制字节流，使用protobuf协议，通过WebSocket传输到前端。
3. 前端使用<img>标签显示图像，渲染可以通过src="data:img/jpeg;base64,xxx"方式渲染。

#### 用户轮廓选择

1. 使用Canvas渲染图像
2. 通过MouseDown、MouseUp、MouseMove事件获取用户手势，使用beginPath()&closePath()以及clip()获取闭合路径。
3. 使用clearRect()清除图像显示背景图像。

### 依赖库

请阅读[requirements.txt](requirements.txt)。

FE：[https://github.com/picone/RealTimeTrackingCamera_FE](https://github.com/picone/RealTimeTrackingCamera_FE)

### Contributing

欢迎各种大佬提交宝贵代码OTZ__

### LICENSE

你可以在[GPL 3.0](LICENSE)许可下自由使用本项目。
