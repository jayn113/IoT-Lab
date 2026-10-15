from tinydb import TinyDB
from bh1745 import BH1745
from datetime import datetime
import time

db = TinyDB("data.json")
sensor_db = db.table("sensor_readings")

sensor = BH1745()
sensor.setup()

print("BH1745 setup successful. Recording data at 1s intervals...")

while True:
	red, green, blue, clear = sensor.get_rgbc_raw()
	
	db.insert({
		'sensor'	: 'BH1745',
		'timestamp' : datetime.now().isoformat(),
		'red' 		: red,
		'green'		: green,
		'blue'		: blue,
		'clear'		: clear
		})
		
	time.sleep(1)
