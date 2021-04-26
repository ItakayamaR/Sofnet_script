#!/usr/bin/env python

#Exportamos el modulo subprocess
from subprocess import call
from package import commands
import serial
import time

i=0

pream=bytes([36,83,79,70])

while (1):
    print("hoa"+pream+"aaja")
    time.sleep(1)
#     if ser.in_waiting > 0:
#         i = int(ser.readline().decode('utf-8').rstrip())
#         #call(["sudo","service","network, "stop"])
#         call(["sudo","route", "add", "default","gw",confg[i]["gw"]])
#         #(["sudo", "ifconfig", "wlan0", "192.168.1.6", "netmask", "255.255.255.0"])
#         call(["sudo", "ifconfig", confg[i]["interfaz"], confg[i]["ip"], "netmask", confg[i]["netmask"]])
# 
#         call(["sudo","ifconfig", confg[i]["interfaz"], "up"])
    

pream=bytes([36,83,79,70])