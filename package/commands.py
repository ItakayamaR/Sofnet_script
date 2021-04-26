import time
import serial
import struct

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
def Config_UART():
    serial_port = serial.Serial(
        port=puerto,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    )
    # Wait a second to let the port initialize
    time.sleep(1)
    return serial_port



def ReceiveComand():
   
    if(serial_port.inWaiting()==0):            
        return -3                       # No hay comunicacion serial

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
            return -1
        if(trama[4]!=len(trama)-5):
            print(len(trama))
            print("Error: longitud de trama no concuerda")
            continue
        if(trama[5]!= 0x8A):
            print("Error: No se reconoce el comando")
            return -1

        crc = CRC16(trama[4:len(trama)-2])
        print(trama[5:len(trama)-2])
        if(crc != bytes(trama[-2:])):
            print("Error: CRC no concuerda")
            return -1

        stateBoton = trama[6]

        #agrega respuesta al Jetson nano
        data = bytes([3,10])
        crc = CRC16(data)
        MDP = pream
        trama = MDP + data + crc

        serial_port.write(trama)
        print("Responde la trama")
        print(trama)
        return stateBoton

    return -2   # Error timeout

def SendComand(cmd,data=None):
    #validaciones
    if(cmd>255):
        print("No existe el comando")
        return 1
    cmd = cmd.to_bytes(1,'big')

    if(data==None):
        data_size=0
        data = bytearray(0)
    else:
        
        data_size = (data.bit_length()+7)//8
        data= data.to_bytes(data_size,'big')

    #crear trama
    MDP = bytes([36,77,68,80])
    longitud = bytes([3+data_size])
    trama = longitud + cmd + data
    crc = CRC16(trama) 
    trama = MDP + trama + crc
    print("Comando a enviar: ")
    print(trama)
    serial_port.write(trama)
    print("Comando enviado: ")
    return 0