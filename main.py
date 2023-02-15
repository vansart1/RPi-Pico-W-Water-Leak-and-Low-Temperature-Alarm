import network
import ntpclient
import time
import config
from machine import ADC, Pin



#set up variables
led = Pin("LED", Pin.OUT)
alarm = Pin(2, Pin.OUT)
test_button = Pin(3, Pin.IN)
moisture_sensor = ADC(0)
temp_sensor = ADC(4)


#initialize variables
led.value(0)
alarm.value(0)
moisture_alert_time = 0
cold_alert_time = 0


#set up wifi
wlan = None
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()
time.sleep(0.2)


#functions
def send_alert(message, last_alert_time):
    current_time = time.time()
    time_since_last_alert = current_time - last_alert_time
    print(f"Time since last alert is {time_since_last_alert} seconds")
    if time_since_last_alert > config.ALERT_TIME_INTERVAL:
        print(f"Sending alert message: {message}")
    
    return current_time


#------------ main program loop start ---------------------
while True:
    #----- connect to wifi
    if not wlan.isconnected():

        print(f"Connecting to Wi-Fi SSID: {config.WIFI_SSID}")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

        while not wlan.isconnected():
            time.sleep(0.5)

        #get & set time from NTP server
        try:
            ntpclient.settime()
        except OSError:
            print("Failed to get Network time")
            led.value(1)
            time.sleep(10)

        print(f"Connected to Wi-Fi SSID: {config.WIFI_SSID}")
        
        #blink LED and sound chirp to show wifi is configured
        led.value(1)
        alarm.value(1)
        time.sleep(.2)
        led.value(0)
        alarm.value(0)

    #----- get board temp
    temp_raw = temp_sensor.read_u16()
    temp_volts = temp_raw * ( 3.3 / 65535 )
    temp_c = 27 - ( temp_volts - 0.706 ) / 0.001721
    temp_f = temp_c * 9 / 5 + 32
    print(f"Temperature is {temp_f} degrees Farenheight")
    
    #----- get moisture level
    moisture_raw = moisture_sensor.read_u16()
    moisture = moisture_raw * ( 100.0 / 65535 )
    print(f"Moisure level is {moisture}")
    
    #----- get test button state
    test_mode = test_button.value()
    print(f"Test mode status is {test_mode}")

    
    #----- alert based on sensors
    if (moisture > config.MOISTURE_ALARM_THRESHOLD) or (temp_f < config.COLD_ALERT_THRESHOLD) or (test_mode == True):
        led.value(1)
        alarm.value(1)
        #if wet
        if moisture > config.MOISTURE_ALARM_THRESHOLD:
            moisture_alert_time = send_alert("Its WET!!!", moisture_alert_time)
        #if too cold    
        if temp_f < config.COLD_ALERT_THRESHOLD:
            cold_alert_time = send_alert("Its cold!", cold_alert_time)
        #if test button pressed    
        if test_mode == True:
            send_alert("Just a test!", 0)
    else:
        led.value(0)
        alarm.value(0)
   
    print(time.time())    
    time.sleep(3)
#------------ main program loop end ---------------------
    
    

