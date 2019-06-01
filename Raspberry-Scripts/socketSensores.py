
import socket
import RPi.GPIO as GPIO
import random
import time
import dht11
GPIO.setmode(GPIO.BCM) #Ajustamos la placa en modo BCM
GPIO.setup(4, GPIO.IN)#MQ135



HOST = '' # Server IP or Hostname
PORT = 12356 # Pick an open Port (1000+ recommended), must match the client sport

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ('Socket sensor created')

    #managing error exception
    try:
            s.bind((HOST, PORT))
    except socket.error:           
            print ('Bind sensor failed => Retry')
            time.sleep(3)
            continue

    s.listen(5)
    print ('Socket sensor awaiting messages')
    (conn, addr) = s.accept()
    print ('Sensor connected')

    mIzqAnt=0
    mDerAnt=0
      
    while True:
        try:
        
            data = conn.recv(1024)
            dataStr=str(data)
            if dataStr == "b''":
                print("Cierro => no recibo mensaje")
                conn.close()
                break;
            else :
                aux = dataStr.split("b'")                          
                listaParam=aux[1].split("#")
                listaParam[0] = listaParam[0].strip()

                # Compruebo mensaje solicitud
                if listaParam[0] == "SENSOR_REQUEST":
                    # Leo sensores           
                    sensor_mq135 = GPIO.input(4)
                    
                    instance = dht11.DHT11(pin = 24)
                    result = instance.read()
                    dht11Str = "#";
                    
                    if result.is_valid():
                        dht11Str =  dht11Str + str(result.temperature) + "#" + str(result.humidity)            
                    else:
                        dht11Str = dht11Str + "#"
                        
                    sensorString = "#" + str(sensor_mq135) + dht11Str;
                    print("Envio -> ", sensorString)
                    
                    # Envio lectura de sensores                          
                    conn.send(str.encode(sensorString))
                else :
                    conn.send(str.encode("EMPTY"))
                time.sleep(2)

        except Exception as ex:
            print(ex)
            print("Error, reiniciando conexion")
            conn.close()
            break
        
    conn.close() # Close connections
    
conn.close()

    
