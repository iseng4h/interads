#!/usr/bin/python3

from datetime import datetime
import shutil
import requests
import os
import mmap
import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime

if datetime.now().year < 2020:
	print("\nClock unsynced - please check the internet connection")
	sys.exit(0)

now = datetime.now()
datestr = now.strftime("%Y-%m-%d")

scanFile = "csv/Scan-"+datestr+".csv"
countFile = "csv/Count-"+datestr+".csv"
configFile = "config.file"
defaultFile = "config.default"

config = dict()
defaultConfig = ""
with open(defaultFile, 'r') as file:
	defaultConfig = file.read()

with open(configFile, 'r') as file:
	try:
		config = json.loads(file.read())
	except:
		config = json.loads(defaultConfig)

person = 0
face = 0
largeVehicle = 0
vehicle = 0
motorcycle = 0
wifi = 0
bluetooth = 0

client = mqtt.Client()
client.connect(config["mqtt_host"], config["mqtt_port"], 60)
client.loop_start()

def tail(filename, n):
    """Returns last n lines from the filename. No exception handling"""
    size = os.path.getsize(filename)
    with open(filename, "rb") as f:
        # for Windows the mmap parameters are different
        fm = mmap.mmap(f.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
        try:
            for i in range(size - 1, -1, -1):
                if fm[i] == '\n':
                    n -= 1
                    if n == -1:
                        break
            return fm[i + 1 if i else 0:].splitlines()
        finally:
            fm.close()

if __name__ == '__main__':
	while True:
		start = time.time()

		with open(configFile, 'r') as file:
			try:
				config = json.loads(file.read())
			except:
				config = json.loads(defaultConfig)

		if os.path.exists(scanFile):
			lastline = tail(scanFile,0)[-1].decode("utf-8")
			datas = lastline.split(',')
			wifi = int(datas[4])
			bluetooth = int(datas[5])
		if os.path.exists(countFile):
			lastline = tail(countFile,0)[-1].decode("utf-8")
			datas = lastline.split(',')
			person = int(datas[8])
			face = int(datas[9])
			largeVehicle = int(datas[11]) + int(datas[12])
			vehicle = int(datas[10])
			motorcycle = int(datas[13])

		data={"device_id":datas[0],"timestamp":datetime.now().strftime("%Y/%m/%d %H:%M:%S"),"person":person,"face":face,"large_vehicle":largeVehicle,"vehicle":vehicle,"motorcycle":motorcycle,"wifi":wifi,"bluetooth":bluetooth}

		with open(configFile, 'r') as file:
			try:
				config = json.loads(file.read())
			except:
				config = json.loads(defaultConfig)

		client.publish(config["mqtt_topic"],payload=json.dumps(data))

		time.sleep((config["interval"]*60)-(time.time()-start))
		
