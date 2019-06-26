# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO
from time import sleep
from threading import Thread
import numpy as np
import math

GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)
laser=GPIO.PWM(33, 50)
laser.start(0)


stop_thread = False



vertical_min = 63
vertical_max = 115
vertical_range = vertical_max - vertical_min
horizontal_min = 96
horizontal_max = 160
horizontal_range = horizontal_max - horizontal_min

vertical_starting_angle = 83
horizontal_starting_angle = 120



vertical_angle = vertical_starting_angle
horizontal_angle = horizontal_starting_angle



frame_width = 500

prev_verical = 0
prev_hor = 0
rect_global = (0,0)
diff_x = 0
diff_y = 0



GPIO.setup(12, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)
vertical=GPIO.PWM(12, 50)
vertical.start(0)
hor=GPIO.PWM(32, 50)
hor.start(0)



# Function that aiming towards the target
def changeRot():
    global prev_verical,prev_hor,horizontal_angle,vertical_angle,rect_global,frame_global,stop_thread
    
    if prev_verical == vertical_angle and prev_hor == horizontal_angle:
            return
        
    duty = vertical_angle / 18 + 2
    GPIO.output(12, True)
    vertical.ChangeDutyCycle(duty)
    
    
    duty = horizontal_angle / 18 + 2
    GPIO.output(32, True)
    hor.ChangeDutyCycle(duty)
    sleep(0.1)
    GPIO.output(12, False)
    vertical.ChangeDutyCycle(0)
    
    
    GPIO.output(32, False)
    hor.ChangeDutyCycle(0)
    
    prev_verical = vertical_angle
    prev_hor = horizontal_angle

        
sleep(1)        
changeRot() # initialize the starting degree of servo
sleep(1)


lower_red = np.array([200,200,220]) 
upper_red = np.array([255,255,255]) 


# Out record video optional
#out = cv2.VideoWriter('test.mp4', cv2.VideoWriter_fourcc(*'H264'), 25, (500,375))

vs = VideoStream(src=0).start()
time.sleep(2.0)

# initialize the first frame in the video stream
firstFrame = None # we compare the current frame with last frame
counter = 0

## Finding the laser real location in camera frame
def findLaserCoordinates(x,y,coords):
    distance = 10000000
    f = ()
    if type(coords) != None:
        for p in coords:
            dist = math.hypot(x - p[0][0], y - p[0][1])
            if distance > dist:
                distance = dist
                f = (p[0][0],p[0][1])
    return f

# calculate the degree towards the target
def lasertopoint(rect):
    global vertical_angle,horizontal_angle,rect_global,diff_x,diff_y
    
    (x,y) = rect
    
    vertical_angle = vertical_max - ((y-diff_y)/375) * vertical_range             
    horizontal_angle = horizontal_max - ((x-diff_x)/frame_width) * horizontal_range

# Calculate the differences between real location of laser and actually hit point.
def updateDiff(ax_hit, ay_hit, sx_hit, sy_hit): # ax = actualy hit / sx = suppose hit
    global diff_x,diff_y
    
    diff_x = ax_hit - sx_hit
    diff_y = ay_hit - sy_hit

# Check if laser is found inside detected rect.
def isLaser(small_rect_frame):
    global lower_red ,upper_red
    
    mask = cv2.inRange(small_rect_frame, lower_red, upper_red)
    img=mask.astype(np.uint8)
    coord=cv2.findNonZero(img)

    return (str(type(coord)) != '<class \'NoneType\'>')

# loop over the frames of the video
while True:
    
    # grab the current frame and initialize the occupied/unoccupied
    # text
    counter += 1
    frame = vs.read()
    
    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if frame is None:
        break

    # resize the frame
    frame = imutils.resize(frame, width=frame_width)

    # detecting red colors in order to detect laser

    mask = cv2.inRange(frame, lower_red, upper_red)
    img=mask.astype(np.uint8)
    coord=cv2.findNonZero(img)

    # gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    firstFrame = gray

    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    ''' # In this script not in used, we saw in real time in raspberry pi its heavily effects FPS and wasn't accurate at all.
    if 0 and counter % 10 == 0 and type(coord) != None:
        (x,y) = rect_global
        mPoint = findLaserCoordinates(x,y,coord)
        (ax_hit,ay_hit) = mPoint
        updateDiff(ax_hit,ay_hit,x,y)
        #print(mPoint)
    '''
    i = 0        
    # loop over the contours
    for c in cnts:
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        small_rect = frame[y:y+h,x:x+w] # the first rectangle movement captured
        #if(isLaser(small_rect)): ## Optional
        #    break
           
        rect_global = (x+w/2 , y+h/2) # center of rec
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # drawing rec
        
        
        lasertopoint(rect_global) # calculate the degree towards target
        changeRot() # aiming towards it
        break
             #   print(x+w,y+h)
            

    cv2.imshow("Security Feed", frame)  # real frame
    cv2.imshow("Red Window", mask) # Red light only
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        GPIO.cleanup()
        break


stop_thread = True
vertical.stop()
hor.stop()
laser.stop()
# cleanup the camera and close any open windows
vs.stop()
cv2.destroyAllWindows()