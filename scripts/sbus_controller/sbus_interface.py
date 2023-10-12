#!/usr/bin/python
# -*- coding: utf-8 -*-
import serial

from multiprocessing import Event
from collections import deque
from threading import Thread

import time

class SBUSData:
    SBUS_HEADER = 0x0F
    SBUS_FOOTER = 0x00
    def __init__(self):
        self.frame = deque(maxlen=50)
        self.complete = False

    def is_complete(self):
        self.complete = False
        if(len(self.frame) < 3):
            return self.complete
    
        if (self.frame[0] == self.SBUS_HEADER
        and self.frame[-1] == self.SBUS_FOOTER):
            self.complete = True

        return self.complete
    
    def parse(self):
        if not self.is_complete():
            return None, False
        
        channels = 16*[0]

        frame = [self.frame[i] for i in range(-25, 0)]
        # TODO: parse all other channels
        channels[0]     = frame[1] | ((frame[2] << 8) & 0x07FF)
        channels[1]     = (frame[2] >> 3) | ((frame[3] <<5) & 0x07FF)
        channels[2]     = (frame[3] >> 6) | (frame[4] << 2) | ((frame[5] << 10) & 0x07FF)
        channels[3]     = (frame[5] >> 1) | ((frame[6] << 7) & 0x07FF)
        channels[4]     = (frame[6] >> 4) | ((frame[7] << 4) & 0x07FF)
        channels[5]     = (frame[7] >> 7) | (frame[8] << 1) | ((frame[9] << 9) & 0x07FF)
        channels[6]     = (frame[9] >> 2) | ((frame[10] << 6) & 0x07FF)
        channels[7]     = (frame[10] >> 5) | ((frame[11] << 3) & 0x07FF)
        channels[8]     = frame[12] | ((frame[13] << 8) & 0x07FF)
        channels[9]     = (frame[13] >> 3) | ((frame[14] <<5) & 0x07FF)
        channels[10]    = (frame[14] >> 6) | (frame[15] << 2) | ((frame[16] << 10) & 0x07FF)
        channels[11]    = (frame[16] >> 1) | ((frame[17] << 7) & 0x07FF)
        channels[12]    = (frame[17] >> 4) | ((frame[18] << 4) & 0x07FF)
        channels[13]    = (frame[18] >> 7) | (frame[19] << 1) | ((frame[20] << 9) & 0x07FF)
        channels[14]    = (frame[20] >> 2) | ((frame[21] << 6) & 0x07FF)
        channels[15]    = (frame[21] >> 5) | ((frame[22] << 3) & 0x07FF)       
        
        failsafe        = (frame[23] & 0x08)
        return channels, failsafe
    
class SBUSReceiver:
    __BAUD = 100000
    def __init__(self, logger, params=dict()):
        self.__default_params = {"port": '/dev/ttyUSB0'}

        for default_key in self.__default_params.keys():
            if default_key not in params.keys():
                params[default_key] = self.__default_params[default_key]
    
        self.port       = params["port"]
        
        self.ser = None

        self.data = SBUSData()
        self.last_byte = 0
        self.failsafe_event = Event()

        self.logger = logger

        self.shutdown = False
        self.deque = deque(maxlen=5)

        self.read_thread = Thread(target=self.read_sbus_data, name="read_thread")
        self.read_thread.daemon = True
        
        self.connect()
        self.read_thread.start()

    def __del__(self):
        self.shutdown = True
        self.ser.close()
        self.read_thread.join()

    def connect(self):

        try:
            self.ser = serial.Serial(
                self.port,
                timeout = None,
                baudrate=self.__BAUD, 
                parity=serial.PARITY_EVEN, 
                stopbits=serial.STOPBITS_TWO,
                bytesize=serial.EIGHTBITS
            )
            while not self.shutdown and self.ser.in_waiting < 25:
                self.logger.warn("Wait until data has been received to start the read thread.")
                time.sleep(1)

        except Exception as e:
            self.logger.error("Try connect to %s, but encountered %s."%(self.port, e))
            return False
        
        return True

    def read_sbus_data_once(self):
        if self.ser.in_waiting == 0:
            return

        while self.ser.in_waiting and (not self.shutdown):   
            byte = ord(self.ser.read())
            self.data.frame.append(byte)
            
            if len(self.data.frame) < 25:
                continue

            if self.data.frame[-1] != SBUSData.SBUS_FOOTER \
            or self.data.frame[-25]  != SBUSData.SBUS_HEADER:
                continue
            
            channels, failsafe = self.data.parse()
            if not channels:
                return

            if failsafe:
                self.failsafe_event.set()
            else:
                self.failsafe_event.clear()

            self.deque.append(channels)

            # The buffer is likely to be populated with repeated data.
            # Thus, the input buffer is clear after each complete frame read
            self.ser.reset_input_buffer()
            return

    def read_sbus_data(self):
        if not self.ser:
            self.logger.error("No connection has been attempted!")
            return

        while not self.shutdown:
            self.read_sbus_data_once()
            
            # Sleep to prevent CPU overusage
            time.sleep(0.01)
            
if __name__ == "__main__":
    pass    




        
            
