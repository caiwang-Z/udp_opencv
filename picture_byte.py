# coding=utf-8
import os
import cv2
import numpy

# 全局变量
VIDEO_PATH = "/home/cwz/Downloads/新裤子_花火_乐队的夏天.mp4"  # 视频地址
EXTRACT_FOLDER = './extract_folder'  # 存放帧图片的位置
EXTRACT_FREQUENCY = 100  # 帧提取频率


def extract_frames(video_path, dst_folder, index):
    # 主操作
    video = cv2.VideoCapture()
    if not video.open(video_path):
        print("can not open the video")
        exit(1)
    count = 1
    while True:
        frame = video.read()
        if frame is None:
            break
        if count % EXTRACT_FREQUENCY == 0:
            # img = numpy.array(frame)
            save_path = "{}/{:>03d}.jpg".format(dst_folder, index)
            cv2.imwrite(save_path, frame)
            index = index + 1
        count = count + 1
    video.release()
    # 打印出所提取帧的总数
    print("Totally save {:d} pics".format(index - 1))


def main():
    os.mkdir(EXTRACT_FOLDER)
    # 抽取帧图片，并保存到指定路径
    extract_frames(VIDEO_PATH, EXTRACT_FOLDER, 1)


if __name__ == '__main__':
    main()
