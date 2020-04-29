#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:st time:2020-04-22


import cv2
import numpy
import socket
import struct

# 服务器先于客户端运行，运行之后，客户端发出请求，服务器分配新的套接字并应答
def main():
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 监听套接字，类似10010客服热线，只负责接听电话然后分配给每一个client
    # 客户端新的套接字，分配完成之后，自己又去监听了，就跟该客户端断掉联系
    tcp_server_socket.bind(("", 7898))  # 本地任意一个ip的7898端口
    tcp_server_socket.listen(128)  # 让默认的套接字由主动变为被动listen

    while True:  # 注意：多个client可同时链接服务器，但是服务器只能一个一个的进行处理
        print("等待一个新的客户端的到来...")
        new_client_socket, client_addr = tcp_server_socket.accept()  # accept返回两个参数，1.新的套接字（类似打通10010
        # 热线后分配的单独为你解决问题的人工服务，负责通信），2.链接本服务器的客户端的地址。返回参数为元组的拆包
        # a, b = (11,22),那么a=11,b=22 ,本条语句为解堵塞，为accept之前一直处于接听状态,所以如果客户端若没有请求，程序会一直停在这里直到客户端发起请求
        print("一个新的客户端已经到来 %s" % str(client_addr))

        while True:
            recv_data = new_client_socket.recv(1024)  # 不同udp返回数组，因为这里前面accept时已经知道客户端的地址，所以这里返回的直接就是数据
            print("客户端的请求是： %s" % recv_data.encode("utf-8"))

            if recv_data:
                print('now starting to send frames...')
                capture = cv2.VideoCapture(0)  # VideoCapture对象，可获取摄像头设备的数据
                print capture.isOpened()
                try:
                    while True:
                        success, frame = capture.read()  # 若未获取成功视频帧，则返回的sucess和frame都为false或者none
                        while not success and frame is None:  # 先执行not sucess和frame is None ，然后求与and,
                            success, frame = capture.read()  # 获取视频帧
                        result, imgencode = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])  # 编码
                        new_client_socket.sendall(struct.pack('i', imgencode.shape[0]))  # 发送编码后的字节长度，这个值不是固定的;将v1,
                        # v2等参数的值进行一层包装，包装的方法由fmt指定。被包装的参数必须严格符合fmt。最后返回一个包装后的字符串。
                        # 这里一共分为了两步，第一步发送编码后的字节长度，第二步发送的才是经过压缩编码的发送视频帧数据
                        new_client_socket.sendall(imgencode)  # 此为第二步：发送视频帧数据 尝试发送string的所有数据， 成功则返回None， 失败则抛出异常。
                        #  send()的返回值式发送的字节数量， 这个数量值可能小于要发送的string的字节数，也就是说可能无法发送string中所有的数据。如果有错误，则会抛出异常。
                        print('have sent one frame')
                except Exception as e:
                    print(e)
                    new_client_socket.sendall(struct.pack('c', 1))  # 发送关闭消息 python中的struct主要是用来处理C
                    # 结构数据的，读入时先转换为Python的字符串类型，然后再转换为Python的结构化类型，比如元组(tuple)啥的
                    capture.release()
                    new_client_socket.close()

                new_client_socket.send("ok,i have recive the request from you".encode("utf-8"))  # 回送数据给客户端
            else:
                break

        new_client_socket.close()  # 完成对一个client的请求后，就关闭该客户端，然后进入循环等待下一个新的客户端发起请求，
        print("服务器已经关闭....")
    tcp_server_socket.close()


if __name__ == "__main__":
    main()
