# IoT-Lab
Internet of Things Lab: EE/CE 4201 Electrical and Computer Engineering Laboratory in Computing Systems and Computer Engineering


## 1st Lab 
(Rpi order delivered Sep 3): 
Goals: Raspberry Pi setup, Rasbperry OS setup, connect to and test peripherals, sensors, camera
Sensors: BH1745 luminance and color sensor; Raspberry Pi Camera Module 3
* Sep 8: Had trouble with my initial SD (32gb) card; every time RpiOS was flashed on it using Raspberry Pi Imager, it would fail to verify (contents were different than what was written)
* Sep 9: Had to buy a new 64gb card which then worked, flasher worked on first try
  * All setup, sensor testing completed

## 2nd Lab
Goals: Set up TinyDB, AWS account and DynamoDB set up; upload sensor data to local TinyDB and cloud DB using MQTT
* Sep 4: AWS account and DynamoDB set up by Will Arato
* Sep 10: Set up and test TinyDB with sensor data
* Sep 17: Set up data uploading to AWS DynamoDB using MQTT

## 3rd Lab
Goals: Install and run an SLM locally. Give the SLM agentic capabilities relevant to the sensor setup and IoT.
* SLM qwen2.5 installed Sep 10 (no particular model installed yet
* Sep 17: installed and ran qwn2.5.0.5b
* Sep 24: Switched to US-made SLM— Liquid AI’s LFM2.5-350M
* Oct 7: Implemented and gave tools to LFM2.5 to give it agentic capabilities. See tools below:
  * Check BH1745 status
  * Read directly from BH1745
  * Retrieve the latest entry from local TinyDB
* Oct 8: implemented conversation loop and deterministic user-input checking to ensure correct tool calling
  * This resolves an issue where the SLM would repeat previous tool results or confuse which tool should be called as the conversation continued, without compromising multi-tool requests
* Oct 15: implement camera tools for still images and video recordings. Updated TinyDB database to have separate tables for sensor data and camera records
### To Do:
* Update cam tools for delivery to agent in agent.py
* Expand toolset upload data to AWS DynamoDB
* Actuator: send an alert (via email?) following maybe facial recognition or other sensor breakpoint
  * Give agent tools to actuate after making a decision

## 4th Lab
Machine Learning 
Tensor Flow LiteRT (Google) 
Pytorch (deep learning framework to build & teach neural networks)
* meant for small footprint computers (Pi5)

Operate a ML algo on the Pi
* install LiteRT or PyTorch
* install a face recognition ML algo
* OpenCV for open-source algos or ask Chat for open-src algos for small footprint

