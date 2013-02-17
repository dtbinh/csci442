#!/bin/sh

# Script to monitor a remote machine's status

function printUsage {
		echo """Usage: alamode-sentry [options] (-n HOSTNAME | -f FILENAME) [-d directory]
Options:
	-h				help
	-u <username>	Username to use when SSHing
		"""
		quit
}

while getopts "hd:n:f:u:" opt 
	do
	case $opt in
	h)
		printUsage
		;;
	n)
		HNAME=$OPTARG
		;;
	f)
		FNAME=$OPTARG
		;;
	d)
		DNAME=$OPTARG
		;;
	u)
		UNAME=$OPTARG
		;;
	\?)
		printUsage
		;;
	esac
done

if [ -n "$HNAME" ] && [ -n "$FNAME" ];
	then
	echo "Please use EITHER -n OR -f. Not both"
	exit
fi

if [ -z "$HNAME" ] && [ -z "$FNAME" ];
	then
	echo "Please use the -n or the -f flag. One of them is required"
	exit
fi

if [ -n "$DNAME" ];
	then
	SAVEDIR=$DNAME
else
	SAVEDIR=$(mktemp -d)
fi

if [ -z "$UNAME" ];
	then
	UNAME="mbuland"
fi

echo "Using $UNAME as the username. If this is wrong, please use the -u flag"

list='echo hi'

# num users
usrs="echo Users Logged in: " #\$(who | wc -l)\""

# gather CPU info
cpuinfo="cat /proc/cpuinfo"

# avg load
avgload="echo \"avgload: $(cat /proc/loadavg)\""

# utilization
util="cat /proc/stat"

# setup ssh's command
command="'$cpuinfo'"

# done forming ssh command

ssh $UNAME@$HNAME $command
