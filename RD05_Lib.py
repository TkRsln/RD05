# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 16:22:19 2024

@author: utkua
"""

import serial
import time
import threading

class RD05_Serial:
    
    def __init__(self,listener_pico=None,serial_port="/dev/ttyS0",boundrate=9600,timeout=5):
        self.tag="[Serial]"
        self.listener_pico=listener_pico
        self.ser = serial.Serial(serial_port, boundrate, timeout=timeout)
        self.ser.flush()
        threading.Thread(target=self.read_from_pico).start()
    
    def write_to_pico(self,msg):
        self.ser.write(msg.encode('utf-8'))
        #print(self.tag,f"message sent ({msg})")

    def read_from_pico(self):
        while True:
            start_time = time.time()
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').rstrip()
                if self.listener_pico != None:
                    self.listener_pico(line)
                #print("Pico'dan gelen veri: " + line)
            # Döngü başına 1/60 saniye bekle
            time.sleep(max(0, (1/60) - (time.time() - start_time)))

    