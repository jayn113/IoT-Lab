# Edge AIoT System with Local SLM Agent

A Raspberry Pi 5-based IoT monitoring system integrating a BH1745 color and luminance sensor and Raspberry Pi Camera Module 3 for environmental data collection and image/video capture. 
Data acquired from the sensors is timestamped and stored into a local TinyDB, while an MQTT pipeline uploads said data through AWS IoT to DynamoDB. 
Liquid AI's LFM2.5-350M small language model (SLM) was used to build a conversational agent capable of calling tools to obtain the sensor's status, live measurements, and retrieve the latest entry from TinyDB.

## In Progress
Camera tools: 
* Timestamped still image capture and metadata upload to TinyDB
* Timestamped 15-second video recording and metadata upload to TinyDB

## Planned Features
* Tool to upload local TinyDB to DynamoDB using MQTT
* Implement a real-time, machine learning-based facial detection system using the Raspberry Pi Camera Module 3
