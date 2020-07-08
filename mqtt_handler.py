#!/usr/bin/python3

import os
import sys
import time
import paho.mqtt.client as mqtt
import subprocess
import json
import logging
from configUpdater import updateConfig
logging.basicConfig(level=logging.DEBUG)


logger = logging.getLogger(__name__)
cmd = "cat /proc/device-tree/serial-number"
ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
imei = ps.communicate()[0].decode("utf-8")
imei = imei[0:len(imei)-1]
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
		config["host_port"]
		config["host_dir"]
		config["mqtt_host"]
		config["mqtt_port"]
		config["mqtt_topic"]
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

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	subsTopic = "/jetson/get"
	client.subscribe(subsTopic)
	print("Subscribed to Topic " + subsTopic)
	subsTopic = "/jetson/"+imei+"/get"
	client.subscribe(subsTopic)
	print("Subscribed to Topic " + subsTopic)
	subsTopic = "/jetson/"+imei+"/set/#"
	client.subscribe(subsTopic)
	print("Subscribed to Topic " + subsTopic)

def on_message(client, userdata, msg):
	topicToServer = "/jetson/response/"+imei+"/"
	response=None
	command = msg.payload.decode("utf-8").lower()
	if msg.topic.find(imei) == -1:
		if command == "active":
			response=imei
		else:
			return
	else:
		topic = msg.topic[msg.topic.rfind('/'):len(msg.topic)]
		#Read latest config
		with open(configFile, 'r') as file:
			try:
				config = json.loads(file.read())
			except:
				config = json.loads(defaultConfig)

		if msg.topic.find("get") != -1:

			if command == "ping":
				response="ack";

			elif command == "config":
				response=config

			elif command == "reboot":
				client.publish(topicToServer,payload="rebooting")
				client.disconnect()
				time.sleep(1)
				os.system('reboot')

			elif command == "user":
				response="scp user name : " + config["user"]

			elif command == "host":
				response="scp host : " + config["host"]

			elif command == "host_port":
				response="scp port : " + str(config["host_port"])

			elif command == "host_dir":
				response="scp host dir : " + config["host_dir"]

			elif command == "mqtt_host":
				response="used mqtt host : " + config["mqtt_host"]

			elif command == "mqtt_port":
				response="used mqtt port : " + config["mqtt_port"]

			elif command == "mqtt_topic":
				response="topic for data publish : " + config["mqtt_topic"]

			elif command == "person":
				response="person detection : " + str(config["person"]).lower()

			elif command == "face":
				response="face detection : " + str(config["face"]).lower()

			elif command == "vehicle":
				response="vehicle detection : " + str(config["vehicle"]).lower()

			elif command == "large_vehicle":
				response="large vehicle detection : " + str(config["large_vehicle"]).lower()

			elif command == "motor":
				response="motor detection : " + str(config["motor"]).lower()

			elif command == "record":
				response="recording : " + str(config["record"]).lower()

			elif command == "mirror":
				response="mirror : " + str(config["mirror"]).lower()

			elif command == "interval":
				response="send data interval : " + str(config["interval"]) + "minutes"

			elif command == "reboot_time":
				response="reboot time every " + config["reboot_time"]

			elif command == "start_time":
				response="service start time " + config["start_time"]

			elif command == "stop_time":
				response="service stop time " + config["stop_time"]

			elif command == "reset_time":
				if config["reset_time"][0] == '/':
					response="counter reset time every " + config["reset_time"][1:len(config["reset_time"])] + " hours"
				else:
					response="counter reset time at " + config["reset_time"]

			else:
				return

		elif msg.topic.find("set") != -1:
			if topic == "/user":
				updateConfig(user=command)
				response="scp user name set to " + command

			elif topic == "/host":
				updateConfig(host=command)
				response="scp host set to " + command

			elif topic == "/host_port":
				try:
					updateConfig(host_port=int(command))
					response="scp port set to " + command
				except:
					response="invalid message, message must be a number"

			elif topic == "/host_dir":
				updateConfig(host_dir=command)
				response="scp host dir set to " + command

			elif topic == "/mqtt_host":
				client.publish(topicToServer,payload="connecting to : "+command)
				updateConfig(mqtt_host=command)
				client.disconnect()
				time.sleep(3)
				sys.exit(0)

			elif topic == "/mqtt_port":
				try:
					int(command)
					client.publish(topicToServer,payload="connecting to port : "+command)
					updateConfig(mqtt_port=int(command))
					client.disconnect()
					sys.exit(0)
				except:
					response="invalid message, message must be a number"

			elif topic == "/mqtt_topic":
				response="topic for data publish set to : "+command
				updateConfig(mqtt_topic=command)

			elif topic == "/person":
				if command == "true":
					updateConfig(person=True)
					response="person detection set to : true"
				elif command == "false":
					updateConfig(person=False)
					response="person detection set to : false"
				else:
					response="invalid message, message is true or false"

			elif topic == "/face":
				if command == "true":
					updateConfig(face=True)
					response="face detection set to : true"
				elif command == "false":
					updateConfig(face=False)
					response="face detection set to : false"
				else:
					response="invalid message, message is true or false"

			elif topic == "/vehicle":
				if command == "true":
					updateConfig(vehicle=True)
					response="vehicle detection set to : true"
				elif command == "false":
					updateConfig(vehicle=False)
					response="vehicle detection set to : false"
				else:
					response="invalid message, message is true or false"

			elif topic == "/large_vehicle":
				if command == "true":
					updateConfig(large_vehicle=True)
					response="large_vehicle detection set to : true"
				elif command == "false":
					updateConfig(large_vehicle=False)
					response="large_vehicle detection set to : false"
				else:
					response="invalid message, message is true or false"

			elif topic == "/motor":
				if command == "true":
					updateConfig(motor=True)
					response="motor detection set to : true"
				elif command == "false":
					updateConfig(motor=False)
					response="motor detection set to : false"
				else:
					response="invalid message, message is true or false"

			elif topic == "/record":
				if command == "start":
					updateConfig(record=True)
					response="recording for " + str(config["record_dur"]) + " minute"
				elif command.find('m') != -1:
					updateConfig(record=True, record_dur=int(command[0:len(command)-1])*60)
					response="recording for " + command[0:len(command)-1] + " minutes"
				elif command.find('h') != -1:
					updateConfig(record=True, record_dur=int(command[0:len(command)-1])*3600)
					response="recording for " + command[0:len(command)-1] + " hours"
				elif command == "stop":
					updateConfig(record=False)
					response="record stopped"
				else:
					response="invalid message, message is start, (n)m, (n)h, stop"

			elif topic == "/mirror":
				if command == "true":
					updateConfig(mirror=True)
					response="mirror set to : true"
				elif command == "false":
					updateConfig(mirror=False)
					response="mirror set to : false"
				else:
					response="invalid message, message is true or false"

			elif topic == "/interval":
				try:
					interval=int(command)
					updateConfig(interval=interval)
					response="send data interval set to " + command
				except:
					response="invalid message, message must be a number"

			elif topic == "/reboot_time":
				try:
					hour = int(command[0 : command.find(':')])
					minute = int(command[command.find(':') + 1 : len(command)])
					if hour > 23 or minute > 59:
						raise Exception('Invalid Value')
					updateConfig(reboot_time=command)
					response="reboot time set to " + command
				except:
					response="invalid message, message is (hour):(minute), example 23:00"

			elif topic == "/start_time":
				try:
					hour = int(command[0 : command.find(':')])
					minute = int(command[command.find(':') + 1 : len(command)])
					if hour > 23 or minute > 59:
						raise Exception('Invalid Value')
					updateConfig(start_time=command)
					response="start time set to " + command
				except:
					response="invalid message, message is (hour):(minute), example 06:00"

			elif topic == "/stop_time":
				try:
					hour = int(command[0 : command.find(':')])
					minute = int(command[command.find(':') + 1 : len(command)])
					if hour > 23 or minute > 59:
						raise Exception('Invalid Value')
					updateConfig(stop_time=command)
					response="stop time set to " + command
				except:
					response="invalid message, message is (hour):(minute), example 06:00"

			elif topic == "/reset_time":
				try:
					if command[0] == '/' and int(command[1:len(command)]) > 0 and int(command[1:len(command)]) < 23:
						updateConfig(reset_time=command)
						response="reset time set to per " + command[1:len(command)] + " hour"
					elif int(command) <= 23 and int(command) >= 0:
						updateConfig(reset_time=command)
						response="reset time set to " + command + ":00"
					else:
						raise Exception('Invalid Value')
				except:
					response="invalid message, message is (hour) or /(hour), example 23 or /4"
			else:
				return
		else:
			return

	json_response = {'device_id':imei, 'msg':response}
	client.publish(topicToServer,payload=json.dumps(json_response))



client = mqtt.Client(client_id=imei, clean_session=False)
client.enable_logger(logger)
client.on_connect = on_connect
client.on_message = on_message

client.connect(config["mqtt_host"], config["mqtt_port"], 60)

client.loop_forever()
