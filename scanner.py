#!/usr/bin/python3

import subprocess
import threading
import time
from datetime import datetime
import bluetooth
from csv import writer
from csv import DictWriter
import os
import sys
#from bluetooth.ble import DiscoveryService

cmd = "sudo iw dev wlan0 scan | grep \"on wlan0\|SSID:\""
#cmd = "sudo iw dev wlan0 scan | grep \"on wlan0\""
#service = DiscoveryService()

cmd1 = "cat /proc/device-tree/serial-number"
ps = subprocess.Popen(cmd1,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
imei = ps.communicate()[0].decode("utf-8")
imei = imei[0:len(imei)-1]

if datetime.now().year < 2020:
	print("\nClock unsynced - please check the internet connection")
	ps = subprocess.Popen("sudo ~/INTERADS/settime.sh",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	print(ps.communicate()[0].decode("utf-8"))
	sys.exit(0)

interval = 15

addresses = list()
scannedAddress = list()
btdevices = list()
ScannedBTdevices = list()
tempFile = "/var/tmp/scan.temp"
field_names = ['IMEI','Time Stamp','WiFi','Bluetooth','Total WiFi','Total Bluetooth','MAC WiFi', 'MAC Bluetooth']
datestr = ""

def sniff():
	global scannedAddress
	global addresses
	ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	output = ps.communicate()[0]
	addresses = list(output[0:len(output)-1].decode("utf-8").replace("\n\tSSID: ",'\t').split('\n'))
	for i,address in enumerate(addresses):
		addresses[i] = address[4:21] + address[address.index('\t'):len(address)]
		if address[4:21] not in scannedAddress:
			scannedAddress.append(address[4:21])
			with open(tempFile,'a') as fwp:
				print("w\t"+address[4:21],file=fwp)

def scan():
	global ScannedBTdevices
	global btdevices
	btdevices = bluetooth.discover_devices(lookup_names = False)
	#btdevices = service.discover(2).items()
	#print (btdevices)
	for i,btdevice in enumerate(btdevices):
		if btdevice not in ScannedBTdevices:
			ScannedBTdevices.append(btdevice)
			with open(tempFile,'a') as fbp:
				print("b\t"+btdevice,file=fbp)

loop_sniff = True
loop_scan = True

def loop_sniff():
	while loop_sniff:
		sniff()
		time.sleep(5)

def loop_scan():
	while loop_scan:
		scan()
		time.sleep(5)

sniffThread = threading.Thread(target=loop_sniff)
sniffThread.daemon = True
scanThread = threading.Thread(target=loop_scan)
scanThread.daemon = True

def start():
	sniffThread.start()
	scanThread.start()

def stop():
	global loop_sniff
	global loop_scan
	loop_sniff = False
	sniffThread.join()
	loop_scan = False
	scanThread.join()

def print_result():
	now = datetime.now()
	nowStr = now.strftime("%Y/%m/%d %H:%M:%S")
	with open("csv/Scan-"+datestr+".csv", 'a+', newline='') as write_obj:
			dict_writer = DictWriter(write_obj, fieldnames=field_names)
			dict_writer.writerow({"IMEI":imei,"Time Stamp":nowStr,"WiFi":len(addresses),"Bluetooth":len(btdevices),'Total WiFi':len(scannedAddress),"Total Bluetooth":len(ScannedBTdevices),"MAC WiFi":scannedAddress,"MAC Bluetooth":ScannedBTdevices})
	done = datetime.now()
	time.sleep(interval - ((done.hour*3600 + done.minute*60 + done.second) - (now.hour*3600 + now.minute*60 + now.second)))

def init():
	global scannedAddress
	global ScannedBTdevices
	global datestr
	now = datetime.now()
	datestr = now.strftime("%Y-%m-%d")
	if os.path.exists(tempFile) and os.path.getsize(tempFile) > 0:
		with open(tempFile,'r') as frp:
			date = frp.readline()
			if datestr in date:
				while True:
					line = frp.readline()
					data = line.split("\t")
					if data[0].lower() == "w":
						scannedAddress.append(data[1][0:17])
					elif data[0].lower() == "b":
						ScannedBTdevices.append(data[1][0:17])
					if not line:
						break
	else:
		with open(tempFile,'w') as frp:
			print(datestr, file=frp)
	if not os.path.exists("csv/Scan-"+datestr+".csv"):
		with open("csv/Scan-"+datestr+".csv",'w+') as cf:
			dict_writer = DictWriter(cf, fieldnames=field_names)
			dict_writer.writerow({"IMEI":"IMEI","Time Stamp":"Time Stamp","WiFi":"WiFi","Bluetooth":"Bluetooth",'Total WiFi':'Total WiFi',"Total Bluetooth":"Total Bluetooth","MAC WiFi":"MAC WiFi","MAC Bluetooth":"MAC Bluetooth"})
		with open(tempFile,'w') as frp:
			print(datestr, file=frp)

if __name__ == "__main__":
	init()
	start()
	while True:
		try:
			print_result()

			#reset
			if not os.path.exists(tempFile):
				print("reset count")
				addresses = list()
				scannedAddress = list()
				btdevices = list()
				ScannedBTdevices = list()
		except KeyboardInterrupt:
			stop()
			break
