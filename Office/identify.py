#Client class is a python object the contains information about clients that exist
#ACCEPTS
# IDCODE,PASSPHRASE,DECODE_KEY,Last Com
#IDENIFTy class is designed for uasge of commands and encrpyt after someone has
#been found on client list.
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime


#Object that holds all data for client info, aka encode/decode keys, last_c
class Identify():
    def __init__(self,ip,port,server_key,filemng):
        self.idenity = ''
        self.encode = None
        self.last_com = 0
        self.ip = ip
        self.port = port
        self.server_key = server_key
        self.log = []
        self.hash_last = 0
        self.chain = []
        self.files = filemng
        self.passphrase = None

    def find_client_keys(self,data,client_list):

        print("Finding ID:")

        for client in client_list:

            if client.passphrase == self.Decrypt(data):
                self.idenity = client.id
                self.encode = client.encode_key
                self.last_com = client.last_com
                self.chain = client.chain
                self.chain.ip = self.ip
                self.hash_last = client.passphrase.decode('utf-8')
                self.passphrase = client.passphrase
                print("Client {0} has connected to server".format(client.id))
                return client
        print("No Id Found")
        return False

    def Decrypt(self,data):
        try:
            return self.server_key.decrypt(data,padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None)
            )
        except :
            return False

    def Encrypt(self,data):
        try:
            return self.encode.encrypt(data,padding.OAEP(
                                               mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                               algorithm=hashes.SHA256(),
                                               label=None
                                                        )
                                       )
        except :
            return False

    def Update_Last_Com(self):
        self.last_com = datetime.datetime.now().timestamp()
    def Load_Log(self):
        self.files.Set_Lock()
        try:
            self.files.Set_Client_and_Chain(self.idenity,self.chain)
            self.chain.passhprass = self.passphrase
            print('load')
            self.chain.Set_Hasher()
            self.files.Load_Month()
            print("Loaded {name} logs".format(name=self.idenity))
        finally:
            self.files.Release_Lock()
    def Save_Log(self):
        self.files.Set_Lock()
        try:
            self.files.Set_Client_and_Chain(self.idenity,self.chain)
            self.chain.passhprass = self.passphrase 
            self.files.Save_Log()
            print("Saved {name} logs".format(name=self.idenity))
        finally:
            self.files.Release_Lock()
    #data is in below format
    # hash_last&time&(kind)&(type);value@(type);value&%hash_current
    #***(8)****(19)**(3)****(5)***(5)****************(8)
    #Time is in "%m-%d-%Y:%H-%M-%S" format
    #FUnction decodes data and executes correct function.
    #log,time,client,sensor = None,alert = None
    def Command(self,data):
        data = data.decode('UTF-8')
        splitstring = data.split('#')
        sensor = splitstring[2].split(';')
        alert = splitstring[3].split(';')
        lhash = splitstring[0]
        if(lhash == self.hash_last):
            self.hash_last = splitstring[-1]
        time = splitstring[1]
        self.chain.MSG_Add_Block(time,self.ip,self.passphrase,sensor,alert)
        self.Save_Log()





    #executes off of data[2]
#x = Identify("127.0.0.1","98")

#x.find_client_keys(x.Encrypt(b'Frank12'))
#data = x.Encrypt(b'data')
#print(x.Decrypt(data))
