#!/bin/bash

source /home/pi/.virtualenvs/cv/bin/activate
#source /home/pi/.profile
#workon cv &>> /home/pi/output.log
cd /home/pi
python socketMovimiento.py & python socketSensores.py & python socketImagen.py

