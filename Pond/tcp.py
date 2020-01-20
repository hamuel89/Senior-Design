#communication file
import socket
import queue
import hashlib
import time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from threading import Thread

class TCP(Thread):
    def __init__(self,encrypt,passphrase,host,port,que,send_que,recv_que):
        Thread.__init__(self)
        self.encode_key = encrypt[0]
        self.decode_key = encrypt[1]
        self.host = str(host)
        self.port = int(port)
        self.passphrase = passphrase
        self.error = []
        self.que = que
        self.recv_que = recv_que
        self.tcpClient =[]
        self.BUFFER_SIZE = 2000
        self.message_que = send_que
        self.State = False
        self.last_hash = passphrase
        self.error_start = 0
    def run(self):
        try:
            self.State = True
            self.Connect()
            if(self.EstablishIdenity()):
                print("Connected to Server")
                self.Connected_State()

            self.que.put(100)
            self.tcpClient.close()

        except socket.error as e :
            self.que.put(e.args)
            self.error_start += 1
            
            
    def Connected_State(self):
            self.State = True
            self.error_start  = 0
            self.tcpClient.setblocking(0)
            while self.State:
                data = ""
                try:
                    data = self.tcpClient.recv(256)
                    #print(self.Decrypt(data))
                    self.recv_que.put_nowait(self.Decrypt(data))
                except socket.error as e:
                    if  e.args[0] == 10035:
                        pass
                finally:
                    if not self.message_que.empty():
                        next_msg = self.message_que.get()
                        self.Send(next_msg)
                        

    def Connect(self):
        self.tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClient.connect((self.host, self.port))

    def EstablishIdenity(self):
        self.tcpClient.send(self.Encrypt(self.passphrase.encode('utf-8')))
        if(self.Decrypt(self.tcpClient.recv(self.BUFFER_SIZE)) == self.passphrase.encode('utf-8')):
            return True
        return False

    def Send(self,Message):
        msg = self.Encrypt(Message.encode('utf-8'))
        if msg :
            self.tcpClient.send(msg)

    def Encrypt(self,data):
        try:

            return self.encode_key.encrypt(data,padding.OAEP(
                       mgf=padding.MGF1(algorithm=hashes.SHA256()),
                       algorithm=hashes.SHA256(),
                       label=None)
                )
        except Exception as msg:
            print("Failed to encoded transmission, Transmission discarded,data   ",msg,len(data))
            self.que.put(99)
            return False

    def Decrypt(self,data):
        try:
                return self.decode_key.decrypt(data,padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None)
                )
        except :
            print("Failed to decode transsion, Transmission discarded")
            self.que.put(98)
            return False





