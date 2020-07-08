#!/usr/bin/python3

import subprocess
import json
import time
from datetime import datetime

config = dict()
defaultConfig = ""
configFile = "config.file"
defaultFile = "config.default"

checkCounter = "systemctl is-active --user count"

startCounter = "systemctl --user start count"

stopCounter = "systemctl --user stop count"

with open(defaultFile, 'r') as file:
	defaultConfig = file.read()

while True:
	with open(configFile, 'r') as file:
		try:
			config = json.loads(file.read())
			config["start_time"]
			config["stop_time"]
		except:
			config = json.loads(defaultConfig)

	start_hour = int(config["start_time"][0 : config["start_time"].find(':')])
	start_minute = int(config["start_time"][config["start_time"].find(':') + 1 : len(config["start_time"])])
	stop_hour = int(config["stop_time"][0 : config["stop_time"].find(':')])
	stop_minute = int(config["stop_time"][config["stop_time"].find(':') + 1 : len(config["stop_time"])])
	now = datetime.now()

	print(str(start_hour) + ":" + str(start_minute) + " - " + str(stop_hour) + ":" + str(stop_minute))
	timenow = now.hour*60 + now.minute
	timestart = start_hour*60 + start_minute
	timestop = stop_hour*60 + stop_minute

	outCheckCount = subprocess.Popen(checkCounter,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0].decode("utf-8")
	outCheckCount = outCheckCount[0:len(outCheckCount)-1]

	if timenow >= timestart and timenow <= timestop:

		if outCheckCount == 'inactive':
			print("starting counter")
			subprocess.Popen(startCounter,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

		print(str(now.hour) + ":" + str(now.minute) + " active")
		time.sleep(min(45, 60 - now.second))
	else:

		if outCheckCount == 'active':
			print("stopping counter")
			subprocess.Popen(stopCounter,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

		print(str(now.hour) + ":" + str(now.minute) + " inactive")
		time.sleep(min(45, 60 - now.second))
