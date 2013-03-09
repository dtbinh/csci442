/cpu[0-9]+ / { 
	match($1, "[0-9]+");
	cpuNum = substr($1, RSTART, RLENGTH);
	print "CPU Num: " cpuNum
	oldsum = cpuArray[cpuNum, 0];
	cpuArray[cpuNum, 0] = 0;
	for ( i = 2; i <= NF; i++ ) { cpuArray[cpuNum, 0] += $i };
	oldidle = cpuArray[cpuNum, 1];
	cpuArray[cpuNum, 1] = $5;
	diffsum = cpuArray[cpuNum, 0] - oldsum;
	diffidle = cpuArray[cpuNum, 1] - oldidle;
	cpuArray[cpuNum, 2] = (( diffsum - diffidle ) / diffsum ) * 100;
	print "Array num 2: " cpuArray[cpuNum, 2]
}
END {
	print  sprintf("CPU%d Utilization: ", 0) cpuArray[0, 2]
}
