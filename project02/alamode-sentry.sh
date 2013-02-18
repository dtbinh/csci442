#!/bin/sh -f

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
		HOSTS=$HNAME
		;;
	f)
		FNAME=$OPTARG
		HOSTS=$(cat $FNAME)
		;;
	d)
		DNAME=$OPTARG
		;;
	u)
		UNAME="$OPTARG@"
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

#if [ -z "$UNAME" ];
#	then
#	UNAME="mbuland"
#fi

echo "Output directory: $SAVEDIR"

for HNAME in $HOSTS;
	do
	# num users
	usrs="echo \"Users Logged in: \$(who | wc -l)\""
	
	# gather CPU info
	cpuinfo="echo \"CPU \$(cat /proc/cpuinfo | grep -m1 'model name' )\""
	cpuinfo="$cpuinfo; cat /proc/cpuinfo | grep -m1 'cpu MHz'"
	cpuinfo="$cpuinfo; echo -n 'Real Cores: '; cat /proc/cpuinfo | awk '/siblings/ { tot++; sib=\$3} /cpu cores/ { cores=\$4 }; END { print (tot/sib*cores )}'"
	cpuinfo="$cpuinfo; echo -n 'Virtual Cores: '; cat /proc/cpuinfo | awk '/siblings/ { tot++; sib=\$3} /cpu cores/ { cores=\$4 }; END { print (tot-tot/sib*cores )}'"
	
	# avg load
	avgload="echo \"avgload: \$(cat /proc/loadavg)\""
	
	# utilization
	# source: https://github.com/zirrostig/OneLiners/blob/master/cpu_usage.sh
	util="echo -n 'CPU Usage: '; ( sleep 2; cat /proc/stat ) | cat /proc/stat - |
	    awk ' /cpu / { oldsum = sum; sum = 0;
		for ( i = 2; i <= NF; i++ ) { sum += \$i };
		oldidle = idle;
		idle = \$5;
		diffsum = sum - oldsum;
		diffidle = idle - oldidle;
		usage = (( diffsum - diffidle ) / diffsum ) * 100}
		END { print usage }'"
	
	# Cache
	cache='for f in $(ls /sys/devices/system/cpu/cpu0/cache); do f="/sys/devices/system/cpu/cpu0/cache/$f"; echo "L$(cat $f/level) $(cat $f/type) Size: $(cat $f/size)"; done'
	
	# mem info
	mem="cat /proc/meminfo | grep Mem"
	
	# setup ssh's command
	command="$usrs; $cpuinfo; $avgload; $util; $cache; $mem"
	
	# done forming ssh command
	
	ssh $UNAME$HNAME $command #> $SAVEDIR/$HNAME
done
