#!/usr/bin/python3
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import cv2
import jetson.inference
import jetson.utils
import numpy as np
import math
import time
import argparse
import sys
from csv import writer
from csv import DictWriter
import os
from datetime import datetime
from configUpdater import updateConfig
import subprocess
import json

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
						   formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.3, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")
parser.add_argument("--nodisplay", action='store_true')

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

cmd = "cat /proc/device-tree/serial-number"
opt.camera = "/dev/video0"
opt.overlay = "none"
tempFile = "/var/tmp/count.temp"
configFile = "config.file"
defaultFile = "config.default"


if not os.path.exists(opt.camera):
	print("\nCamera not found")
	sys.exit(0)

if datetime.now().year < 2020:
	print("\nClock unsynced - please check the internet connection")
	sys.exit(0)

config = dict()
configDef = dict()
defaultConfig = ""
with open(defaultFile, 'r') as file:
	defaultConfig = file.read()
	configDef = json.loads(defaultConfig)

with open(configFile, 'r') as file:
	try:
		config = json.loads(file.read())
	except:
		config = json.loads(defaultConfig)

prevRec = False
fourcc = cv2.VideoWriter_fourcc(*'FMP4')
output = cv2.VideoWriter()

ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
imei = ps.communicate()[0].decode("utf-8")
imei = imei[0:len(imei)-1]

maxList = 9
minValid = 4
if minValid > maxList:
	print("minValid is higher than maxList")
	sys.exit(0)
persons = 0
personsCountList = []
MAFp = 0
prevMAFp = 0
faces = 0
facesCountList = []
MAFf = 0
prevMAFf = 0
cars = 0
carsCountList = []
MAFc = 0
prevMAFc = 0
buses = 0
busesCountList = []
MAFb = 0
prevMAFb = 0
trucks = 0
trucksCountList = []
MAFt = 0
prevMAFt = 0
motors = 0
motorsCountList = []
MAFm = 0
prevMAFm = 0
faceargs = ["Counting.py","--model=snapshot_iter_24000.caffemodel","--prototxt=deploy.prototxt","--class_labels=class_labels.txt"]


det = jetson.inference.detectNet("", sys.argv, opt.threshold)
facedet = jetson.inference.detectNet("facenet", faceargs, 0.15)
facesCountList = [0,0]

# create the camera and display
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
if not opt.nodisplay:
	display = jetson.utils.glDisplay()


# process frames until user exits
if __name__ == '__main__':
	field_names = ['IMEI','Time Stamp','Person','Face','Car','Bus','Truck','Motorcycle','Total Person','Total Face','Total Car','Total Bus','Total Truck','Total Motorcycle']
	now = datetime.now()
	datestr = now.strftime("%Y-%m-%d")
	readFailed = False
	if os.path.exists(tempFile) and os.path.getsize(tempFile) > 0:
		with open(tempFile,'r') as frp:
			date = frp.readline()
			if datestr in date:
				try:
					line = frp.readline()
					data = line.split("\t")
					persons = int(data[0])
					personsCountList = list(map(data[1].split(" ")))
					MAFp = float(data[2])
					prevMAFp = float(data[3])
					line = frp.readline()
					data = line.split("\t")
					faces = int(data[0])
					facesCountList = list(map(data[1].split(" ")))
					MAFf = float(data[2])
					prevMAFf = float(data[3])
					line = frp.readline()
					data = line.split("\t")
					cars = int(data[0])
					carsCountList = list(map(data[1].split(" ")))
					MAFc = float(data[2])
					prevMAFc = float(data[3])
					line = frp.readline()
					data = line.split("\t")
					buses = int(data[0])
					busesCountList = list(map(data[1].split(" ")))
					MAFb = float(data[2])
					prevMAFb = float(data[3])
					line = frp.readline()
					data = line.split("\t")
					trucks = int(data[0])
					trucksCountList = list(map(data[1].split(" ")))
					MAFt = float(data[2])
					prevMAFt = float(data[3])
					line = frp.readline()
					data = line.split("\t")
					motors = int(data[0])
					motorsCountList = list(map(data[1].split(" ")))
					MAFm = float(data[2])
					prevMAFm = float(data[3])
				except:
					readFailed = True
	if not os.path.exists("csv/Count-"+datestr+".csv") and not readFailed:
		with open("csv/Count-"+datestr+".csv",'w+') as cf:
			dict_writer = DictWriter(cf, fieldnames=field_names)
			dict_writer.writerow({"IMEI":"IMEI","Time Stamp":"Time Stamp","Person":"Person","Face":"Face","Car":"Car",'Bus':'Bus','Truck':'Truck',"Motorcycle":"Motorcycle","Total Person":"Total Person","Total Face":"Total Face","Total Car":"Total Car",'Total Bus':'Total Bus','Total Truck':'Total Truck',"Total Motorcycle":"Total Motorcycle"})

	videoName = ''

	while True:
		start = time.time()
		# capture the image
		if not os.path.exists(opt.camera):
			print("Camera disconnected")
			sys.exit(0)
		if opt.nodisplay:
			img, width, height = camera.CaptureRGBA(timeout=1)
		else:
			img, width, height = camera.CaptureRGBA(timeout=1,zeroCopy=1)

		
		with open(configFile, 'r') as file:
			try:
				config = json.loads(file.read())
			except:
				config = json.loads(defaultConfig)


		now = datetime.now()
		datestr = now.strftime("%Y-%m-%d")
		timestr = now.strftime(" %H:%M:%S")



		# detect objects in the image (with overlay)
		detectionResult = det.Detect(img, width, height, opt.overlay)
		if config["face"] and config["person"]:
			detectedFaces = facedet.Detect(img, width, height, opt.overlay)


		# convert cudaImg to npArray
		if not opt.nodisplay:
			image = jetson.utils.cudaToNumpy(img, width, height, 4)


		#record
		if config["record"] and not prevRec:
			startRec = now.hour*3600 + now.minute*60 + now.second
			arr = np.uint8(image)
			h, w, d = arr.shape
			videoName = "record/rec_" + imei + "_" + datestr + timestr + ".mp4"
			output = cv2.VideoWriter(videoName, fourcc, 10.0, (w,h))
		elif not config["record"] and prevRec:
			output.release()
			commandSplit="./splitter.sh \""+videoName[videoName.rfind('/')+1:len(videoName)]+"\""
			subprocess.Popen(commandSplit,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			commandUpload="./uploader.sh "+config["user"]+" "+str(config["host_port"])+" "+config["host"]+" "+config["host_dir"]
			subprocess.Popen(commandUpload,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		prevRec = config["record"]


		#reset
		if not os.path.exists(tempFile):
			print('reset counter')
			persons = 0
			personsCountList = []
			MAFp = 0
			prevMAFp = 0
			faces = 0
			facesCountList = []
			MAFf = 0
			prevMAFf = 0
			cars = 0
			carsCountList = []
			MAFc = 0
			prevMAFc = 0
			buses = 0
			busesCountList = []
			MAFb = 0
			prevMAFb = 0
			trucks = 0
			trucksCountList = []
			MAFt = 0
			prevMAFt = 0
			motors = 0
			motorsCountList = []
			MAFm = 0
			prevMAFm = 0

		
		i = 0
		j = 0
		k = 0
		l = 0
		m = 0
		n = 0
		for detection in detectionResult:
			if config["person"] and det.GetClassDesc(detection.ClassID) == "person" :
				top = int(detection.Top)
				bottom = int(detection.Bottom)
				left = int(detection.Left)
				right = int(detection.Right)
				if not opt.nodisplay:
					cv2.putText(image, "person", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255,0,0), lineType=cv2.LINE_AA)
					cv2.rectangle(image, (left, top), (right, bottom), (255, 0, 0),5)
				i += 1
				if config["face"]:
					faceIndex = 0
					while faceIndex < len(detectedFaces):
						faceCenterX = int(detectedFaces[faceIndex].Center[0])
						faceCenterY = int(detectedFaces[faceIndex].Center[1])
						facetop = int(detectedFaces[faceIndex].Top)
						facebottom = int(detectedFaces[faceIndex].Bottom)
						faceleft = int(detectedFaces[faceIndex].Left)
						faceright = int(detectedFaces[faceIndex].Right)
						if faceCenterY >= top and faceCenterY <= bottom and faceCenterX >= left and faceCenterX <= right:
							if not opt.nodisplay:
								cv2.rectangle(image, (faceleft, facetop), (faceright, facebottom), (230, 210, 50),5)
							l += 1
							del (detectedFaces[faceIndex])
							break
						else :
							faceIndex += 1
			elif config["vehicle"] and det.GetClassDesc(detection.ClassID) == "car" :
				if not opt.nodisplay:
					top = int(detection.Top)
					bottom = int(detection.Bottom)
					left = int(detection.Left)
					right = int(detection.Right)
					cv2.putText(image, "car", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0,255,0), lineType=cv2.LINE_AA)
					cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0),5)
				j += 1
			elif config["large_vehicle"] and det.GetClassDesc(detection.ClassID) == "bus" :
				if not opt.nodisplay:
					top = int(detection.Top)
					bottom = int(detection.Bottom)
					left = int(detection.Left)
					right = int(detection.Right)
					cv2.putText(image, "bus", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0,255,0), lineType=cv2.LINE_AA)
					cv2.rectangle(image, (left, top), (right, bottom), (50, 230, 210),5)
				m += 1
			elif config["large_vehicle"] and det.GetClassDesc(detection.ClassID) == "truck" :
				if not opt.nodisplay:
					top = int(detection.Top)
					bottom = int(detection.Bottom)
					left = int(detection.Left)
					right = int(detection.Right)
					cv2.putText(image, "truck", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0,255,0), lineType=cv2.LINE_AA)
					cv2.rectangle(image, (left, top), (right, bottom), (210, 50, 230),5)
				n += 1
			elif config["motor"] and det.GetClassDesc(detection.ClassID) == "motorcycle" :
				if not opt.nodisplay:
					top = int(detection.Top)
					bottom = int(detection.Bottom)
					left = int(detection.Left)
					right = int(detection.Right)
					cv2.putText(image, "motorcycle", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0,0,255), lineType=cv2.LINE_AA)
					cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255),5)
				k += 1



		# Counting using Moving Average Filter
		MAFp = round(sum(personsCountList) * 1.0 / (len(personsCountList) or 1) + (0.5-(minValid*1./maxList)))
		if config["person"] and prevMAFp < MAFp:
			persons += (MAFp-prevMAFp)
		personsCountList.append(i)
		if len(personsCountList) > maxList:
			del (personsCountList[0])
		prevMAFp = MAFp


		MAFf = round(sum(facesCountList) * 1.0 / (len(facesCountList) or 1) + (0.5-(minValid*1./maxList)))
		if config["face"] and config["person"] and prevMAFf < MAFf:
			faces += (MAFf-prevMAFf)
		facesCountList.append(l)
		if len(facesCountList) > maxList:
			del (facesCountList[0])
		prevMAFf = MAFf


		MAFc = round(sum(carsCountList) * 1.0 / (len(carsCountList) or 1) + (0.5-(minValid*1./maxList)))
		if config["vehicle"] and prevMAFc < MAFc:
			cars += (MAFc-prevMAFc)
		carsCountList.append(j)
		if len(carsCountList) > maxList:
			del (carsCountList[0])
		prevMAFc = MAFc


		MAFb = round(sum(busesCountList) * 1.0 / (len(busesCountList) or 1) + (0.5-(minValid*1./maxList)))
		if config["large_vehicle"] and prevMAFb < MAFb:
			buses += (MAFb-prevMAFb)
		busesCountList.append(m)
		if len(busesCountList) > maxList:
			del (busesCountList[0])
		prevMAFb = MAFb


		MAFt = round(sum(trucksCountList) * 1.0 / (len(trucksCountList) or 1) + (0.5-(minValid*1./maxList)))
		if config["large_vehicle"] and prevMAFt < MAFt:
			trucks += (MAFt-prevMAFt)
		trucksCountList.append(n)
		if len(trucksCountList) > maxList:
			del (trucksCountList[0])
		prevMAFt = MAFt


		MAFm = round(sum(motorsCountList) * 1.0 / (len(motorsCountList) or 1) + (0.5-(minValid*1./maxList)))
		if config["motor"] and prevMAFm < MAFm:
			motors += (MAFm-prevMAFm)
		motorsCountList.append(k)
		if len(motorsCountList) > maxList:
			del (motorsCountList[0])
		prevMAFm = MAFm



		#write to csv
		with open("csv/Count-"+datestr+".csv", 'a+', newline='') as write_obj:
			dict_writer = DictWriter(write_obj, fieldnames=field_names)
			dict_writer.writerow({"IMEI":imei,"Time Stamp":now.strftime("%Y/%m/%d %H:%M:%S"),"Person":i,"Face":l,"Car":j,'Bus':m,'Truck':n,"Motorcycle":k,"Total Person":persons,"Total Face":faces,"Total Car":cars,'Total Bus':buses,'Total Truck':trucks,"Total Motorcycle":motors})



		#dump
		with open(tempFile,'w') as frp:
			print(datestr, file=frp)
			print(str(persons) + "\t" + " ".join(str(a) for a in personsCountList) + "\t" + str(MAFp) + "\t" + str(prevMAFp), file=frp)
			print(str(faces) + "\t" + " ".join(str(a) for a in facesCountList) + "\t" + str(MAFf) + "\t" + str(prevMAFf), file=frp)
			print(str(cars) + "\t" + " ".join(str(a) for a in carsCountList) + "\t" + str(MAFc) + "\t" + str(prevMAFc), file=frp)
			print(str(buses) + "\t" + " ".join(str(a) for a in busesCountList) + "\t" + str(MAFb) + "\t" + str(prevMAFb), file=frp)
			print(str(trucks) + "\t" + " ".join(str(a) for a in trucksCountList) + "\t" + str(MAFt) + "\t" + str(prevMAFt), file=frp)
			print(str(motors) + "\t" + " ".join(str(a) for a in motorsCountList) + "\t" + str(MAFm) + "\t" + str(prevMAFm), file=frp)


		if config["mirror"]:
			image = cv2.flip(image,1)
			cv2.putText(image, "Mirrored", (width-200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
			cv2.putText(image, "Mirrored", (width-200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)

		if not opt.nodisplay:
			cv2.rectangle(image,(0,height-30),(width,height),(0,0,0),cv2.FILLED)

			locY = 50
			if config["person"]:
				text = "{:d} Persons".format(persons)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)
				locY += 30

			if config["face"] and config["person"]:
				text = "{:d} Faces".format(faces)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)
				locY += 30

			if config["vehicle"]:
				text = "{:d} Cars".format(cars)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)
				locY += 30

			if config["large_vehicle"]:
				text = "{:d} Buses".format(buses)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)
				locY += 30

			if config["large_vehicle"]:
				text = "{:d} Trucks".format(trucks)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)
				locY += 30

			if config["motor"]:
				text = "{:d} Motorcycles".format(motors)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
				cv2.putText(image, text, (20, locY), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)
	

		end = time.time()
		seconds = end-start
		fps = 1 / seconds

		if not opt.nodisplay:
			text = datestr + " " + timestr + " {:d}fps".format(int(fps))
			if config["record"]:
				text += " (R)"
			cv2.putText(image, text, (20, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),3, lineType=cv2.LINE_AA)
			cv2.putText(image, text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0),2, lineType=cv2.LINE_AA)

		if config["record"]:
			arr = np.uint8(image)
			r_channel, g_channel, b_channel, a_channel = cv2.split(arr)
			bgr = cv2.merge((b_channel, g_channel, r_channel))
			output.write(bgr)
			output.write(bgr)
			output.write(bgr)
			if config["face"]:
				output.write(bgr)
				output.write(bgr)
				output.write(bgr)
			if config["record_dur"] <= ((now.hour*3600 + now.minute*60 + now.second) - startRec):
				updateConfig(record=False, record_dur=configDef['record_dur'])

		if not opt.nodisplay:
			img = jetson.utils.cudaFromNumpy(image)
			# render the image
			display.RenderOnce(img, width, height)

			# update the title bar
			display.SetTitle("INTERADS".format(opt.network, det.GetNetworkFPS()))

