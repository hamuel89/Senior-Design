#Designed to load and manage encryption keys
#Requirements load both types of keys for
#Load encryption keys
#Load json files,
import os
import sys
from os import path
from pathlib import Path
from datetime import datetime , timedelta
from blockchain import BlockChain
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import copy
class Filemng:
    def __init__(self,client,blockchain= None):
        encode_key_file = 'Server_public_key.pem'
        decode_key_file =  client+'_private_key.pem'
        base_path = Path(__file__).parent
        self.encode_path = str((base_path / "key" / encode_key_file).resolve())
        self.decode_path = str((base_path / "key" / decode_key_file).resolve())
        self.clients_list_file = str((base_path / "client" / 'clients.json').resolve())
        self.secert_path = str((base_path / "key" / 'Server_private_key.pem').resolve())
        self.client_list = []
        self.client = client
        self.error = []
        self.blockchain = blockchain

    def Get_Error(self):
        return self.error

    def load_encode_key(self):
        encode_key = []
        if(path.exists(self.encode_path) and path.isfile(self.encode_path) and not os.stat(self.encode_path).st_size==0):
            with open(self.encode_path, "rb") as key_file:
                encode_key = serialization.load_pem_public_key(
                           key_file.read(),
                           backend=default_backend()
                           )
            return encode_key
        self.error.append(96)
        return False

    def load_decode_key(self):
        decode_key = []
        if(path.exists(self.decode_path) and path.isfile(self.decode_path) and not os.stat(self.decode_path).st_size==0):
            with open(self.decode_path, "rb") as key_file:
                decode_key = serialization.load_pem_private_key(
                           key_file.read(),
                           password=None,
                           backend=default_backend()
                           )
            return decode_key
        self.error.append(97)
        return False
    def Load_Spefic_key(self,client):
        decode_key = []
        base_path = Path(__file__).parent
        encode_path = str((base_path / "key" / client ).resolve())

        if(path.exists(encode_path) and path.isfile(encode_path) and not os.stat(encode_path).st_size==0):
            with open(encode_path, "rb") as key_file:
                decode_key = serialization.load_pem_public_key(
                           key_file.read(),
                           backend=default_backend()
                           )
            return decode_key
        print("94")
        self.error.append(97)
        return False

    def Load_Both_Keys(self):
        encypt = []
        encypt.append(self.load_encode_key())
        encypt.append(self.load_decode_key())

        if(not encypt[0] ):
            print("Encrypt keys not loaded")
            sys.exit()
        else:
                print("Encryption keys loaded")
        if( not encypt[1]) :
                    print("Decrypt keys not loaded")
                    sys.exit()
        else:
                 print("Decryption keys loaded")
        return encypt

    def Load_Month(self):
        for x in range(0,29):
            file = (datetime.now() - timedelta(x)).strftime("{name}-%m-%d-%Y.log").format(name=self.client.decode('UTF-8')if type(self.client) != str else self.client)
            file = Path(str((Path(__file__).parent / "log" / file)))
            if(file.exists() and file.is_file()):
                    self.__load_log__(file)
                    print(file)
        self.blockchain.Sort(False)

    def __Save_Chains__(self):
        days = self.blockchain.Split_into_days()
        for key in days:
            days[key].sort(key=self.__indexer__)
            file = self.client.decode('UTF-8')  if type(self.client) != str else self.client + "-"+ key+".log"
            file = str((Path(__file__).parent / "log" / file).resolve())
            self.__save_log__(days[key],file)

    def __indexer__(self,block):
        return block.index


    def Save_Log(self):
        self.__Save_Chains__()

    def __save_log__(self,data,file):
        with open(file, 'w+') as f:
            json.dump(data,f, cls=self.ComplexEncoder,indent=4)

    def __load_log__(self,file):
        sensor = []
        alert = []
        sensor_index = 0
        alert_index = 0

        if(file.exists() and file.is_file()):
                with open(str(file), 'r') as f:
                    json.load(f,object_hook = lambda x : self.blockchain.block_creator(x,sensor,alert,sensor_index,alert_index))
                    if len(self.blockchain.chain) != 0 :
                        return True
        print("Failed to Load data log")
        return False
    def Load_Server_Key(self):
        with open(self.secert_path, "rb") as key_file:
            print("Loaded Server Key")
            return serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                    )


    def Load_Client_List(self):
        if(path.exists(self.clients_list_file) and path.isfile(self.clients_list_file)):
            if(not os.stat(self.clients_list_file).st_size==0):
                with open(self.clients_list_file, 'r') as f:
                    json.load(f,object_hook = self.__client_creator__)
        for client in self.client_list:
            client.Set_Encode(self.Load_Spefic_key(client.public_key_file))
        print("Loaded Client list")
        return self.client_list

    def __client_creator__(self,d):
        if(  d.get('clients',False) == False):
            self.client_list.append(self.Client(d['idenifier'], d['passphrase'],d['public_key_file'],d['last_com']))


    class Client:
        def __init__(self, idcode,passphrase, decode_file,last_com):
            global base_path
            self.id = idcode.encode('utf-8')
            self.passphrase = passphrase.encode('utf-8')
            self.public_key_file = decode_file
            self.last_com = last_com
            self.encode_key = None
        def Set_Encode(self,key):
                self.encode_key = key


    #Python to Json Decoder. Used for creating string to create data log.
    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            if(not isinstance(obj,BlockChain.Block)):
                pass
            if(isinstance(obj,BlockChain.Block)):
                sensor = copy.deepcopy(obj.sensor.__dict__)
                alert = copy.deepcopy(obj.alert.__dict__)
                del_temp = []
                #deletes the empy cells of sensor so they aren't saved and take up space.
                if(len(sensor) > 0):
                    for items in sensor:
                        if sensor[items] == -1:
                            del_temp.append(items)

                    for dels in del_temp:
                        del sensor[dels]
                    del_temp.clear()
                else:
                    sensor = {'sen' :1}
                if(len(alert)>0):
                    for items in alert:
                        if alert[items] == -1:
                            del_temp.append(items)
                    for dels in del_temp:
                        del alert[dels]
                else:
                        alert = {'alt':1}
                if(obj.unsent and obj.unsent != 1):
                    obj.unsent = 1
                stiff = {
                            "index": obj.index,
                            "local_time": obj.local_time,
                            "remote_time": obj.remote_time,
                            "source" : obj.source,
                            "sensor" : sensor,
                            "alert": alert,
                            "hash_last": obj.hash_last,
                            "hash_current": obj.hash_current,
                            "unsent": obj.unsent
                        }
                return stiff
            return json.JSONEncoder.default(self, obj)


#client = 'Frank'
#blockcha = BlockChain(client)
#file = Filemng(client,blockcha)
#stuff = file.Load_Both_Keys()
#file.Load_Month()
"""
for element in blockcha:
    d[element.remote_time] = element.sensor.v_battery * element.sensor.c_battery

for key, value in d:
    plot(k,value)

for element in blockcha:
     if len(element.alert.v_battery):
         process alert"""

