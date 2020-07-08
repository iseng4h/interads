#!/usr/bin/python3

import json

config = dict()
defaultConfig = ""
configFile = "config.file"
defaultFile = "config.default"

with open(defaultFile, 'r') as file:
	defaultConfig = file.read()
with open(configFile, 'r') as file:
	try:
		config = json.loads(file.read())
		config["user"]
		config["host"]
		config["mqtt_host"]
		config["mqtt_port"]
		config["mqtt_topic"]
		config["send_mode"]
		config["person"]
		config["face"]
		config["vehicle"]
		config["large_vehicle"]
		config["motor"]
		config["record"]
		config["record_dur"]
		config["mirror"]
		config["interval"]
		config["reboot_time"]
		config["start_time"]
		config["stop_time"]
		config["reset_time"]
	except:
		config = json.loads(defaultConfig)

def updateConfig(user=None,host=None,host_port=None,host_dir=None,mqtt_host=None,mqtt_port=None,mqtt_topic=None,person=None,face=None,vehicle=None,large_vehicle=None,motor=None,record=None,record_dur=None,mirror=None,interval=None,reboot_time=None,start_time=None,stop_time=None,reset_time=None):
	with open(configFile, 'r') as file:
		try:
			config = json.loads(file.read())
		except:
			config = json.loads(defaultConfig)

	if user is not None:
		config["user"]=user
	if host is not None:
		config["host"]=host
	if host_port is not None:
		config["host_port"]=host_port
	if host_dir is not None:
		config["host_dir"]=host_dir
	if mqtt_host is not None:
		config["mqtt_host"]=mqtt_host
	if mqtt_port is not None:
		config["mqtt_port"]=mqtt_port
	if mqtt_topic is not None:
		config["mqtt_topic"]=mqtt_topic
	if person is not None:
		config["person"]=person
	if face is not None:
		config["face"]=face
	if vehicle is not None:
		config["vehicle"]=vehicle
	if large_vehicle is not None:
		config["large_vehicle"]=large_vehicle
	if motor is not None:
		config["motor"]=motor
	if record is not None:
		config["record"]=record
	if record_dur is not None:
		config["record_dur"]=record_dur
	if mirror is not None:
		config["mirror"]=mirror
	if interval is not None:
		config["interval"]=interval
	if reboot_time is not None:
		config["reboot_time"]=reboot_time
	if start_time is not None:
		config["start_time"]=start_time
	if stop_time is not None:
		config["stop_time"]=stop_time
	if reset_time is not None:
		config["reset_time"]=reset_time

	with open(configFile, 'w') as file:
		print(json.dumps(config), file=file)
