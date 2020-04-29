# coding=utf-8
import cv2
import numpy


def video_demo():
    capture = cv2.VideoCapture(0)  # 打开跟电脑内置摄像头，会有解释
    i = 0
    while True:  # 用while true循环原因：capture为抓取视频的一帧然后显示，然后下一帧，往复循环

        ret, frame = capture.read()  # frame为视频中的每一帧
        frame = cv2.flip(frame, 1)  # 镜像变换，1表示将每一帧左右颠倒，-1表示将每一帧上下颠倒
        cv2.imshow("video", frame)  # 显示视频的每一帧
        # cv2.waitKey(0)  # waitKey(0)或者不传参数表示只刷新视频第一帧，所以不要无限等待，应该以一个帧率刷新图片，这样快速的刷新图片就变成视频流
        # cv2.waitKey(1000)  # 每1000毫秒即1秒钟刷新一帧视频

        # waitKey(delay)返回值： 返回值：如果delay>0,那么超过指定时间则返回-1；如果delay=0，将没有返回值。# 如果程序想响应某个按键，可利用if(waitKey(1)==Keyvalue)；#
        # 经常程序里面出现if( waitKey(10) >= 0 ) 是说10ms中按任意键进入此if块。

        # c = cv2.waitKey(1000)  # 保持窗口50ms如果用户没有任何按键操作，这里fps=20 if (cv2.waitKey(10000) <= 0):  #
        # 这里小于和大于区别：若<=，则没过10秒，打印i值，并且刷新下一帧，通过按键可加速，但仍打印i值， 【TODO2】
        # 若>，则每过10秒，刷新下一帧，但不打印i值，通过按键可加速，但仍不打印i值 continue  # 这里continue和break效果一样，待解决！！！
        # 意思：若用户在每一帧显示10秒钟内按任意键，则终止当且等待直到10秒，进入下一帧，即本来要10秒才显示一帧图片，通过按键可以加速视频刷帧速度，到目前为止，【TODO2】
        # 还没有办法退出while循环，除了终端强制ctrl+c i = i + 1

        # if cv2.waitKey(1) == 27:  # 按下“ESC”退出
        #     break

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按Q可关闭摄像头，并推出摄像框，此条语句防bug，详见网站收藏
            break
        print(i)


def get_image_info(image):
    print(type(image))  # image的类型为numpy的多维数组类型
    print(image.shape)  # （高，宽，通道数目）
    print(image.size)  # size为高×宽×通道数目
    print(image.dtype)  # 每个像素点所占字节位数多少
    pixel_data = numpy.array(image)
    print(pixel_data)


# src = cv2.imread("/home/cwz/Pictures/sky-space-telescope-universe-41951.jpg")   # 读取图片，输入图片地址以及名字
# cv2.namedWindow("input_image", cv2.WINDOW_AUTOSIZE)  # 创建显示图片窗口，左为窗口名，右为窗口大小
# cv2.imshow("input_image", src)  # 显示图片，左为窗口名，右为要显示的图片名
video_demo()
# get_image_info(src)
# cv2.imwrite("/home/test.png", src)  # 保存图片，根据文件后缀名自动保存为相应的格式
# cv2.waitKey(3000)  # waitKey(delay),delay为窗口显示时间，以毫秒为单位，例若3000，则显示图片3秒，然后自动关闭图片窗口，不输入delay参数或者设置为0，表示一直显示图片窗口知道直到用户按下一个键

cv2.destroyAllWindows()  # 根据waitforkey关闭所有显示窗口，若有多个也可控制关闭特定窗口
