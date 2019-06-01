
from __future__ import print_function
from imutils.video import VideoStream
import socket
import RPi.GPIO as GPIO
import os
import _thread
import argparse
import imutils
import time
import cv2
import os
import RPi.GPIO as GPIO
import memcache


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(6, GPIO.OUT)
GPIO.setup(2, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

#Motore oruga
motorI1 = 17
motorI2 = 18
motorD1 =  22
motorD2 = 23

GPIO.setup(motorI1,GPIO.OUT)
GPIO.setup(motorI2,GPIO.OUT)

pwmI1 = GPIO.PWM(motorI1, 50)
pwmI2 = GPIO.PWM(motorI2, 50)
pwmI1.start(0)
pwmI2.start(0)

GPIO.setup(motorD1,GPIO.OUT)
GPIO.setup(motorD2,GPIO.OUT)   

pwmD1 = GPIO.PWM(motorD1, 50)
pwmD2 = GPIO.PWM(motorD2, 50)
pwmD1.start(0)
pwmD2.start(0)





HOST = '' # Server IP or Hostname
PORT = 12345 # Pick an open Port (1000+ recommended), must match the client sport

   
    
def worker(comand):
    os.system(comand)

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ('Socket movement created')

    #managing error exception
    try:
            s.bind((HOST, PORT))
    except socket.error:           
            print ('Bind movement failed => Retry')
            time.sleep(3)
            continue

    s.listen(5)
    print ('Socket movement awaiting messages')
    (conn, addr) = s.accept()
    print ('Movement connected')

    mIzqAnt=0
    mDerAnt=0
    
    direccionIAnt = 0
    direccionDAnt = 0
    powerIAnt = 0
    powerDAnt = 0
      
    while True:
        try:
            data = conn.recv(1024)
            dataStr=str(data)
            if dataStr == "b''":
                conn.close()
                break;
            else :               
                aux = dataStr.split("b'")                          
                listaParam=aux[1].split("#")
                print("RECIBIDO => ", listaParam[0])
                listaParam[0] = listaParam[0].strip()
                if listaParam[0] == "M":

                    print("M =>  Motor Izq DIR = ", listaParam[1], " Motor Der DIR = ", listaParam[2])                    
                    print("M =>  Motor Izq = ", listaParam[3], " Motor Der = ", listaParam[4])
                    
                    direccionI = int(listaParam[1])
                    direccionD = int(listaParam[2])
                    
                    powerI = float(listaParam[3])
                    powerD = float(listaParam[4])

                    
                    if direccionI != direccionIAnt or powerI != powerIAnt:                       

                        if powerI == 0:
                            print("Stop")
                            pwmI1.ChangeDutyCycle(0)
                            pwmI2.ChangeDutyCycle(0)
                        elif direccionI == 1:
                            print("Izq +")
                            pwmI1.ChangeDutyCycle(powerI)
                            pwmI2.ChangeDutyCycle(0)
                                                
                        
                        elif direccionI == -1:
                            print("Izq -")
                            pwmI1.ChangeDutyCycle(0)
                            pwmI2.ChangeDutyCycle(powerI)
                                                    
                        else:
                            print("Stop")
                            pwmI1.ChangeDutyCycle(0)
                            pwmI2.ChangeDutyCycle(0)
                                                        
                    if direccionD != direccionDAnt or powerD != powerDAnt: 

                        if powerD == 0:
                            print("Stop")
                            pwmD1.ChangeDutyCycle(0)
                            pwmD2.ChangeDutyCycle(0)
                        elif direccionD == 1:
                            print("Der +")
                            pwmD1.ChangeDutyCycle(powerD)
                            pwmD2.ChangeDutyCycle(0)
                            
                        elif direccionD == -1:
                            print("Der -")
                            pwmD1.ChangeDutyCycle(0)
                            pwmD2.ChangeDutyCycle(powerD)
                                                    
                        else:
                            print("Stop")
                            pwmD1.ChangeDutyCycle(0)
                            pwmD2.ChangeDutyCycle(0)

                    if powerD == 0:
                            print("Stop")
                            pwmD1.ChangeDutyCycle(0)
                            pwmD2.ChangeDutyCycle(0)
                    if powerI == 0:
                            print("Stop")
                            pwmI1.ChangeDutyCycle(0)
                            pwmI2.ChangeDutyCycle(0)
                                          
                    powerI = powerIAnt
                    powerD = powerDAnt
                    direccionI = direccionIAnt
                    direccionD = direccionDAnt
                    
                elif listaParam[0] == "B":                  
                    servo = int(listaParam[1])
                    power = float(listaParam[2])
                    comandoMotor="python controlServo.py " + str(servo) + " " + str(power)                                  
                    _thread.start_new_thread( worker, (comandoMotor, ))
                elif listaParam[0] == "T":
                    state = int(listaParam[1])                   
    
                    if state == 1:
                        print("Tracking => Start")
                        
                        #Shared variable
                        shared = memcache.Client(['127.0.0.1:11211'], debug=0)
                        shared.set('TrackReady', '0')
                        
                        #Thread tracking
                        comand = "python objectDetectTrack.py"
                        _thread.start_new_thread( worker, (comand, ))
                        
                        #Waitting to camera ready
                        trckReady="0"
                        timeCounter = 0
                        while trckReady=="0":
                            trckReady = shared.get('TrackReady')
                            timeCounter = timeCounter + 1
                            
                            if timeCounter >=800:
                                print("Too much delay => aborting")
                                os.system("sudo pkill -f objectDetectTrack.py")
                                shared.delete("img")
                                break
                                #trckReady = "abort"
                            time.sleep(0.1)
                            
                        conn.send(str.encode(trckReady))
                        
                    else :
                        print("Tracking => Stop")
                        os.system("sudo pkill -f objectDetectTrack.py")
                        shared.delete("img")
                    
                elif listaParam[0] == "C":
                    print("CLOSE => ", listaParam[0])
                    os.system("sudo shutdown -h now")
                    #conn.close()
                    #break;
                    #comandoMotor="python controlServo.py " + str(servo) + " " + str(power)                               
                 
        except Exception as ex:
            os.system("sudo pkill -f objectDetectTrack.py")
            print(ex)
            print("Error, reiniciando conexion")
            conn.close()
            break
        
    os.system("sudo pkill -f objectDetectTrack.py")
    conn.close() # Close connections
    
os.system("sudo pkill -f objectDetectTrack.py")
conn.close()

    
