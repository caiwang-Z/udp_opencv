# coding=utf-8
import cv2


video_full_path = "/home/cwz/Downloads/新裤子_花火_乐队的夏天.mp4"
cap = cv2.VideoCapture(video_full_path)
print cap.isOpened()
frame_count = 1
# success = True
while True:
    success, frame = cap.read()
    print 'Read a new frame: ', success

    params = []
    # params.append(cv.CV_IMWRITE_PXM_BINARY)
    cv2.imwrite("video" + "_%d.jpg" % frame_count, frame, params)

    frame_count = frame_count + 1

cap.release()


