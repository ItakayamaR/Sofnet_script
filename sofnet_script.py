#!/usr/bin/env python3

#Exportamos el modulo subprocess
import serial
import time
from subprocess import call
import netifaces

## Preambulo de la data en emisión/recepción ($SOF)
pream=bytes([36,83,79,70])

## Puerto usb a conectar 
puerto = "/dev/ttyUSB1"

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
            #print("Error: longitud de trama no concuerda")
            continue
        if(trama[5]!= 65 and trama[5]!= 73 ):
            print("Error: No se reconoce el comando")
            return [-1]
        
        crc = CRC16(trama[4:len(trama)-2])
        print(trama[5:len(trama)-2])
        
        if(crc != bytes(trama[-2:])):
            print(crc)
            print("Error: CRC no concuerda")
            #return [-1]
        msg = trama[5:len(trama)-2]
        
        print(trama)
        return msg

    return [-2]   # Error timeout

print("Start program")

serial_port = ConfigSerial()

lista=[]
while (1):
    i=ReceiveCmd()
    if (i[0] > 0):
        if (i[0]==65):
            print("La maquina se apagará")
            call(["sudo","shutdown"])
            break
        
        elif (i[0]==73):
            
            #Transformamos la lista de byte a string
            for n in i:
                lista.append(str(n))
            
            #Filtramos las interfaces correspondientes a las iniciales "enp"
            interface_list = netifaces.interfaces()
            interface_filter=[k for k in interface_list if 'enp' in k]
            
            print("Las interfaces detectadas son: ")
            print(interface_filter)
            
            #call(["sudo","systemctl","restart","NetworkManager"])
            
            #Separamos el ip, gw, netmask y dns para cada interfaz
            for index,interface in enumerate(interface_filter):
                ip 	= '.'.join(lista[1+(16*index):5+(16*index)])
                gw 	= '.'.join(lista[5+(16*index):9+(16*index)])
                nm 	= '.'.join(lista[9+(16*index):13+(16*index)])
                dns	= '.'.join(lista[13+(16*index):17+(16*index)])

                #Eliminamos el DNS por default
                call(["nmcli", "device", "mod", interface, "ipv4.ignore-auto-dns", "yes"])
                #Agregamos el DNS correspondiente
                call(["nmcli", "device", "mod", interface, "ipv4.dns", dns])
                
                #reiniciamos la interfaz para que el cambio haga efecto
                call(["sudo","ifconfig", interface, "down"])
                call(["sudo","ifconfig", interface, "up"])
                
                #Cambiamos la ip y la mascara de red
                call(["sudo", "ifconfig", interface, ip, "netmask", nm])
                #Cambiamos el gateway
                call(["sudo","route", "add", "default","gw",gw, interface])
                
            #call(["sudo","systemctl","restart","NetworkManager"])
                
    time.sleep(1)