#!/bin/bash

cd record
split -b 2M "$1" ../send/"$1".part
rm "$1"
