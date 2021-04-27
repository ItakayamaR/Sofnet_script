#!/usr/bin/env python

#Exportamos el modulo subprocess
from subprocess import call
import serial
import time

## Preambulo de la data en emisión/recepción ($SOF)
pream=bytes([36,83,79,70])
## Puerto usb a conectar 
puerto = "/dev/ttyUSB0"

#######################################
## Funcion que calcula el CRC16
## input:  buff (n Bytes)
## output  crc  (2 Bytes)
######################################
def CRC16(buff):

    leng = len(buff)
    crc = 0xFFFF 

    for pos in range(leng):
        crc ^= buff[pos]
        for i in range(8):
            if (crc & 0x0001)!=0:
                crc >>=1
                crc ^= 0xA001
            else:
                crc >>=1
    return crc.to_bytes(2,'big')

#########################################
## Configura el puerto UART
##
##########################################
def ConfigSerial():
    serial_port = serial.Serial(
        port=puerto,
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    )
    # Wait a second to let the port initialize
    time.sleep(1)
    return serial_port

def ReceiveCmd():
    #serial_port.flush()
    if(serial_port.inWaiting()==0):            
        return [-3]                       # No hay comunicacion serial
    time.sleep(0.2)
    start = time.time()
    trama = bytes()
    while(time.time() - start < 0.2):
        
        if(serial_port.inWaiting()==0):
            continue            
        trama +=serial_port.read()
        
        if(len(trama)<9):
            continue
        if(trama[0:4]!= pream):
            print("Error: "+ str(pream) + " no concuerda")
            return [-1]
        if(int(trama[4])!=len(trama)-5):
            print("Error: longitud de trama no concuerda")
            continue
        if(trama[5]!= 65 and trama[5]!= 73 ):
            print("Error: No se reconoce el comando")
            return [-1]
        
        crc = CRC16(trama[4:len(trama)-2])
        print(trama[5:len(trama)-2])
        
        if(crc != bytes(trama[-2:])):
            print(crc)
            print("Error: CRC no concuerda")
            return [-1]
        msg = trama[5:len(trama)-2]

        #Responde la comunicación
        data = bytes([3,10])
        crc = CRC16(data)
        MDP = pream
        trama = MDP + data + crc

        serial_port.write(trama)
        print("Responde la trama")
        print(trama)
        return msg

    return [-2]   # Error timeout

def sendCmd(cmd,data=None,data2=None):
    if(cmd>255):
        print("No existe el comando")
        return 1
    cmd = cmd.to_bytes(1,'big')
    if (data==0):
      data_size = 1
      data = data.to_bytes(data_size,'big')
    else:
        if(data==None):
            data_size = 0
            data = bytearray(0)
        else:
            data_size = (data.bit_length()+7)//8
            data = data.to_bytes(data_size,'big')
    if(data2==None):
        data2_size = 0
        data2 = bytearray(0)
    else:
        data2_size = (data2.bit_length()+7)//8
        data2 = data2.to_bytes(data2_size,'big')
    #print(data_size)

    MDP = pream
    longitud = bytes([3+data_size+data2_size])
    trama = longitud + cmd + data + data2
    crc = crc16(trama)
    trama = MDP + trama + crc
    serial_port.write(trama)


print("Start program")

serial_port = ConfigSerial()

while (1):
    i=ReceiveCmd()
    if (i):
        print(i[0])
        if (i[0]==65):
            print("u")
            print(["sudo","shutdown"])
        elif (i[0]==73):
            ip 	= '.'.join(i[1:4])
            gw 	= '.'.join(i[5:8])
            nm 	= '.'.join(i[9:12])
            dns	= '.'.join(i[13:16])
#         i = int(ser.readline().decode('utf-8').rstrip())
#         #call(["sudo","service","network, "stop"])
            print(["sudo","route", "add", "default","gw",gw])
            
            print(["sudo", "ifconfig", "eth0", ip, "netmask", nm])
#         #(["sudo", "ifconfig", "wlan0", "192.168.1.6", "netmask", "255.255.255.0"])

# 
#         call(["sudo","ifconfig", confg[i]["interfaz"], "up"])
    time.sleep(1)