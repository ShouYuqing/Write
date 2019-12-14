# 11/30/2019
# ECE5725 Final Project
# Yuqing Shou(ys895), Jiachao Chen(jc3345)
import cv2
import numpy as np
import pyautogui
from pynput.mouse import Button, Controller
import time

class Writer:
    def __init__(self, mouse, alpha = 2, gamma = 0.5, points = [(0,0),(0,0),(0,0),(0,0)], flag = False, prc_img_size = (740/2,1280/2), lower = (160, 100, 200), upper = (179, 255, 255), points_cnt = 0):
        '''
        Writer object
        :param mouse: mouse object
        :param alpha: value of alpha
        :param gamma:  value of gamma
        :param points: coordinates of the image on the opencv windows
        :param flag: initial flag
        :param prc_img_size:  process image size
        :param lower: lower bound of the color
        :param upper: upper bound of the color
        :param points_cnt: counter of points
        '''
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3,640)
        self.cap.set(4,640)
        _,self.img = self.cap.read()
        self.alpha = alpha
        self.mouse = mouse
        self.points = points
        self.gamma = gamma
        self.flag = flag
        self.prc_img_size = prc_img_size
        self.upper = upper
        self.lower = lower
        self.out_points = np.float32([[0,0],[prc_img_size[1],0],[0,prc_img_size[0]],[prc_img_size[1],prc_img_size[0]]])
        self.points_cnt = points_cnt

    # gamma transformation
    def gamma_adjustment(self, image, gamma):
        '''
        adjust the gamma value of an image
        :param image: input image
        :param gamma: value of gamma
        :return: new image
        '''
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
        # LUT transform
        return cv2.LUT(image, table)
    
    # record the coordinates of the points in the window
    def draw_points(self,event,x,y,flags,param):
        '''
        call-back function to draw points on the opencv window
        :param event: event
        :param x: x
        :param y: y
        :param flags: flags
        :param param: param
        :return: none
        '''
        if event == cv2.EVENT_LBUTTONDOWN:
                cv2.circle(self.img,(x,y),5,(0,255,0),-1)
                self.points[self.points_cnt] = (x,y)
                #print(pointIndex)
                self.points_cnt = self.points_cnt + 1

    def window_points(self):
        '''
        find four points on the opencv window
        :return: none
        '''
        while True:
                #print(pts,pointIndex-1)
                cv2.imshow('img', self.img)
                        
                if(self.points_cnt == 4):
                    print(self.points)
                    break
                            
                if (cv2.waitKey(20) & 0xFF == 27) :
                    break
    
    # perspective transformation
    def perspetive_transform(self, image,points):
        '''
        standard opencv perspective transformation: same object's position in different coordinates
        :param image: input image
        :param points: input coordinates of an image
        :return: new image
        '''
        in_points = np.float32(points)
        Map = cv2.getPerspectiveTransform(in_points,self.out_points)
        warped = cv2.warpPerspective(image, Map, (self.prc_img_size[1], self.prc_img_size[0]))
        return warped
    
    def write(self):
        '''
        main function used for writer
        :return: none
        '''
        cv2.namedWindow('img')
        # mouse callback functions
        cv2.setMouseCallback('img',self.draw_points)
        print('Please points at: Top Left, Top Right, Bottom Left, Bottom Right')

        # constantly show the image img unless there are four points detected
        self.window_points()
        #cv2.destroyAllWindows()

        while True:
            # capture the frame by the camera
            _, frame = self.cap.read()
            warped = self.perspetive_transform(frame, self.points)

            blurred = cv2.GaussianBlur(warped, (9, 9), 0)
            
            adjusted = self.gamma_adjustment(blurred, self.gamma)
            
            hsv = cv2.cvtColor(adjusted,cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower, self.upper)

            # ret & otsu
            ret, otsu = cv2.threshold(mask,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            # find contours from the previous image
            contour_num = cv2.findContours(otsu.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None

            a = 0
            b = 0
            # only proceed if at least one contour was found
            if len(contour_num) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(contour_num, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                a = x
                b = y
                print("a:" + str(b) + ", b:" + str(b))
                M = cv2.moments(c)
                if M["m00"] != 0:
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                else :
                    center = (0,0)

                # only proceed if the radius meets a minimum size
                if (radius>1):
                    self.flag = True
                    print(radius)
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
            
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

            width, height = pyautogui.size()

            m = (a/1280)*100
            n = (b/740)*100 

            # coordinates in the screen
            k = (width*m)/100
            c = (height*n)/100

            #pyautogui.FAILSAFE = False
            #pyautogui.moveTo(k,c)
            
            if self.flag == True :
                self.mouse.position = (int(k), int(c))
                print(int(k),int(c))
                self.mouse.press(Button.left)
                
            else:
                self.mouse.release(Button.left)

            self.flag = False   

            cv2.imshow('mask', mask)
            cv2.imshow('warped',warped)
            #cv2.imshow('blurred', blurred)
            #cv2.imshow('hsv', hsv)
            #cv2.imshow('frame',frame)
            #cv2.imshow('dilate',dilate)
            

            k=cv2.waitKey(5) & 0xFF
            if k == 27:
                break

        self.cap.release()

# main function
if __name__ == "__main__":
    mouse = Controller()
    writer = Writer(mouse)
    writer.write()
