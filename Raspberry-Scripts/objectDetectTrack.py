
from __future__ import print_function
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os
import RPi.GPIO as GPIO
import memcache
import base64

panServo = 26
tiltServo = 19

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


def moverPosicion (servo, angle):
	dutyCycle = angle / 18. + 3.
    os.system("python controlServo.py " + str(servo) + " " + str(dutyCycle))

def centrarObjeto (x, y):
    global panAngle
    global tiltAngle
    
    print("Ancho = " ,x)
    print("Alto = ", y)
    if (x < 130):
        panAngle += 10
        if panAngle > 180:
            panAngle = 180
        print("X = ", panAngle)
        moverPosicion (panServo, panAngle)
 
    elif (x > 260):
        panAngle -= 10
        if panAngle < 0:
            panAngle = 0
        print("X = ", panAngle)
        moverPosicion (panServo, panAngle)
    
    if (y < 100):
        tiltAngle -= 10
        if tiltAngle < 0:
            tiltAngle = 0
        print("Y = ", tiltAngle)
        moverPosicion (tiltServo, tiltAngle)
 
    elif (y > 140):
        tiltAngle += 10
        if tiltAngle > 180:
            tiltAngle = 180
        print("Y = ", tiltAngle)
        moverPosicion (tiltServo, tiltAngle)

vs = VideoStream('http://localhost:8081').start()
time.sleep(2.0)

colorLower = (155, 100, 100)
colorUpper = (195, 255, 255)

global panAngle
panAngle = 90
global tiltAngle
tiltAngle =90

moverPosicion (panServo, panAngle)
moverPosicion (tiltServo, tiltAngle)

shared = memcache.Client(['127.0.0.1:11211'], debug=0)
shared.set('TrackReady', '1')

while True:
	frame = vs.read()      
	frame = imutils.rotate(frame, angle=0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	mascara = cv2.inRange(hsv, colorLower, colorUpper)
	mascara = cv2.erode(mascara, None, iterations=2)
	mascara = cv2.dilate(mascara, None, iterations=2)

	cnts = cv2.findContours(mascara.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	center = None

	if len(cnts) > 0:
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		
		if radius > 10:
			cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)			
			centrarObjeto(int(x), int(y))

	cv2.imshow("Frame", frame)
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),70]
	result,image_str = cv2.imencode('.jpg',frame, encode_param)
	jpg_as_text = base64.b64encode(image_str)
	
	shared.set('img', jpg_as_text)