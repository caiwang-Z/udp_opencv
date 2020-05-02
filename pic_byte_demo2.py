# coding=utf-8

# import numpy
import cv2
import os
import struct
import sys

# 全局变量
VIDEO_PATH = "/home/cwz/Downloads/190803_纯享：刺猬乐队《生之响往》_乐队的夏天.mp4"
# VIDEO_PATH = "/home/cwz/Downloads/Predators_Swim_In_The_Super" \
#              "-Clear_Waters_Of_South_Brazil___VR_360___Seven_Worlds__One_Planet.mp4"  # 视频地址
EXTRACT_FOLDER = './extract_folder'  # 存放帧图片的位置
EXTRACT_FREQUENCY = 200  # 帧提取频率


def extract_frames(dst_folder):
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        exit()
    c = 1
    while c % EXTRACT_FREQUENCY != 0:
        ret, frame = cap.read()
        length_of_frame = sys.getsizeof(frame)
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('{}/'.format(dst_folder) + str(c) + '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 0])  # 存储为图像
        # cv2.imwrite('{}/'.format(dst_folder) + str(c) + '.jpg', frame)  # 存储为图像
        result, imgencode = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 0])  # 编码
        imgdecode = cv2.imdecode(imgencode, 1)  # 解码
        cv2.imshow('frame_after_compression', imgdecode)  # 解码解压后的视频
        # cv2.imshow('frame_before_compression', frame)  # 原视频无压缩
        # cv2.imshow('frame_after_compression', imgencode)  # 编码压缩后的视频
        length_after_compression = sys.getsizeof(imgencode)  # 压缩后的图片即传输数据每帧大小
        length_after_decode = sys.getsizeof(imgdecode)  # 压缩后的图片即传输数据每帧大小
        # result, imgencode = cv2.imencode('.jpg', img)  # 编码 imgencode为一个一行的矩阵或者数组
        # length_after_compression = struct.pack('i', imgencode.shape[0])
        c = c + 1
        if c == 199:
            print("before compression in server the 200th picture is {} kB and it's shape is {}".format(
                length_of_frame / 1024, frame.shape))
            print("after compression(imcode) in server the 200th picture is {} kB and it's shape is {}".format(
                length_after_compression / 1024, imgencode.shape))
            print("after decode in client the 200th picture is {} kB and it's shape is {}".format(
                length_after_decode / 1024, imgdecode.shape))
            print("the first value of frame is {}, the first value of imgdecode is {}".format(frame[0, 0], imgdecode[0, 0]))
            # 所以编码压缩前的图片数据和解压解码和的数据不一样？？？
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    # exit()


def main():
    # 递归删除之前存放帧图片的文件夹，并新建一个
    import shutil  # 对文件和文件夹进行操作的一个库，非常好用
    try:
        shutil.rmtree(EXTRACT_FOLDER)
    except OSError:
        pass
    os.mkdir(EXTRACT_FOLDER)
    # 抽取帧图片，并保存到指定路径
    extract_frames(EXTRACT_FOLDER)


if __name__ == '__main__':
    main()

