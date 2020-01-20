#Class: Creates and Maintains ledger.
#Requirements
#1.     independent class()
#2.     Data requirements
#       Sensor that are used, -1 represents no sensor data(done)
#       Alerts if they exist(Needs added)
#3.     Verfity chain(done)
import json
import hashlib
from datetime import datetime
from collections import defaultdict
import threading
import copy
class BlockChain:
    def __init__(self,client,passphase = None):
        self.chain = []
        self.client = client
        self.ip = 0
        self.lock = threading.Lock()
        self.passphrase = passphase 
        self.hasher = None
    #Block is the Block object, with and inbeeded Python object called
    #alerts needs to be added here similar to the way sensors exists
    def Set_Hasher(self):
        self.hasher = hashlib.blake2b(key = self.passphrase)
    class Block:
        def __init__(self, index,local_time,remote_time,source,sensor,alert,hash_last,hash_current,unsent = 1):
            self.index = index
            self.local_time = local_time
            self.remote_time = remote_time
            self.source = source
            self.sensor = sensor
            self.alert = alert
            self.hash_last = hash_last
            self.hash_current = hash_current
            self.unsent = unsent

    class Serializer(json.JSONEncoder):
        def default(self, obj):
            if(isinstance(obj,BlockChain.Block)):
                sensors = copy.deepcopy(obj.sensor.__dict__)
                alert = copy.deepcopy(obj.alert.__dict__)
                del_temp = []
                #deletes the empy cells of sensor so they aren't saved and take up space.
                if(len(sensors) > 0):
                    for items in sensors:
                        if sensors[items] == -1:
                            del_temp.append(items)
                    for dels in del_temp:
                        del sensors[dels]
                    del_temp.clear()
                else:
                    sensors = None
                if(len(alert)>0):
                    for items in alert:
                        if alert[items] == -1:
                            del_temp.append(items)
                    for dels in del_temp:
                        del alert[dels]
                else:
                        alert = None
            return {
                            "index": obj.index,
                            "local_time": obj.local_time,
                            "remote_time": obj.remote_time,
                            "source" : obj.source,
                            "sensor" : [sensors],
                            "alert": [alert],
                            "hash_last": obj.hash_last
                        }
            return json.JSONEncoder.default(self, obj)

#Object that contains sensor data for easy finding. with constructor.
#Constructor requires a Dictionary be passed to it, the decodes the dictionary to
#Create parameters
# Starts out setting all parameters to (-1) the value for unused.
# Add  any new sensor to list both start and under elements
    class information:
        def __init__(self, d):
            self.sen = -1
            self.alt = -1
            self.v_battery = -1
            self.c_battery = -1
            self.v_solar = -1
            self.c_solar = -1
            self.v_trunk = -1
            self.c_trunk = -1
            self.water_level= -1
            self.network = -1
            for element in d:
                    if element == 'sen':
                        self.sen = d['sen']
                    if element == 'alt':
                        self.alt = d['alt']
                    if element in [ 'v_battery', 'vbat']:
                        self.v_battery = d[element]
                    elif element in ['c_battery', 'cbat']:
                        self.c_battery = d[element]
                    elif element in ['v_solar','vso']:
                        self.v_solar = d[element]
                    elif element in ['c_solar','cso']:
                        self.c_solar = d[element]
                    elif element in ['v_trunk', 'vtr']:
                        self.v_trunk = d[element]
                    elif element in ['c_trunk','ctr']:
                        self.c_trunk = d[element]
                    elif element in ['water_level', 'wat']:
                        self.water_level= d[element]
                    elif element in ['network', 'net']:
                        self.network= d[element]

    #Json to Pyt12hon Encoder.
    def block_creator(self,d,sensor,alert,sensor_index,alert_index):
        sen = d.get('sen')
        alt = d.get('alt')
        if len(d):
            if (sen == 1):
                sensor.append(d)
                sensor_index = sensor_index +1
            elif alt == 1:
                alert.append(d)
                alert_index = alert_index +1
            elif sen == None and alt == None:
                if(len(self.chain) > len(sensor)):
                    sensor.append("")
                    sensor_index = sensor_index +1
                if(len(self.chain) > len(alert)):
                    sensor.append("")
                    alert_index = alert_index +1
                if('unsent' in d):
                    self.chain.append( self.Block( d['index'], d['local_time'],d['remote_time'],d['source'],self.information(sensor[sensor_index -1]),self.information(alert[alert_index -1] ), d['hash_last'],d['hash_current'],d['unsent']))
                else:
                    self.chain.append( self.Block( d['index'], d['local_time'],d['remote_time'],d['source'],self.information(sensor[sensor_index -1]),self.information(alert[alert_index -1] ), d['hash_last'],d['hash_current']))

    def Sort(self,rev):
          self.chain.sort(key=self.__indexer__,reverse = True if rev else False)
    #sorter function so blockchain is always saved by index.
    def __indexer__(self,block):
        return block.index

#Creates hashcode of current string.
    def __hash_block__(self,block):
        block_serialized = json.dumps(block,cls=self.Serializer).encode("utf-8")
        return hashlib.sha256(block_serialized).hexdigest()
        

#validates single block, Use Hasblock to create current hash and compares to what is saved.
#need w way to bring this error UP a layer, to report something is wrong in the ledger.
    def Verify_block(self,block):
        hashcode_block = self.__hash_block__(block)
        #print(hashcode_block,'c = ', block.hash_current)
        if hashcode_block != block.hash_current:
            print("Block {0} is invalid".format(block.index))
            return False
        return True
#Verifying days worth of ledger.
    def Verify_Loaded_Chain(self):
        for block in self.chain:
            self.Verify_block(block)

#creates a block from sensor data from remote site
#accepts
# log as a list, Sensor data as a string with @ ast the delimiter

    def MSG_Add_Block(self,time,client,passphrase,sensor = None,alert = None):
        sen = {}
        alt = {}
        if(len(sensor) >0):
            for element in sensor:
                split =element.split("@")
                sen.update({split[0] : split[1]})
            sen.update({'sen':1})
        
        if(len(alert)>0):
            for element in alert:
                split = element.split("@")
                split2 = split[1].split(",")
                values = []
                for value in split2 :
                    values.append(int(value))
                alt.update({split[0] : values})
            alt.update({'alt' : 1})
        self.Create_New_Block(time,client,passphrase,sen,alt,0)
    def Find_Last_Valid_Block(self):
        for i in range(len(self.chain) - 1, -1, -1):
            if(not self.Verify_block(self.chain[i])):
                 del self.chain[i]
                 
    def Create_New_Block(self,time,client,passphrase,sensor,alert,sent = 1):
           ### needs find last valid block.
               self.Find_Last_Valid_Block()
               if(not len(self.chain)):
                    self.Create_Genesis(client,passphrase)
               self.chain.append(self.Block( self.chain[-1].index+1,datetime.now().strftime("%m-%d-%Y:%H-%M-%S"),time,client,self.information(sensor),self.information(alert),self.chain[-1].hash_current,passphrase,sent))
               self.chain[-1].hash_current = self.__hash_block__(self.chain[-1])
        
       
    def Split_into_days(self):
        days = defaultdict(list)
        self.Sort(False)
        for entery in self.chain:
            key = entery.local_time.split(":")[0]
            ##(entery.alert.__dict__,entery.source,key)
            days[key].append(entery)
        return days
    
    def Create_Sensor_Block_MSG(self,block):
            msg = "{time}#vbat@{v_battery};cbat@{c_battery};vso@{v_solar};cso@{c_solar};vtr@{v_trunk};ctr@{c_trunk};wat@{water_level}".format(
                v_battery=block.sensor.v_battery,c_battery=block.sensor.c_battery,
                v_solar=block.sensor.v_solar,c_solar=block.sensor.c_solar,
                v_trunk=block.sensor.v_trunk,c_trunk=block.sensor.c_trunk,
                water_level= block.sensor.water_level,time= block.remote_time)
            msg.strip("[")
            msg.strip("]")
            return msg

    def Create_Alert_Block_MSG(self,block):
        
            msg = "vbat@{v_battery};cbat@{c_battery};vso@{v_solar};cso@{c_solar};vtr@{v_trunk};ctr@{c_trunk};wat@{water_level};net@{network}".format(
                v_battery=block.alert.v_battery,c_battery=block.alert.c_battery,
                v_solar=block.alert.v_solar,c_solar=block.alert.c_solar,
                v_trunk=block.alert.v_trunk,c_trunk=block.alert.c_trunk,
                water_level= block.alert.water_level, network = block.alert.network)
            msg = msg.replace("]", "")
            msg = msg.replace("[", "")
            msg = msg.replace(" ", "")
            return msg
    def Create_Genesis(self,client,passphrase):
        sensor = Create_Sensor(round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2))
        alert = Create_Alert([random.randint(0,2)],[random.randint(0,2)],[random.randint(0,2)], [random.randint(0,2)],[random.randint(0,2)], [random.randint(0,2)], [random.randint(0,2)])
        self.chain.append(self.Block( 'Genesis',self.Time(0),self.Time(0),client,self.information(sensor),self.information(alert),passphrase,passphrase,1))
        self.chain[-1].hash_current = self.__hash_block__(self.chain[-1])

    def Time(self,x):
        return (datetime.now()-timedelta(x)).strftime("%m-%d-%Y:%H-%M-%S")

    def __Message_Hash__(self,data):
        hash = hashlib.blake2b(digest_size=8)
        hash.update(data)
        return hash.hexdigest()
    def Set_Network_Error(self,error):
        self.chain[-1].alert.network = error
        self.chain[-1].hash_current = self.__hash_block__(self.chain[-1])
        

    #hash_last#time&(type);value@(type);value&%hash_current
    def Send_Block(self,last_hash,sensor,alert):

        message = (last_hash +"#" + sensor + "#" + alert)
        chash = self.__Message_Hash__(message.encode('utf-8'))
        
        return ((message + "#" + chash),chash)
