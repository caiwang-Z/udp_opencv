# coding=utf-8
import cv2
import numpy
import socket
import struct

HOST = '192.168.0.102'
PORT = 9999
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket对象
server.connect((HOST, PORT))
print('now starting to send frames...')
capture = cv2.VideoCapture(0)  # VideoCapture对象，可获取摄像头设备的数据
print capture.isOpened()
try:
    while True:
        success, frame = capture.read()  # 若未获取成功视频帧，则返回的sucess和frame都为false或者none
        while not success and frame is None:  # 先执行not sucess和frame is None ，然后求与and,
            success, frame = capture.read()  # 获取视频帧
        result, imgencode = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])  # 编码
        server.sendall(struct.pack('i', imgencode.shape[0]))  # 发送编码后的字节长度，这个值不是固定的;将v1,
        # v2等参数的值进行一层包装，包装的方法由fmt指定。被包装的参数必须严格符合fmt。最后返回一个包装后的字符串。
        # 这里一共分为了两步，第一步发送编码后的字节长度，第二步发送的才是经过压缩编码的发送视频帧数据
        server.sendall(imgencode)  # 此为第二步：发送视频帧数据
        print('have sent one frame')
except Exception as e:
    print(e)
    server.sendall(struct.pack('c', 1))  # 发送关闭消息
    capture.release()
    server.close()

