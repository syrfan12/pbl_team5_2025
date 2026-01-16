import gpiozero
import time
import schedule
import datetime

PIN_AIN1 = 18

pin = gpiozero.DigitalOutputDevice(PIN_AIN1)

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
	time.sleep(60)




