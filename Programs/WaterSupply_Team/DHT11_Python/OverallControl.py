import RPi.GPIO as GPIO
import gpiozero
import time
import schedule
import datetime
import dht11

# GPIO番号指定のモード設定
GPIO.setmode(GPIO.BCM)

# Pomp initialization process
PIN_AIN1 = 18
pin = gpiozero.DigitalOutputDevice(PIN_AIN1)

# Soil Sensor initialization process
# センサーのDOピン番号
DO_PIN = 17
# ピンを入力モードに設定
GPIO.setup(DO_PIN, GPIO.IN)


# temperature sensor initialization process
# read data using pin 14
instance = dht11.DHT11(pin=14)


def waterSupply():
	print ("I'm working...")
	try:
		PIN_AIN1 = 18
		for i in range(1, 3, 1):
			pin.on()
			time.sleep(1.0)
			pin.off()
			time.sleep(0.8)
	finally:
		pin.close()




schedule.every().day.at("10:10").do(waterSupply)
print ("program start")



while True:
    now = datetime.datetime.now()
    schedule.run_pending()

    # Soil Condition
    sensor_value = GPIO.input(DO_PIN)
    if sensor_value == 0:
        print("Soil: Moisture")
    else:
        print("Soil: Dryness, ")

    # Temperature
    result = instance.read()
    if result.is_valid():
        print("Last valid input: " + str(datetime.datetime.now()))
        print("Temperature: %-3.1f C" % result.temperature)
        print("Humidity: %-3.1f %%" % result.humidity)
        print("-----------------------------------------------------")

    time.sleep(60)



