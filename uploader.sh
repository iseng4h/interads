#!/bin/bash

#1 = user
#2 = port
#3 = host
#4 = host dir

cd send/
for f in *;
do
	scp -P $2 "$f" $1@$3:$4; rm "$f"
done
