#!/usr/bin/python3
# Face detection for Raspberry Pi 5 + Camera Module 3 (Picamera2 + OpenCV Haar cascade)
# Run from the Pi desktop:  python3 face_detect.py      Press q in the video window to quit.

import cv2
import os
import time
from picamera2 import Picamera2
from libcamera import controls

# Look for files next to this script, no matter which folder you run it from
SCRIPT_DIR = os.path.dirname(os.path.abspath("/home/jayn/IOT-Lab/Face-Detection-Data/haarcascade_frontalface_default.xml"))
CASCADE_PATH = os.path.join(SCRIPT_DIR, "haarcascade_frontalface_default.xml")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "detected_faces")
SAVE_INTERVAL = 2.0  # seconds between saved face images (set to 0 to save every frame)

face_detector = cv2.CascadeClassifier(CASCADE_PATH)
if face_detector.empty():
    raise SystemExit(
        f"Could not load {CASCADE_PATH}\n"
        "Copy it with: cp /usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml "
        f"{SCRIPT_DIR}/"
    )

os.makedirs(OUTPUT_DIR, exist_ok=True)

picam2 = Picamera2()
# "RGB888" gives a 3-channel image in BGR order, which is what OpenCV expects
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

# Camera Module 3 autofocus (delete these lines if you use a Camera Module V2, which has no autofocus)
try:
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
except Exception:
    print("Autofocus not available on this camera, continuing without it.")

last_save = 0.0

try:
    while True:
        im = picam2.capture_array()
        grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

        # Save face crops from the clean frame, before any boxes are drawn on it
        now = time.time()
        if len(faces) > 0 and now - last_save >= SAVE_INTERVAL:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            for i, (x, y, w, h) in enumerate(faces):
                filename = os.path.join(OUTPUT_DIR, f"face_{stamp}_{i}.jpg")
                cv2.imwrite(filename, im[y:y + h, x:x + w])
            last_save = now

        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Camera", im)
        if cv2.waitKey(1) & 0xFF == ord("q"):
			# Quit on input "q"
            break
except KeyboardInterrupt:
    pass
finally:
    picam2.stop()
    cv2.destroyAllWindows()
