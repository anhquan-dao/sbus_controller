import serial 
import time

ser = serial.Serial(
    '/dev/ttyUSB0', 
    baudrate=100000, 
    parity=serial.PARITY_EVEN, 
    stopbits=serial.STOPBITS_TWO
)
ser.flush()
time.sleep(1)
print(ser.in_waiting)

data = bytearray()
while True:
    if not ser.in_waiting:
        continue

    byte = ser.read()
    if len(data) == 0:
        if ord(byte) == 0x0F:
            data.append(byte)
        
        continue

    elif(len(data) < 24):
        data.append(byte)
        continue
    
    if(ord(byte) != 0x00):
        data = bytearray()
        continue

    data.append(byte)
    for i in range(25):
        print(data[i]),
    print()
    
    data = bytearray()