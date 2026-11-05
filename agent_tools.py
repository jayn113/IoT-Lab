from tinydb import TinyDB
from bh1745 import BH1745
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import time
import os


# BH1745 sensor setup
sensor = BH1745()
sensor.setup()

# TinyDB setup
db = TinyDB("data.json")
sensor_db = db.table("sensor_readings")
camera_db = db.table("camera_records")

# Camera setup
picam2 = Picamera2()
img_config = picam2.create_still_configuration()
vid_config = picam2.create_video_configuration()


def get_sensor_status():
    if sensor.ready():
        return {
            "DEVICE": "BH1745",
            "STATUS": "online",
            "TIMESTAMP": datetime.now().isoformat()
        }
    else:
        return {
            "DEVICE": "BH1745",
            "STATUS": "offline",
            "TIMESTAMP": datetime.now().isoformat()
        }


def read_light_sensor():
    red, green, blue, clear = sensor.get_rgbc_raw()
    
    sensor_db.insert({
		"DEVICE"	: "BH1745",
		"RED" 		: red,
		"GREEN"		: green,
		"BLUE"		: blue,
		"CLEAR"		: clear,
		"TIMESTAMP" : datetime.now().isoformat()

	})
	
    return {
        "SOURCE": "LIVE BH1745",
        "RED": red,
        "GREEN": green,
        "BLUE": blue,
        "CLEAR": clear
        "TIMESTAMP": datetime.now().isoformat()

    }


def get_latest_sensor_reading():
    records = sensor_db.all()

    if not records:
        return {"ERROR": "No sensor DATA found"}

    return "SOURCE: SENSOR DATABASE", records[-1]


def get_latest_camera_metadata():
    records = camera_db.all()

    if not records:
        return {"ERROR": "No camera data found"}

    return "SOURCE: CAMERA DATABASE", records[-1]


def cam_capture_image():
    picam2.configure(img_config)

    IMAGE_DIR = "images"
    os.makedirs(IMAGE_DIR, exist_ok=True)

    try:
        picam2.start()
        time.sleep(2)  # Allow cam to adjust focus/exposure

        timestamp = datetime.now().isoformat()
        filename_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(IMAGE_DIR, f"{filename_timestamp}.jpg")

        picam2.capture_file(filename)

        camera_db.insert({
            "DEVICE": "CAMERA",
            "TYPE": "IMAGE",
            "TIMESTAMP": timestamp,
            "FILENAME": filename
        })

        return {
            "DEVICE": "CAMERA",
            "TYPE": "IMAGE",
            "TIMESTAMP": timestamp,
            "FILE_NAME": filename
        }

    finally:
        picam2.stop()


def cam_record_video():
    picam2.configure(vid_config)

    VIDEO_DIR = "videos"
    SEGMENT_LENGTH = 15

    os.makedirs(VIDEO_DIR, exist_ok=True)

    try:
        picam2.start()
        time.sleep(2)  # Allow exposure/focus to settle

        timestamp = datetime.now().isoformat()
        filename_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(VIDEO_DIR, f"{filename_timestamp}.mp4")

        encoder = H264Encoder(10_000_000)
        output = FfmpegOutput(filename)

        picam2.start_recording(encoder, output)

        try:
            time.sleep(SEGMENT_LENGTH)
        finally:
            picam2.stop_recording()

        camera_db.insert({
            "DEVICE": "CAMERA",
            "TYPE": "VIDEO",
            "TIMESTAMP": timestamp,
            "DURATION_SEC": SEGMENT_LENGTH,
            "FILENAME": filename
        })

        return {
            "DEVICE": "CAMERA",
            "TYPE": "VIDEO",
            "TIMESTAMP": timestamp,
            "DURATION_SECONDS": SEGMENT_LENGTH,
            "FILE_NAME": filename
        }

    finally:
        picam2.stop()
