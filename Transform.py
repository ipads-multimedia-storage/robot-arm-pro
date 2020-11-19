#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time

__isRunning = False

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# app初始化调用
def init():
    print("Transforming Init")

# app开始玩法调用
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("Transforming Start")

# 变量重置
def reset():
    global __isRunning
    __isRunning = False

def get_location():
    return (0, 0)


if __name__ == '__main__':
    init()
    start()

    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
    
        if img is not None:
            location = get_location()

            # Display the resulting frame        
            cv2.imshow("input", img)

            print('notify arm to move to :', location)

            key = cv2.waitKey(1)
            if key == 27:
                break
    cv2.destroyAllWindows() 
    cv2.VideoCapture(0).release()
