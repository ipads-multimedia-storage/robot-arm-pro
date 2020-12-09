import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import numpy as np
from LABConfig import *
from ArmIK.Transform import *

range_rgb = {
    'red':   (0, 0, 255),
    'blue':  (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

size = (640, 480)
__target_color = ('red', 'green', 'blue')

#找出面积最大的轮廓
#参数为要比较的轮廓的列表
def getAreaMaxContour(contours) :
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours : #历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c))  #计算轮廓面积
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  #只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = c

        return area_max_contour, contour_area_max  #返回最大的轮廓

def detect(image):
    frame_resize = cv2.resize(image, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
    # it seems that this is not necessary
    #如果检测到某个区域有识别到的物体，则一直检测该区域直到没有为止
    # if get_roi and not start_pick_up:
    #     get_roi = False
    #     frame_gb = getMaskROI(frame_gb, roi, size)      
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间

    # the color of the max contour
    color_area_max = None
    # the area of the max contour
    max_area = 0
    # the max contour
    areaMaxContour_max = 0
    
    for i in color_range:
        if i in __target_color:
            frame_mask = cv2.inRange(frame_lab, color_range[i][0], color_range[i][1])  #对原图像和掩模进行位运算
            opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  #开运算
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) #闭运算
            contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #找出轮廓
            areaMaxContour, area_max = getAreaMaxContour(contours)  #找出最大轮廓
            if areaMaxContour is not None:
                if area_max > max_area:#找最大面积
                    max_area = area_max
                    color_area_max = i
                    areaMaxContour_max = areaMaxContour
    if max_area > 2500:  # 有找到最大面积
        # rect: [(center_x, center_y), (width, height), angle]
        rect = cv2.minAreaRect(areaMaxContour_max)
        box = np.int0(cv2.boxPoints(rect))
        
        roi = getROI(box) #获取roi区域
        # get_roi = True
        img_centerx, img_centery = getCenter(rect, roi, size, square_length)  # 获取木块中心坐标
            
        world_x, world_y = convertCoordinate(img_centerx, img_centery, size) #转换为现实世界坐标
        
        cv2.drawContours(image, [box], -1, range_rgb[color_area_max], 2)
        cv2.putText(image, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[color_area_max], 1)  #绘制中心点
        return image, world_x, world_y, rect[2], color_area_max
    
    return False