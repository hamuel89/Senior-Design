// **** INCLUDES *****
#include "SleepyPi2.h"
#include <TimeLib.h>
#include <LowPower.h>
#include <Wire.h>
#include <PCF8523.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <HC_SR04_lib.h>

// **** HW pins *****
const int ALARM_PIN      = 0;
const int BUTTON_PIN     = 1;
const int PI_IS_RUNNING  = 7;
const int LED_PIN        = 13;

const int System_power = 9; 
const int Attena_power = 10; 
const int Triger_Pin = 11;
const int Echo_Pin = 12;

const unsigned long FREQ_TIME = 30000; //  seconds * 1000
unsigned long water_level = 0,start = 0;
const float MAX_VOLT = 20, MIN_VOLT = 10;
bool timer_on = false;
bool StateOn = false;
Adafruit_INA219 battery_sensor(0x40);
HC_SR04Dev Sensor_A(Triger_Pin,Echo_Pin);

eTIMER_TIMEBASE  timer_timebase     = eTB_HOUR;   // eTB_SECOND, eTB_MINUTE, eTB_HOUR
uint8_t          timer_value        = 1;

// button
void button_isr()
{
   StateOn = false;
}

bool attena = false;
bool shut_system = false;
// I2C
void receiveEvent(int howMany)
{

  uint8_t hour = Wire.read();
  uint8_t minute = 0;

  if (255 == hour)
  {
    return;
  }
  if(hour== 1)
  { 
    SleepyPi.enableExtPower(false);
    delay(100);
    SleepyPi.enableExtPower(true);
  }    

  if(hour== 2)
  { 
      digitalWrite(Attena_power, LOW);
  }

  if(hour== 3)
  { 
     pi_off();
    shut_system = true;
  }    

  if (Wire.available() > 0) {
    minute = Wire.read();
  }

  if (0 == hour)
  {
    start = millis()+minute*60000;
    timer_on = true;
    attena = false;
    pi_off();
    digitalWrite(Attena_power, HIGH);
  }
}

void setup()
{
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  pinMode(System_power, OUTPUT);
  pinMode(Attena_power, OUTPUT);
  digitalWrite(System_power, HIGH);
  digitalWrite(Attena_power, HIGH);
  Wire.begin(4);                // join i2c bus with address #4
  Wire.onReceive(receiveEvent); // register event
  delay(50);
  battery_sensor.begin();
  battery_sensor.setCalibration_16V_400mA(); 
  
  // Allow wake up triggered by button press
  attachInterrupt(BUTTON_PIN, button_isr, LOW);
  
  SleepyPi.rtcInit(true);

  // initialize serial communication: In Arduino IDE use "Serial Monitor"
  Serial.begin(115200);
  delay(50);
  
}

void pi_on()
{
  if(voltage_ok())
  {
    StateOn = true;
    SleepyPi.enablePiPower(true);
    digitalWrite(LED_PIN, HIGH);
  }
}

void pi_off()
{
  SleepyPi.piShutdown();
  digitalWrite(LED_PIN, LOW);
}

void timer_check()
{

  if (millis() - start < 2000 && timer_on)
  {
    timer_on = false;
    StateOn = false;
  }
}


bool should_pi_turn_On()
{
  if(!SleepyPi.checkPiStatus(false) && !StateOn)
    return true;
  return false;
}
void Check_water_level()
{
   if (Sensor_A.Sync() == HC_SR04_READ_OK)
  {
    water_level = Sensor_A.Read();
  }
}
bool voltage_ok()
{
  float  temp =Check_Voltage();
  if(temp > MIN_VOLT && temp < MAX_VOLT)
    return true;
  return false;
}
float Check_Voltage()
{
  battery_sensor.powerSave(false);
  delay(20);
  float busvoltage = battery_sensor.getBusVoltage_V();
  battery_sensor.powerSave(true);
  return busvoltage;
}
void Should_transmit_water()
{
 if (Serial.available() > 0)
 {
  Serial.read();
  Check_water_level();
  Serial.println(water_level,DEC);
 }
}
unsigned long systemcheck = 0;
float voltage = 0,current = 0;
int count = 0;
void loop() 
{

 if(millis() - systemcheck > FREQ_TIME)
  {
    if(SleepyPi.checkPiStatus(false))
      StateOn = true;
    if(should_pi_turn_On())
      pi_on() ;
    

    Check_water_level();
    if(water_level < 40);
       StateOn = true;
    systemcheck = millis();
  }

  if(!SleepyPi.checkPiStatus(false) && shut_system)
  {
    delay(10000);
    digitalWrite(System_power, LOW);    
  }
  timer_check();
  Should_transmit_water();
  delay(10);
 
}
