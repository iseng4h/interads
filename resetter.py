#!/usr/bin/python3

import os
import json
import time
from datetime import datetime

config = dict()
defaultConfig = ""
configFile = "config.file"
defaultFile = "config.default"
tempCountFile = "/var/tmp/count.temp"
tempScanFile = "/var/tmp/scan.temp"

with open(defaultFile, 'r') as file:
	defaultConfig = file.read()

while True:
	with open(configFile, 'r') as file:
		try:
			config = json.loads(file.read())
			config["reset_time"]
		except:
			config = json.loads(defaultConfig)

	now = datetime.now()
	print(str(now.hour) + ':' + str(now.minute))
	if config["reset_time"].find('/') == -1:
		if now.hour == int(config["reset_time"]) and now.minute == 4:
			print('reset start')
			os.remove(tempCountFile)
			os.remove(tempScanFile)
			time.sleep(61-now.second)
		else:
			time.sleep(min(45, 60 - now.second))
	else:
		if (now.hour%int(config["reset_time"][1:len(config["reset_time"])])) == 0 and now.minute == 4:
			print('reset start')
			if os.path.exists(tempCountFile):
				os.remove(tempCountFile)
			if os.path.exists(tempScanFile):
				os.remove(tempScanFile)
			time.sleep(61-now.second)
		else:
			time.sleep(min(45, 60 - now.second))
