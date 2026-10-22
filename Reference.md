### Python virtual environment:
`source ~/.virtualenvs/pimoroni/bin/activate`

BH1745 Luminance and Color Sensor: [Shop Page](https://shop.pimoroni.com/products/bh1745-luminance-and-colour-sensor-breakout?variant=12767599755347)  
Python Lib: https://github.com/pimoroni/bh1745-python/tree/main


TinyDB Database: "data.json"
* Table "sensor_readings" contains BH1745 readings and corresponding timestamps
* Table "camera_records" contains still images and video segment metadata (timestamps, file names)


To view DB contents in python3 interpreter (in terminal):
```
>>> from tinydb import TinyDB
>>> db = TinyDB('DB name here')
>>> db.all() # This prints all DB contents
```

See TinyDB documentation here: https://tinydb.readthedocs.io/en/latest/

To run LFM2.5-350M (SLM):  
`$ ollama run LiquidAI/lfm2.5-350m`

Ollama tool calling API: https://docs.ollama.com/capabilities/tool-calling#python
