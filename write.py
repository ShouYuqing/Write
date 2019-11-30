# copy & paste code from GitHub with commends added
# 11/20/2019 ys895
import cv2
import numpy as np
import pyautogui
from pynput.mouse import Button, Controller
import time
  
cap = cv2.VideoCapture(1)
cap.set(3,640) 
cap.set(4,640)

time.sleep(1.1)
_,img = cap.read()
alpha = 2
mouse = Controller()
gamma = 0.5
check = False
pts = [(0,0),(0,0),(0,0),(0,0)]
pointIndex = 0
# computer screen size
AR = (740,1280)
oppts = np.float32([[0,0],[AR[1],0],[0,AR[0]],[AR[1],AR[0]]])
a = 0
b = 0
# set the color upper bound&lower bound
# blue
#lower = (110, 50, 250)
#upper = (130,255,255)

# red
lower = (160, 100, 200)
upper = (179, 255, 255)


# gamma transformation
def adjust_gamma(image, gamma):

   invGamma = 1.0 / gamma
   table = np.array([((i / 255.0) ** invGamma) * 255
      for i in np.arange(0, 256)]).astype("uint8")

   return cv2.LUT(image, table)

# record the coordinates of the points in the window
def draw_circle(event,x,y,flags,param):
	global img
	global pointIndex
	global pts

	if event == cv2.EVENT_LBUTTONDOWN:
			cv2.circle(img,(x,y),5,(0,255,0),-1)
			pts[pointIndex] = (x,y)
			#print(pointIndex)
			pointIndex = pointIndex + 1


# constantly show the image img
def show_window():  
		global pts                     
		while True:
				#print(pts,pointIndex-1)
				cv2.imshow('img', img)
					
				if(pointIndex == 4):
					print(pts)
					break
						
				if (cv2.waitKey(20) & 0xFF == 27) :
					break

# perspective transformation
# same object's position in different coordinates
def get_persp(image,pts):
    ippts = np.float32(pts)
    Map = cv2.getPerspectiveTransform(ippts,oppts)
    warped = cv2.warpPerspective(image, Map, (AR[1], AR[0]))
    return warped

cv2.namedWindow('img')
# mouse callback functions
cv2.setMouseCallback('img',draw_circle)
print('Top left, Top right, Bottom Right, Bottom left')

# constantly show the image img unless there are four points detected
show_window()

while True:
	# capture the frame by the camera
	_, frame = cap.read()
	warped = get_persp(frame, pts)

	cv2.imshow('warped',warped)

	blurred = cv2.GaussianBlur(warped, (9, 9), 0)
	cv2.imshow('blurred', blurred)
	adjusted = adjust_gamma(blurred, gamma)
	cv2.imshow('adjusted',adjusted)
	hsv = cv2.cvtColor(adjusted,cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lower, upper)
	cv2.imshow('mask',mask)
	# ret & otsu
	ret, otsu = cv2.threshold(mask,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

	#hsv = cv2.GaussianBlur(hsvv, (5, 5), 0)

	# find contours from the previous image
	cnts = cv2.findContours(otsu.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
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
			check = True
			print(radius)
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
	
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
			#pts.appendleft(center)

	k=cv2.waitKey(5) & 0xFF
	if k == 27:
		break


cv2.destroyAllWindows()
cap.release()