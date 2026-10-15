import time
from datetime import datetime
from bh1745 import BH1745

sensor = BH1745()
sensor.setup()

while True:
	print(sensor.get_rgbc_raw(), "timestamp:", datetime.now().isoformat())
	time.sleep(1)
