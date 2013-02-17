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
echo "Output directory: $SAVEDIR"

list='echo hi'

# num users
usrs="echo \"Users Logged in: \$(who | wc -l)\""

# gather CPU info
cpuinfo="echo \"CPU \$(cat /proc/cpuinfo | grep -m1 'model name' )\""
cpuinfo="$cpuinfo; cat /proc/cpuinfo | grep -m1 'cpu MHz'"
cpuinfo="$cpuinfo; cat /proc/cpuinfo | grep -m1 'cpu cores'"
# TODO: Virtual cores

# avg load
avgload="echo \"avgload: \$(cat /proc/loadavg)\""

# utilization
# TODO processing CPU utilization
util="cat /proc/stat | grep 'cpu ' | awk '{ total=0 }'"

# TODO: Cache


#util="$util; echo \"Total Interrupts: \$(cat /proc/stat | grep intr | awk 'END { print \$2 }')\""

# mem info
mem="cat /proc/meminfo | grep Mem"

# setup ssh's command
command="$usrs; $cpuinfo; $avgload; $util; $mem"

# done forming ssh command

ssh $UNAME@$HNAME $command #> $SAVEDIR/$HNAME
