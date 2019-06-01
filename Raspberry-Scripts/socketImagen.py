
import argparse
import time
import socket
import RPi.GPIO as GPIO
import memcache


GPIO.setmode(GPIO.BCM) #Ajustamos la placa en modo BCM
GPIO.setup(4, GPIO.IN)#MQ135



HOST = '' # Server IP or Hostname
PORT = 12365 # Pick an open Port (1000+ recommended), must match the client sport

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    print ('Socket imagen created')

    #managing error exception
    try:
            s.bind((HOST, PORT))
    except socket.error:           
            print ('Bind sensor failed => Retry')
            time.sleep(3)
            continue

    s.listen(5)
    
    print ('Socket imagen awaiting messages')
    (conn, addr) = s.accept()
    print ('Sensor connected')
    shared = memcache.Client(['127.0.0.1:11211'], debug=0)
    while True:
        try:            
            print("Empieza")
            data = conn.recv(1024)
            dataStr=str(data)
            print("Recibo peticion")
            if dataStr == "b''":          
                print("Cierro => no recibo mensaje")
                conn.close()
                break;
            #else :
            else:
                try:
                    if shared.get('img') is None:
                        print("Imagen null")
                        time.sleep(3)
                        conn.sendall(str.encode("null"))
                   
                    else:
                        imgFrame = shared.get('img')
                        conn.sendall(imgFrame)
                        print("Envio imagen")
                except Exception as exc:
                    print("Errorcete")
                   
                    
        except Exception as ex:
            print(ex)
            print("Error, reiniciando conexion")
            conn.close()
            break
        
    conn.close() # Close connections
    
conn.close()

    
