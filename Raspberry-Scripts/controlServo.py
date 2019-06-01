from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def setServoAngle(servo, dutyCycle):
    pwm = GPIO.PWM(servo, 50)
    pwm.start(8)
    pwm.ChangeDutyCycle(dutyCycle)
    sleep(0.3)
    #pwm.stop()

if __name__ == '__main__':
    import sys
    servo = int(sys.argv[1])
    print("Servo script => pin = ", servo, " pwm = ", sys.argv[2])
    GPIO.setup(servo, GPIO.OUT)
    setServoAngle(servo, float(sys.argv[2]))
    GPIO.cleanup()   
    
    
