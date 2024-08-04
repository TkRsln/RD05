# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 19:19:01 2024

@author: utkua
"""

"""
#Remote Command

##receive_schema:
    "#<sender_id>:<command_id>:<data>"

##sender_id:
    0:Server
    1:User
    2:AI
    3:Pi(Self)
    4:Phone

##command_id:
    0:position_status_change
        data:
            0:Repair
            1:Case
            2:Lay
            3:Stand
    
    1:control_mode
        data:
            0:None
            1:AI
            2:User
            3:All(Default)
            
    2:request_status
        data:
            0:All
            1:position_mode
            2:location
            

##sender_schema

    <inform_id>:<data>
    inform_id:
        0:position_status
            data:position_status
                0:Repair
                1:Case
                2:Lay
                3:Stand
                4:None
                5:Roll_Over
                6:Changing
        
                

"""

from RD05_Network import ServerHandler
from RD05_Lib import RD05_Serial as SerialHandler

class RD05:
    position_order=["REPAIR","CASE","LAY","STAND"]
    sender_order=["SERVER","USER","AI","PI","PHONE"]
    
    def __init__(self,serial_id="",server_ip="141.11.109.116",port=6060,serial_port="/dev/ttyS0"):
        self.tag="[RD05]"
        self.network=ServerHandler(
            to_ip=server_ip,to_port=port,
            listener_position_change=self.on_position_change_command,
            listener_command_error  =self.on_command_error
                                  )
        self.serial=SerialHandler(serial_port=serial_port,listener_pico=self.on_pico_msg)
        
    def on_position_change_command(self,sender_id,data):
        print(self.tag,f"Sender:{RD05.sender_order[sender_id]}, requested_position:{data[0]}")
        self.network.send("0:6")
        return
    
    def on_command_error(self):
        print(self.tag,"Could not resolve command from server")
        return
    
    def on_pico_msg(self,msg):
        print(self.tag,"pico msg:",msg)
    
r = RD05()