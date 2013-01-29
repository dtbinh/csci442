#!/bin/bash

# Matt Buland's traceroute bash script

if [ -z $1 ]
then
	echo "Please provide me with an address to trace"
	exit 1
fi

for ttl in {1..255};
do
	stdOut=`python ping.py $1 $ttl`
	ret=$?
	if [ $ret -eq 0 ]
	then
		# Destination reached
		#echo "Destination reached"
		echo $stdOut
		exit 0
	elif [ $ret -eq 9 ]
	then
		# TTL exeeded
		#echo "TTL Exceeded. Continueing"
		echo $stdOut
	else
		# exit with error: script got an unexpected response
		echo "Unexpected result"
		exit 1
	fi
done
echo "Destination not reached within 225 hops"
exit 1
