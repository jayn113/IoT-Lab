from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from tinydb import TinyDB
from datetime import datetime
import os
import time

VIDEO_DIR = "videos"
SEGMENT_LENGTH = 15

os.makedirs(VIDEO_DIR, exist_ok = True)

db = TinyDB("sensor_data.json")

picam2 = Picamera2()

config = picam2.create_video_configuration()
picam2.configure(config)

encoder = H264Encoder(10_000_000)

picam2.start()

time.sleep(2) # Allow exposure/focus to settle

try:
	while True:
		timestamp = datetime.now().isoformat()
		filename = os.path.join(VIDEO_DIR, f"{timestamp}.mp4")
		
		print(f"\nRecording {filename}")
		
		output = FfmpegOutput(filename)
		picam2.start_recording(encoder, output)
		
		time.sleep(SEGMENT_LENGTH)
		
		picam2.stop_recording()
		
		print("Recording finished!")
		
		# Add recording info to TinyDB
		db.insert({
			"sensor"	: "CAMERA",
			"timestamp"	: timestamp,
			"filename"	: filename
		})
		
		print("Database entry added")
		
except KeyboardInterrupt:
	print("\nStopping camera...")
	picam2.stop()
