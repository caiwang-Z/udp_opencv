#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:st time:2020-04-23


import cv2
import numpy
import socket
import struct


def main():
    frame_number = 1
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # localaddr = ("", 9999)  # 绑定任意一個本地ip，必须是自己电脑的ip，同桌朋友的不行,双引号内空格，whitespace
    buffSize = 65535

    tcp_socket.connect(('192.168.0.102', 7898))
    download_file_name = input("please enter the file name you want to download: ")
    tcp_socket.send(download_file_name.encode("utf-8"))

    recv_data = tcp_socket.recv(1024)
    if recv_data:
        print('now waiting for frames...')
        while True:
            data, address = tcp_socket.recvfrom(buffSize)  # 先接收的是字节长度,此为第一步：接收server第一步发送的经过压缩编码的字节长度
            if len(data) == 1 and data[0] == 1:  # 如果收到关闭消息则停止程序
                tcp_socket.close()
                cv2.destroyAllWindows()
                exit()
            if len(data) != 4:  # 进行简单的校验，长度值是int类型，占四个字节 ；视频发送成功了并且客户端也收到数据了，但是数据为None
                length = 0
            else:
                length = struct.unpack('i', data)[0]  # 长度值，对第一步接收的经过压缩编码的字节长度进行解压解码，相当于
            data, address = tcp_socket.recvfrom(buffSize)  # 接收编码图像数据；此为第二步，接收server第二步发送的经过压缩编码的视频帧数据
            if length != len(data):  # 进行简单的校验
                continue
            data = numpy.array(bytearray(data))  # 格式转换
            imgdecode = cv2.imdecode(data, 1)  # 解码
            print('have received {} frame'.format(frame_number))
            frame_number = frame_number + 1
            cv2.imshow('frames', imgdecode)  # 窗口显示
            if cv2.waitKey(1) == 27:  # 按下“ESC”退出
                break
        tcp_socket.close()
        cv2.destroyAllWindows()

    tcp_socket.close()


if __name__ == "__main__":
    main()
