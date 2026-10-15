from picamera2 import Picamera2
from datetime import datetime
import time
import os

picam2 = Picamera2()

config = picam2.create_still_configuration()
picam2.configure(config)

IMAGE_DIR = "images"

picam2.start()

time.sleep(2) # Allow cam to adjust focus/exposure

timestamp = datetime.now().isoformat()
filename = os.path.join(IMAGE_DIR, f"{timestamp}.jpg")

print(f"\nCapturing {filename} at {timestamp}")

picam2.capture_file(filename)

picam2.stop()

print("Image captured!")
