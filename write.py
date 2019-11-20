# demo for the project
# 11/20/2019 ys895
import numpy as np
import cv2 


#img = cv2.imread('img.png')
img = np.zeros((512, 512, 3), np.uint8)

# perspective transformation
def get_persp(image,pts):
        ippts = np.float32(pts)
        Map = cv2.getPerspectiveTransform(ippts,oppts)
        warped = cv2.warpPerspective(image, Map, (AR[1], AR[0]))
        return warped


def show_window():
	while True:
		cv2.imshow('img', img)

def draw_demo(img, x, y, radius, center):
	cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 2)
	cv2.circle(img, center, 5, (0, 0, 255), -1)

# use the default camera
cap = cv2.VideoCapture(0)

cv2.namedWindow('img')
cv2.setMouseCallback('img', draw_demo)

#display window
#show_window()

# Create a black image
img = np.zeros((512,512,3), np.uint8)

# Draw a diagonal blue line with thickness of 5 px
cv2.line(img,(0,0),(511,511),(255,0,0),5)

center = (0, 0)

#draw_demo(img, 20, 20, 5, center)
while True:
	_, frame = cap.read()
