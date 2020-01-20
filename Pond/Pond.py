##Main Python script for Ingram readymix remote monitoring sight
##Hardware Required:
##Rasberry Pi
##SleepPi 2
##Wifi Attena
##LANDZO 2 Channel Relay Module Expansion Board for Arduino Raspberry Pi DSP AVR PIC ARM Note: JD-VCC is 5V and VCC is 3v3, Remove jumper to accomidate this.
##INA219 Voltage && Current Sensor
##JSN-SR04T Integrated Ultrasonic Distance Sensor
##Communications I2C, TCP, Uart.
##Description:
##Script is Ran when ever the rasberry Pi turns on1.
##Script will attempt to connect to sensors and pull data, if a failure it accures it will attempt to reconfigure sensor, If Issue presits will attempt to power down Sensor array 
##Will then decide if water level is to high or if packets haven't been transmitted, if high water level or transmisstion is required will attempt to turn on attenna.
##Depending on attena state it will either tramsitte or wait for attenna to power. System will determine attena boots or fails. if failure accures it will attempt to boot attenna again
##or restart the whole system.After water level is low, or tranmissions aren't required system will set a timer and reboot. 

from tcp import TCP
from filemng import Filemng
from blockchain import BlockChain
from datetime import datetime,timedelta
import time
import queue
import random
import smbus
from Sensor import Sensor
import sys
passphrase = 'sexychicken'
client = 'Frank'
last_hash = passphrase
host = "192.168.1.3"
port = 2004
MAX_WATER_LEVEL = 60
UNSENT_SEND = 7

##Function Description: Sends I2C command to SleepPi to turn off external power bus.
def turn_off_external_power():
    bus  = smbus.SMBus(1)
    bus.write_byte_data(0x04,0x01,0x00)

##Function Description: Pulls data from all 3 INA219 and Water level Sensor class.
##Sensor readings then turn into a two different lists one of sensor readings, Second a list of errors that accured while reading sensors
##Required Inputs: Initialized sensor class, Intialized Chain class.

def __Collect_Sensor_value(sensor,chain):
    sensor_list = ["bat" ,"bmu","solar"]
    voltage_value = []
    current_value = []
    error = 0
    value = get_v_bat(sensor,chain)
    voltage_value.append(value)
    value = get_c_bat(sensor,chain)
    current_value.append(value)
    value = get_v_solar(sensor,chain)
    voltage_value.append(value)
    value = get_c_solar(sensor,chain)
    current_value.append(value)
    value = get_v_bmu(sensor,chain)
    voltage_value.append(value)
    value = get_c_bmu(sensor,chain)
    current_value.append(value)
           
    water_level = sensor.measure_water_level()
    sensor_readings = Create_Sensor(voltage_value[0][0],current_value[0][0],
                                    voltage_value[1][0],current_value[1][0],
                                    voltage_value[2][0],current_value[2][0],
                                    water_level[0])
    alert_readings = Create_Alert(voltage_value[0][1],current_value[0][1],
                                    voltage_value[1][1],current_value[1][1],
                                    voltage_value[2][1],current_value[2][1],
                                    water_level[1])
    
    return (sensor_readings,alert_readings)

##Function Description: Pulls data from all 3 INA219 Sensors via Sensor class and checks voltage sensors for any know 
##Sensor readings then turn into a two different lists one of sensor readings, Second a list of errors that accured while reading sensors
##Required Inputs: Initialized sensor class, Intialized Chain class.

def get_v_bat(sensor,chain):
    error = 0;
    value = sensor.read_voltage('bat')
    while  value[0] == int(chain.chain[-1].sensor.v_battery) and error < 5 :
        value = sensor.read_voltage('bat')
        error  += 1
        if(error == 4):
            sensor.Config_Sensors()
            time.sleep(1)
            value = sensor.read_voltage('bat')
        elif error ==5:
            turn_off_external_power()
            time.sleep(1)
            value = sensor.read_voltage('bat')
    if(value[0] == int(chain.chain[-1].sensor.v_battery)):
                value = (value[0] , 3)
    return value

def get_v_bmu(sensor,chain):
    error = 0;
    value = sensor.read_voltage('bmu')
    while  value[0] == int(chain.chain[-1].sensor.v_trunk) and error <= 5:
        value = sensor.read_voltage('bmu')
        error  += 1
        if(error == 4):
            sensor.Config_Sensors()
            time.sleep(1)
            value = sensor.read_voltage('bmu')
        elif error ==5:
            turn_off_external_power()
            time.sleep(1)
            value = sensor.read_voltage('bmu')
    if(value[0] == int(chain.chain[-1].sensor.v_trunk)):
        value = (value[0] , 3)
    return value

def get_v_solar(sensor,chain):
    error = 0;
    value = sensor.read_voltage('solar')
    while  value[0] == int(chain.chain[-1].sensor.v_solar) and error <= 5:
        value = sensor.read_voltage('solar')
        error  += 1
        if(error >= 4):
            sensor.Config_Sensors()
            time.sleep(1)
            value = sensor.read_voltage('solar')
        elif error ==5:
            turn_off_external_power()
            time.sleep(1)
            value = sensor.read_voltage('solar')
    if(value[0] == int(chain.chain[-1].sensor.v_solar)):
          value = (value[0] , 3)
    return value

def get_c_bat(sensor,chain):
    error = 0;
    value = sensor.read_current('bat')
    while  value[0] == int(chain.chain[-1].sensor.c_battery) and error <= 5:
        value = sensor.read_current('bat')
        error  += 1
        if(error >= 4):
            sensor.Config_Sensors()
            time.sleep(1)
            value = sensor.read_current('bat')
        elif error ==5:
            turn_off_external_power()
            time.sleep(1)
            value = sensor.read_current('bat')
    if(value[0] == int(chain.chain[-1].sensor.c_battery)):
            value = (value[0] , 3)
    return value

def get_c_bmu(sensor,chain):
    error = 0;
    value = sensor.read_current('bmu')
    while  value[0] == int(chain.chain[-1].sensor.c_trunk) and error <= 5:
        value = sensor.read_current('bmu')
        error  += 1
        if(error >= 4):
            sensor.Config_Sensors()
            time.sleep(1)
            value = sensor.read_current('bmu')
        elif error ==5:
            turn_off_external_power()
            time.sleep(1)
            value = sensor.read_current('bmu')
    if(value[0] == int(chain.chain[-1].sensor.c_trunk)):
                value = (value[0] , 3)
    return value

def get_c_solar(sensor,chain):
    error = 0;
    value = sensor.read_current('solar')
    while  value[0] == int(chain.chain[-1].sensor.c_solar) and error <= 5:
        value = sensor.read_current('solar')
        error  += 1
        if(error >= 4):
            sensor.Config_Sensors()
            time.sleep(1)
            value = sensor.read_current('solar')
        elif error ==5:
            turn_off_external_power()
            time.sleep(1)
            value = sensor.read_current('solar')
    if(value[0] == int(chain.chain[-1].sensor.c_solar)):
            value = (value[0] , 3)
    
    return value


def Collect_Sensor(chain,sensors):
    global client,passphrase,host,port
    block_values = __Collect_Sensor_value(sensors,chain)
    chain.Create_New_Block(Time(0),host,passphrase,block_values[0],block_values[1])
def Time(x):
    return (datetime.now()-timedelta(x)).strftime("%m-%d-%Y:%H-%M-%S")

def Create_Sensor(v_battery = -1,c_battery= -1,v_solar= -1,c_solar= -1,v_trunk= -1,c_trunk= -1,water_level= -1):
    sensor ={'sen':1,'v_battery' : v_battery, "c_battery" : c_battery, "v_solar" : v_solar,
                 "c_solar" : c_solar, "v_trunk" : v_trunk, "c_trunk" : c_trunk, "water_level" : water_level }
    return sensor
def Create_Alert(v_battery = -1,c_battery= -1,v_solar= -1,c_solar= -1,v_trunk= -1,c_trunk= -1,water_level= -1, network =-1):
    alert ={'alt':1,
            'v_battery' : v_battery, "c_battery" : c_battery,
            "v_solar" : v_solar,     "c_solar" : c_solar,
            "v_trunk" : v_trunk, "c_trunk" : c_trunk,
            "water_level" : water_level,
            "network": network}

    return alert

def Create_Test_Alert():
    alert = Create_Alert([random.randint(0,14)],
                          [random.randint(0,14)],
                          [random.randint(0,14)],
                          [random.randint(0,14)],
                          [random.randint(0,14)],
                          [random.randint(0,14),random.randint(0,14)],
                          [random.randint(0,14),random.randint(0,14)],
                          [random.randint(0,14),random.randint(0,14)])
    return alert


def Create_Test_Sensor():
    sensor = Create_Sensor(round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2),round(random.uniform(0,14),2))
    return sensor
def Start_Comm(comm):
        comm.start()
        
  
def main(*args,**kwargs):
    start = time.time()
    global client,passphrase,host,port
    network = []
    chain = BlockChain(client,passphrase)
    files = Filemng(client,chain)
    encrypt = files.Load_Both_Keys()
    files.Load_Month()
    print("Loading Logs")
    sensors = Sensor()
    sensors.Config_Sensors()
    print("Configued Sensors")
    que = queue.Queue()
    send_que = queue.Queue()
    recv_que = queue.Queue()
    comm = TCP(encrypt,passphrase,host,port,que,send_que,recv_que)
 
    Showdown = False
    while not Showdown :
        print("Collecting Sensors data")
        Collect_Sensor(chain,sensors)
        print("Saving Log")
        files.Save_Log()
        error = 0
        transmit = False
        water_count  = 0
        print("Checking Water level/Levels")
        if(float(chain.chain[-1].sensor.water_level) < MAX_WATER_LEVEL and float(chain.chain[-1].sensor.water_level) != 0.00 or 0 < water_count <= 10 ):
            if(float(chain.chain[-1].sensor.water_level) < MAX_WATER_LEVEL):
                water_count =0
            water_count +=1
            attenna_status = True #sensors.boot_antenna()
            while( not attenna_status and not Showdown):
                attenna_status = sensors.boot_antenna()
                error +=1
                if(error >= 3):
                    chain.Set_Network_Error(112)
                    Shutdown(files)
                    Showdown = True
            if(not comm.State):
                Start_Comm(comm)
                time.sleep(1)
            print("Water level High")
            transmit = True
        print("Checking Unsent Object")    
        if(Check_Unsent_Blocks(chain) > UNSENT_SEND and not transmit):
            attenna_status = True #sensors.boot_antenna()
            while( not attenna_status and not Showdown):
                attenna_status = sensors.boot_antenna()
                error +=1
                if(error >= 3):
                    chain.Set_Network_Error(112)
                    Shutdown(files)
                    Showdown = True
            if(not comm.State):
                Start_Comm(comm)
                time.sleep(1)
            print("Unsent blocks High")
            transmit = True

        if(transmit):
            Send_Blocks(chain,send_que)
            time.sleep(5)
            Remove_blocks(chain,recv_que)
            print("Transmitting")
        else:
            print("Nothing to transmitt")
            files.Save_Log()
            Showdown = True

        if not que.empty():
            network.append(que.get())
        if(len(network)>0):
            chain.Set_Network_Error(network[0][0])
            if(network[0][0] == 111):
                Showdown = True
        time.sleep(2)
        print("Cycling ")
    print("Shutting Down")
    Soft_Shutdown(files,comm)
    

def Check_Unsent_Blocks(chain):
    count = 0
    for block in chain.chain:
        if block.unsent == 1:
            count +=1
    return count

def Send_Blocks(chain,send_que):
 global last_hash
 for block in chain.chain:
        if block.unsent == 1:
            sensor = chain.Create_Sensor_Block_MSG(block)
            alert = chain.Create_Alert_Block_MSG(block)
            message = chain.Send_Block(last_hash,sensor,alert)
            block.unsent = message[1] 
            last_hash = message[1]
            send_que.put(message[0])
            
def Remove_blocks(chain,recv_que):
        while(not recv_que.empty()):
            lhash = recv_que.get().decode('utf-8')
            for i in range(len(chain.chain) - 1, -1, -1):
                if chain.chain[i].unsent == lhash:
                    del chain.chain[i]
                    
def Soft_Shutdown(files,comm):
    files.Save_Log()
    print("Exit Program")
    if(comm.State):
        comm.State = False
        comm.join()
    time.sleep(1)
	##Remove comments when system goes live so it will restart correctly
    #bus  = smbus.SMBus(1)
    #bus.write_byte_data(0x04,0x00,0x01)
    sys.exit()

def Shutdown(files):
    files.Save_Log()
    time.sleep(1)
    #from subprocess import call
    print("System Reset")
	##Remove comments when system goes live so it will restart correctly
    #bus  = smbus.SMBus(1)
    #bus.write_byte_data(0x04,0x03,0x00)

if __name__ == "__main__":
    main()
