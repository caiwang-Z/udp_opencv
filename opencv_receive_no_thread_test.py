# coding=utf-8
# from threading import Thread, Lock
from queue import Queue, PriorityQueue
import socket
import time
import cv2
import numpy
import sys


# from config import Config
# from packer import Packer
# import logging

class FramePack(object):
    def __init__(self, idx, ctime, frame):
        self.idx = idx
        self.ctime = ctime
        self.frame = frame

    def __lt__(self, other):
        return self.ctime > other.ctime  # TODO 重排存疑，是否是按照时间先后重排的


class NetVideoStream:
    def __init__(self, queue_size=128):
        self.frame_count_receive = 0
        self.stopped = False

        self.HOST = '192.168.0.104'
        self.PORT = 12340
        self.address = (self.HOST, int(self.PORT))
        self.queue_size = 128

        # self.Q = PriorityQueue(maxsize=self.queue_size)
        self.Q = Queue(maxsize=self.queue_size)  # 实力化一个队列类实例,队列最大值由初始化给出__init__,队列里即使超过最大队列值，也不会报错，但会有数据丢失
        # self.Q存放某一帧的各个分片 128
        self.img_Q = Queue(maxsize=self.queue_size)  # 128先进先出　　self.img_Q存放由分片重组得来的图片,将其刷起来就是视频

        self.w = 1080
        self.h = 720
        self.d = 3
        self.frame_pieces = 10
        self.frame_size = self.w * self.h
        self.frame_size_3d = self.w * self.h * self.d
        self.piece_size = int(self.w * self.h * self.d / self.frame_pieces)  # 一块数据，分成十片后，每片所占的大小 　276480字节
        self.idx_frame = int(self.h / self.frame_pieces)  # # 将一原数据帧分成十片后的一片数据，在原始图像占多少行,在这里idx_frame==72
        self.piece_limit = 30
        self.pack_len = 60016
        self.head_name = "FIRE"
        self.head_data_len_len = 4
        self.head_index_len = 1
        self.head_time_len = 7
        self.head_len = len(self.head_name) + self.head_data_len_len + self.head_index_len + self.head_time_len
        # self.pack_len = self.head_len + self.piece_size # 46096

        self.piece_array = []
        self.piece_time = int(time.time() * 1000)
        self.piece_fps = 40
        for i in range(self.frame_pieces):
            self.piece_array.append(None)

        # init timestamp
        self.frame = numpy.zeros(self.frame_size_3d, dtype=numpy.uint8)  # 一维数组
        # self.imshow = self.frame.reshape(self.h, self.w, self.d)
        self.last_frame_time = int(time.time() * 1000)
        self.require = True
        self.time_delay = 0
        self.delay_timer = int(time.time() * 1000)

        # def init_connection_sock(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(self.address)
            # return sock
        except socket.error as msg:
            print(msg)
            sys.exit(1)
    # def close_connection(self):
    #     self.sock.close()
    def start(self):
        # start threads to recieve
        for i in range(self.frame_pieces):
            self.recv_thread(i)
        self.rebuild_thread()

        return self

    def unpack_data(self, res):
        data_len = 0
        index = -1
        create_time = 0
        data = b''
        if len(res) < self.head_len:
            return index, create_time, data
        head_block = res[:self.head_len]  # 数据包头依次为固定长度(依次4,4,1,7字节)的包头名，数据长度，索引值，创建时间,然后是数据body
        name, data_len, index, create_time = self.unpack_header(head_block)
        data_end = data_len + self.head_len  # data_len是之前pack封装进去的分片大小 16
        body_block = res[self.head_len:data_end]

        return index, create_time, body_block

    def unpack_header(self, head_block):
        name = head_block[:4]  # name为fire本就是字符串,字符型变量索引跟str一样，这里的4表示取出head_block的前四个数据，但是索引为０,1,2,3
        data_len = int.from_bytes(head_block[4:8], byteorder='big')
        index = int.from_bytes(head_block[8:9], byteorder='big')
        create_time = int.from_bytes(head_block[9:self.head_len], byteorder='big')
        return name, data_len, index, create_time

    def rebuild_thread(self):
        while True:
            # 拥塞控制
            # if self.Q.qsize() > self.piece_limit:  # Queue.qsize()返回当前队列内的元素的个数 10 30
            #     self.Q = Queue()  # 清空队列
            #     if self.Q.mutex:  # 系统线程分配到此处，接着下面清空队列  # TODO 这里只有互斥锁的实例化，并没有上锁acquire和解锁release等??
            #         self.Q.queue.clear()  # 清空队列中其余所有元素
            # # 不断地从队列里面取数据尝试
            try:
                pack = self.Q.get()  # 从队列内返回并从原队列删除该元素，这里的元素为之前放入的FramePack类实例,创建时间最早的先被取出
                ptime = pack.ctime  # pack为类实例
                loop = self.frame_pieces - 1
                # print(pack is not None)
                while (pack is not None) and (loop >= 0):
                    idx = pack.idx  # idx为视频帧分片的索引
                    data = pack.frame  # frame为分片数据body
                    row_start = idx * self.piece_size  # 单片数据量大小，或者说720Ｐ逐行扫描(progressive)中逐行大小
                    row_end = (idx + 1) * self.piece_size
                    self.frame[row_start:row_end] = data  # self.Frame是一个之前在__init__时就设定好的(720*1080*3,)的一维数组
                    if self.Q.qsize() == 0:
                        break
                    pack = self.Q.get()
                    loop -= 1
                self.img_Q.put(self.frame.reshape(self.h, self.w, self.d))  #
                # 将队列里的十片数据取出拆分开来重组成视频的一帧，放入存放视频帧的队列里面
                ctime = int(time.time() * 1000)  # 乘以1000，小数点右移三位，int是抹去小数点返回整数值
                self.time_delay = ctime - ptime  # 从数据帧创建分片到这里组装成图片的耗费时间
            except:
                pass
        # return

    def recv_thread(self, thread_idx):
        # sock = self.init_connection_sock()

        # self.stopped = False

        # if self.stopped:
        # break
        # otherwise, ensure the queue has room in it
        if not self.Q.full():
            try:
                data, addr = self.sock.recvfrom(self.pack_len)
                idx, ctime, raw_img = self.unpack_data(data)
                line_data = numpy.frombuffer(raw_img, dtype=numpy.uint8)  # numpy.frombuffer 用于实现动态数组。
                # numpy.frombuffer 接受 buffer 输入参数，以流的形式读入转化成 ndarray 对象,shape并没有变化，只是转化成一维数组
                line_data = cv2.imdecode(line_data, 1).flatten()  # imdecode解码后shape为(720, 1280,3)然后flatten()压成一维数组
                # add the frame to the queue
                self.Q.put(FramePack(idx, ctime, line_data))  # 将类的实例（实例包括索引，创建时间，分片数据）按照创建时间早晚排序放进队列中
            except:
                pass
        else:
            # time.sleep(0.01)  # Rest for 10ms, we have a full queue
            pass
        # sock.close()  # 接收一片数据就开关一次套接字 感觉很繁琐 但不会丢数据？

    def read_img(self):
        # return self.imshow
        # print(self.img_Q.qsize())
        if self.img_Q.qsize() == 0:
            return None
        else:
            frame = self.img_Q.get()
            return frame

        # frame = self.img_Q.get()
        # if self.img_Q.qsize() > self.packer.frame_limit:  # 128
        #     # print("exeed limit")
        #     self.img_Q = Queue()
        #     if self.img_Q.mutex:
        #         self.img_Q.queue.clear()
        # return frame

    def read_show(self):
        while True:
            nvs = self.start()
            last_frame_time = time.time()
            tshow = 0

            while True:
                # print("reading img")
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # now = time.time()
                frame = self.read_img()
                if frame is not None:
                    self.frame_count_receive = self.frame_count_receive + 1
                    print("{}th frame was received".format(self.frame_count_receive))
                    cnow = int(time.time() * 1000)
                    if cnow - nvs.delay_timer > 200:
                        nvs.delay_timer = cnow
                        tshow = nvs.time_delay
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bottomLeftCornerOfText = (10, 50)
                    fontScale = 1
                    fontColor = (0, 0, 255)
                    lineType = 2
                    cv2.putText(frame, 'Get Fire! Recieve Delay: ' + str(tshow).ljust(3) + " ms",
                                bottomLeftCornerOfText,
                                font,
                                fontScale,
                                fontColor,
                                lineType)
                    cv2.imshow("Receive server", frame)
                    last_frame_time = int(time.time() * 1000)
            # print("piece show time is:", (now - last_frame_time))


def receivevideo():
    t = 0
    if t == 0:
        NetVideoStream().read_show()  # 一次性使用


if __name__ == "__main__":
    receivevideo()
