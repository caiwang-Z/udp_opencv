# coding=utf-8

import cv2
import struct
import time

img = cv2.imread("720p_199_原图_203.8kB.jpg")
cv2.imshow("Image", img)
time.sleep(2)
cv2.destroyAllWindows()
result, imgencode = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 20])  # 编码
# result, imgencode = cv2.imencode('.jpg', img)  # 编码 imgencode为一个一行的矩阵或者数组
imgdecode1 = cv2.imdecode(imgencode, 1)  # 解码
imgdecode2 = cv2.imdecode(imgencode, 3)  # 解码
length_after_compression = struct.pack('i', imgencode.shape[0])
print("img.shape:".format(img.shape))
print("imgencode.shape".format(imgencode.shape))
print("imgdecode1.shape:".format(imgdecode1.shape))
print(length_after_compression)

