#Sensor class for all INA219 and Water level sensors
#Read voltages
from ina219 import INA219
from ina219 import DeviceRangeError
import time
import threading
import serial
import smbus
import requests
class Sensor():
    def __init__(self, bat_addr = 0x40, sol_addr = 0x41,bmu_addr = 0x44):
            SHUNT_OHMS = 0.1
            MAX_AMP = 2.0

            self.temperature = 20
            self.speedSound = 17150
            self.__bat_addr = bat_addr
            self.__sol_addr = sol_addr
            self.__bmu_addr = bmu_addr
            self.__SANE_MAX_VOLT = 20.00
            self.__SANE_MIN_VOLT = 10.00 
            self.__SANE_MAX_CURRENT = 1000.00
            self.__SANE_MIN_CURRENT = -2000.00
            self.READINGS = 5
            self.__water = serial.Serial('/dev/ttyS0',115200)
            self.__bat = INA219(SHUNT_OHMS,MAX_AMP,address=bat_addr)
            self.__solar = INA219(SHUNT_OHMS,MAX_AMP,address=sol_addr)
            self.__bmu = INA219(SHUNT_OHMS,MAX_AMP,address=bmu_addr)

    def Config_Sensors(self):
            try:
                self.__bat.reset()
                self.__bat.configure(self.__bat.RANGE_16V,bus_adc=self.__bat.ADC_32SAMP,shunt_adc=self.__bat.ADC_32SAMP)
            except OSError as e :
                pass
            try:
                self.__solar.reset()
                self.__solar.configure(self.__bat.RANGE_16V,bus_adc=self.__bat.ADC_32SAMP,shunt_adc=self.__bat.ADC_32SAMP)
            except OSError as e :
                pass
            try:
                self.__bmu.reset()
                self.__bmu.configure(self.__bat.RANGE_16V,bus_adc=self.__bat.ADC_32SAMP,shunt_adc=self.__bat.ADC_32SAMP)
            except OSError as e :
                pass
                   
    #Accepts choice(str)
    #valid choice return tuple(int,bool)
    #invalid choice return false

    def read_voltage(self,choice):
        switcher = { "bat" : self.__bat_voltage,
                      "solar": self.__sol_voltage,
                    "bmu" : self.__bmu_voltage
                   }
        func = switcher.get(choice, lambda: False)
        try:
            return func()
        
        except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
            print(e)

    #Accepts choice(str)
    #valid choice return tuple(int,bool)
    #invalid choice return false

    def read_current(self,choice):
        switcher = { "bat" : self.__bat_current,
                    "solar": self.__sol_current,
                    "bmu" : self.__bmu_current
                   }
        
        func = switcher.get(choice, lambda: False)
        try:
           return func()
        except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
            print(e)

    def __bat_voltage(self):
        try:
          self.__bat.wake()
          time.sleep(.02)
          voltage = self.__bat.supply_voltage()
        except:
              return (0, 4)
        return (round(voltage,2),self.__sane_voltage(voltage))

    def __bmu_voltage(self):
        try:
          self.__bmu.wake()
          time.sleep(.02)
          voltage = self.__bmu.voltage()
        except:
          return (0, 4)
    
        return (round(voltage,2),self.__sane_voltage(voltage))
    def __sol_voltage(self):
        try:
            self.__solar.wake()
            voltage = self.__solar.voltage()
        except:
              return (0, 4)
        return (round(voltage,2),self.__sane_voltage(voltage))
            
    def __bat_current(self):
        try:
            voltage = self.__bat.current()
            time.sleep(.02)
            self.__bat.sleep()
        except:
              return (0, 4)
        return (round(voltage,2),self.__sane_current(voltage))

    def __bmu_current(self):
        try:
            voltage = self.__bmu.current()
            self.__bmu.sleep()
        except:
              return (0, 4)
        return (round(voltage,2),self.__sane_current(voltage))

    def __sol_current(self):
        try:
          voltage = self.__solar.current()
          self.__solar.sleep()
        except:
              return (0, 4)
        return (round(voltage,2),self.__sane_current(voltage))

    def __sane_voltage(self,voltage):
        if(voltage >= self.__SANE_MAX_VOLT):
                return 2
        if self.__SANE_MIN_VOLT >= voltage:
                return 1
        return -1
    def __sane_current(self,current):
        if(current >= self.__SANE_MAX_CURRENT):
            return 2
        if(self.__SANE_MIN_CURRENT >= current):
           return 1
        return -1

# -----------------------
# Define Water level functions
# -----------------------

    def _measure_water_level(self):
        self.__water.write(b'1');
        temp = self.__water.readline()
        return int(temp.decode('utf-8'))
        

    def __sane_water_level(self,distance):
        if distance <= 0:
            return 2
        if distance > 240 :
            return 1
        return -1
    def measure_water_level(self):
        # This function takes 3 measurements and
        # returns the average.s

        distance1=self._measure_water_level()
        distance2=self._measure_water_level()
        distance3=self._measure_water_level()
        distance = distance1 + distance2 + distance3
        distance = distance / 3
        return (round(distance,2), self.__sane_water_level(distance))

    def Cleanup():
           GPIO.cleanup()

    def boot_antenna(self):
        boot = True
        TIMEOUT = 130
        bus  = smbus.SMBus(1)
        bus.write_byte_data(0x04,0x02,0x00)
        start = time.time()
        request = None
        while boot and time.time() - start <= TIMEOUT:
            boot2 = False
            while not boot2 and time.time() - start <= TIMEOUT:
                try:
                    time.sleep(1)
                    print(time.time() - start)
                    request = requests.get('http://192.168.1.239',timeout=30)
                    boot2 = True
                except:
                    pass
            if boot2:
                request = requests.get('http://192.168.1.239',timeout=30)
                while request.status_code != 200 and time.time() - start <= TIMEOUT:
                    try:
                        request = requests.get('http://192.168.1.239',timeout=30)
                    except:
                        pass
                    time.sleep(.10)
                boot = False
        if(not boot):
            return True
        return False


if __name__ == '__main__':
   wallEE = Sensor()
   print(wallEE.boot_antenna())
   
   #print(walleEE.read_current('bat'))

