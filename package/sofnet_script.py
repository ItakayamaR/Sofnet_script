#!/usr/bin/env python

#Exportamos el modulo subprocess
from subprocess import call
from . import commands
import serial
import time

#Diccionarios con las configuraciones de red
confg1 = {"interfaz":"wlan0","ip":"192.168.1.6","netmask":"255.255.255.0","gw":"192.168.1.1"}
confg2 = {"interfaz":"wlan0","ip":"192.168.1.8","netmask":"255.255.255.0","gw":"192.168.1.1"}

#configuramos la comunicación serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
ser.flush()

confg= [confg1, confg2]
i=0

while (1):
    if ser.in_waiting > 0:
        i = int(ser.readline().decode('utf-8').rstrip())
        #call(["sudo","service","network, "stop"])
        call(["sudo","route", "add", "default","gw",confg[i]["gw"]])
        #(["sudo", "ifconfig", "wlan0", "192.168.1.6", "netmask", "255.255.255.0"])
        call(["sudo", "ifconfig", confg[i]["interfaz"], confg[i]["ip"], "netmask", confg[i]["netmask"]])

        call(["sudo","ifconfig", confg[i]["interfaz"], "up"])
    

