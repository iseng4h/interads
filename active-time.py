#!/usr/bin/python3

import subprocess
import json
import time
from datetime import datetime

config = dict()
defaultConfig = ""
configFile = "config.file"
defaultFile = "config.default"

checkScanner = "sudo systemctl is-active scanner"
checkSender = "sudo systemctl is-active sender"

startScanner = "sudo systemctl start scanner"
startSender = "sudo systemctl start sender"

stopScanner = "sudo systemctl stop scanner"
stopSender = "sudo systemctl stop sender"

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

	outCheckScan = subprocess.Popen(checkScanner,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0].decode("utf-8")
	outCheckScan = outCheckScan[0:len(outCheckScan)-1]
	outCheckSend = subprocess.Popen(checkSender,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0].decode("utf-8")
	outCheckSend = outCheckSend[0:len(outCheckSend)-1]
	if timenow >= timestart and timenow <= timestop:

		if outCheckScan == 'inactive':
			print("starting scanner")
			subprocess.Popen(startScanner,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

		if outCheckSend == 'inactive':
			print("starting sender")
			subprocess.Popen(startSender,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

		print(str(now.hour) + ":" + str(now.minute) + " active")
		time.sleep(min(45, 60 - now.second))
	else:

		if outCheckScan == 'active':
			print("stopping scanner")
			subprocess.Popen(stopScanner,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

		if outCheckSend == 'active':
			print("stopping sender")
			subprocess.Popen(stopSender,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

		print(str(now.hour) + ":" + str(now.minute) + " inactive")
		time.sleep(min(45, 60 - now.second))
