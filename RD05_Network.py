# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 00:01:43 2024

@author: utkua
"""
import socket
from threading import Thread,Lock
import time

class Network_Client_TCP:
    def __init__(self,ip_addres,port,listener_receive=None,listener_leave=None,listener_connection_start=None,debug=False):
        self.listener_receive=listener_receive
        self.listener_leave=listener_leave
        self.listener_connection_start=listener_connection_start
        self.tag="[Client_TCP]"
        self.debug=debug
        self.HOST=ip_addres
        self.PORT=port
        self.sender_lock = Lock()
        self.main_loop_lock=Lock()
        self.main_loop=True
        thread = Thread(target = self.__start_channel__)
        thread.start()
        
    def __start_channel__(self):
            self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.addr=(self.HOST, self.PORT)
            self.socket.connect(self.addr)
            self.__start_connection__()
            self.__start_reader__()
            #ls.log(self.tag,"connection granted",level=ls.MSG_OK)
            
            with self.sender_lock:
                self.addr=(self.HOST, self.PORT)
                    
    def __start_reader__(self):
        thread = Thread(target = self.__connection_reader__)
        thread.start()
        
    def __connection_reader__(self):
        try:
            while self.main_loop:
                with self.sender_lock:
                    data = self.socket.recv(1024)
                    if not data:
                        self.__start_left__()
                        with self.sender_lock:
                            print(self.tag,"loop is broken")
                            self.socket=None
                        break
                    self.__start_receive__(data)
        except:
            with self.sender_lock:
                self.socket=None
            self.__start_left__()
            
            
            
    def __start_receive__(self,data):
        thread = Thread(target = self.on_receive,args=(data,))
        thread.start()
        
    def __start_left__(self):
        thread = Thread(target = self.on_left)
        thread.start()
    
    def __start_connection__(self):
        thread = Thread(target = self.on_connection_start)
        thread.start()
    
    def on_connection_start(self):
        if self.debug:
            print(self.tag,"connection started with:",self.addr)
        if self.listener_connection_start != None:
            self.listener_connection_start(self,self.addr)
    
    def on_receive(self,cmd):
        if self.debug:
            print(self.tag,"received:",cmd,"from:",self.addr)
        if self.listener_receive != None:
            self.listener_receive(self,(cmd).decode("utf-8"),self.addr)
    
    def on_left(self):
        if self.debug:
            print(self.tag,"connection closed with",self.addr)
        if self.listener_leave != None:
            self.listener_leave(self,self.addr)
            
    def send(self,data):
            if self.socket!=None:
                self.socket.sendall(str.encode(data))
            #print("Sent",(self.socket!=None))
                
    def is_connected(self):
        with self.sender_lock:
            return (self.connection!=None)
        
    def try_stop(self):
        with self.main_loop_lock:
            self.main_loop=False
            
class Client:
    def __init__(self):
        self.tag="[Client]"
        self.socket=Network_Client_TCP("141.11.109.116", 5050,listener_receive=self.on_receive,listener_connection_start=self.on_connection_granted,listener_leave=self.on_connection_lost)
        self.send_prompt()
        
    def send_prompt(self,prompt=None):
        while True:
            prompt=input("Enter:")
            self.socket.send(prompt)
        
    def on_connection_granted(self,tcp:Network_Client_TCP,addr):
        print(self.tag,f"Connection granted with server{addr}")
    
    def on_connection_lost(self,tcp:Network_Client_TCP,addr):
        print(self.tag,f"Connection LOST with server{addr}")
        
    def on_receive(self,tcp:Network_Client_TCP,msg,addr):
        print(self.tag,f"Received:{msg}")
        
class client_module:
    
    def __init__(self,listener_command_receive=None,listener_start=None,listener_leave=None,to_ip="141.11.109.116",to_port=6060):
         self.tag="[Client]"
         self.listener_leave=listener_leave
         self.listener_start=listener_start
         self.socket=Network_Client_TCP(to_ip, to_port, listener_receive=self.on_receive,    listener_connection_start=self.on_connection_granted,listener_leave=self.on_connection_lost)
             
    
    def on_connection_granted(self,tcp:Network_Client_TCP,addr):
        print(self.tag,f"Connection granted with server: {addr}")
        if self.listener_start != None:
            self.listener_start()
    
    def on_connection_lost(self,tcp:Network_Client_TCP,addr):
        print(self.tag,f"Connection LOST with server: {addr}")
        if self.listener_leave != None:
            self.listener_leave()
            
    def send(self,data):
        self.socket.send(data)
    def on_receive(self,tcp:Network_Client_TCP,msg,addr):
        print(self.tag,"Received:",msg)
          

"""
#Remote Command

##receive_scheme:
    "<sender_id>:<command_id>:<data>"

##sender_id:
    -1:Undefined
    0:Server
    1:User
    2:AI
    3:Pi(Self)
    4:Phone

##command_id:
    -1:Undefined
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
       
            
##sending_schema

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
class ServerHandler(client_module):
    
    COMMAND_ERROR = -1
    COMMAND_POSITION_STATUS_CHANGE = 0
    POSITION_REPAIR = 0
    POSITION_CASE = 1
    POSITION_LAY = 2
    POSITION_STAND = 3
    
    def __init__(self,listener_position_change=None,listener_command_error=None,to_ip="141.11.109.116",to_port=6060):
        self.listener_position_change = listener_position_change
        self.listener_command_error=listener_command_error
        self.tag="[ServerHandler]"
        client_module.__init__(self,to_ip=to_ip,to_port=to_port)
    
    def on_connection_granted(self,tcp:Network_Client_TCP,addr):
        print(self.tag,f"Connection granted with server: {addr}")
    
    def on_connection_lost(self,tcp:Network_Client_TCP,addr):
        print(self.tag,f"Connection LOST with server: {addr}")
        
    def on_receive(self,tcp:Network_Client_TCP,msg:str,addr):
        msg = msg.split(":")
        sender  =  int(msg[0]) if msg[0].isdigit() else -1
        command_id=int(msg[1]) if msg[1].isdigit() else -1
        data=[]
        for i in range(2,len(msg)):
            data.append(msg[i])
        if command_id == ServerHandler.COMMAND_POSITION_STATUS_CHANGE:
            if self.listener_position_change != None:
                self.listener_position_change(sender,data)
        elif command_id == ServerHandler.COMMAND_ERROR:
           if self.listener_command_error != None:
               self.listener_command_error()
    
        
        
        
        
        
        