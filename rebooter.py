#!/usr/bin/python3

import os
import json
import time
from datetime import datetime

config = dict()
defaultConfig = ""
configFile = "config.file"
defaultFile = "config.default"

with open(defaultFile, 'r') as file:
	defaultConfig = file.read()

while True:
	with open(configFile, 'r') as file:
		try:
			config = json.loads(file.read())
			config["reboot_time"]
		except:
			config = json.loads(defaultConfig)

	hour = int(config["reboot_time"][0 : config["reboot_time"].find(':')])
	minute = int(config["reboot_time"][config["reboot_time"].find(':') + 1 : len(config["reboot_time"])])
	now = datetime.now()
	if now.hour == hour and now.minute == minute:
		print('reboot in a minute')
		time.sleep(60)
		os.system('reboot')
	else:
		print(str(now.hour) + ':' + str(now.minute))
		time.sleep(45)
