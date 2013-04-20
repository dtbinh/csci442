#!/bin/bash
set -e

function printUsage {
	echo """Usage: alamode-publish [-s] [-d]
	Options:
		-s	<directory>		path to input directory, which was created by alamode-sentry
		-d	<directory> 	path to output directory
		-o					print html to standard out
"""
	exit
}

INPUTDIR="."
while getopts "hd:s:o" opt 
	do
	case $opt in
	h)
		printUsage
		;;
	s)
		if [ ! -e $OPTARG ] && [ ! -d $OPTARG ];
			then
			printUsage
		fi
		INPUTDIR=$OPTARG
		;;
	d)
		if [ ! -e $OPTARG || ! -d $OPTARG];
			then
			printUsage
		fi
		OUTDIR=$OPTARG
		;;
	o)
		SOUT=true
		;;
	\?)
		printUsage
		;;
	esac
done

if [ -z "$INPUTDIR" ];
	then
	read s_in
	INPUTDIR=$s_in
fi

if [ -z "$OUTDIR" ];
	then
	# output to standard out
	OUTDIR="."
fi

if [ -z "$SOUT" ];
	then
	OUTPUT='/proc/self/fd/1'
else
	OUTPUT="$OUTDIR/index.html"
fi

echo "<!DOCTYPE html><html><head></head><body>" > $OUTPUT

oldPWD=$PWD
#cd $INPUTDIR
for machine in $(ls $INPUTDIR);
	do
	
	cat $INPUTDIR/$machine | awk "
		BEGIN { data[\"machine\"] = $machine; }
		/Users/ { data[\"users\"] = \$1; }
		/CPU model/ { for(i=5;i<NF-1;i++) { data[\"cpumodel\"]=data[\"cpumodel\"]\" \"\$i; }
			data[\"cpunom\"] = \$NF;
		}
		/cpu MHz/ { data[\"cpumhz\"] = \$4; }
		/MemTotal/ { data[\"memtot\"] = \$2; }
		/MemFree/ { data[\"memfree\"] = \$2; }
		/avgload/ { data[\"avgload0\"] = \$2; data[\"avgload1\"] = \$3; data[\"avgload2\"] = \$4; split(\$5, arr, \"/\"); data[\"numproc\"] = arr[2]; }
		/Failed to connect/ { failure=1; }
		function kb_to_gb(number) {
			return (number+0)/1024/1024
		}
		function memusageratio() {
			return ((data[\"memtot\"] - data[\"memfree\"])/(data[\"memtot\"]+0));
		}

		END { 
		if(failure) {
			print \"<div index=$machine style='background-color:grey' ><h1>$machine</h1>Could not connect to host</div>\";
		} else { 
			if (memusageratio() < 0.33) { load=\"green\"; }
			else if (memusageratio() < 0.66) { load=\"yellow\"; }
			else { load=\"red\"; }
		print \"<div index=$machine style='background-color:\"load\"' >\n\",
\"		<h1>$machine</h1>\n\",
\"		<div class=systeminfo>\n\",
\"			<table border=2 bordercolor=black cellspacing=0 >\n\",
\"				<thread>\n\",
\"					<tr>\n\",
\"						<th></th>\n\",
\"						<th></th>\n\",
\"						<th></th>\n\",
\"						<th></th>\n\",
\"						<th></th>\n\",
\"						<th></th>\n\",
\"						<th colspan=3 >Previous load (% load) </th>\n\",
\"					</tr>\n\",
\"					<tr>\n\",
\"						<th>Users logged in </th>\n\",
\"						<th>CPU Model</th>\n\",
\"						<th>Current CPU clock speed</th>\n\",
\"						<th>Nominal CPU clock speed</th>\n\",
\"						<th> Number of running processes </th>\n\",
\"						<th> Memory Usage </th>\n\",
\"						<th>1 min</th>\n\",
\"						<th>5 min</th>\n\",
\"						<th>15 min</th>\n\",
\"					</tr>\n\",
\"				</thead>\n\",
\"				<tbody>\n\",
\"					<tr>\n\",
\"						<td align=center >\" data[\"users\"] \"</td>\n\",
\"						<td align=center >\"data[\"cpumodel\"] \"</td>\n\",
\"						<td align=center >\"data[\"cpumhz\"]\"</td>\n\",
\"						<td align=center >\" data[\"cpunom\"] \"</td>\n\",
\"						<td align=center >\" data[\"numproc\"] \"</td>\n\",
\"						<td align=center >\" (kb_to_gb(data[\"memtot\"])-kb_to_gb(data[\"memfree\"])) \" GB / \" kb_to_gb(data[\"memtot\"]) \" GB</td>\n\",
\"						<td align=center >\" data[\"avgload0\"] \"</td>\n\",
\"						<td align=center >\" data[\"avgload1\"] \"</td>\n\",
\"						<td align=center >\" data[\"avgload2\"] \"</td>\n\",
\"					</tr>\n\",
\"				</tbody>\n\",
\"			</table>\n\",
\"		</div>\n\",
\"		</div>\"
		} }
	" >> $OUTPUT
done

echo """
<div>
<table>
	<tr>
	  <td colspan="7">
		<span style='background-color: green'>Light load</span>
		<span style='background-color: yellow'>Medium load</span>
		<span style='background-color: red'>Heavy load</span>
		<span style='background-color: grey'>Unreachable</span>
	  </td>
	</tr>
</table>
</div>
</body></html>
""" >> $OUTPUT
