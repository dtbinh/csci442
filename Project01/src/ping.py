#!/usr/bin/python

# note: This was written for Python 3

import sys
import re
from subprocess import *

# Wrapper program for ping

def main():
	if len(sys.argv) < 3:
		# The required argument was not provided
		print("Usage: ping.py <hostname> <TTL>")
		exit(0)
	
	ttl = sys.argv[2]
	hostname = sys.argv[1]
	openObj = Popen("ping -c 1 -t " + ttl + " -W 5 " + hostname, shell=True, bufsize=-1, stdout=PIPE)
	err = openObj.wait()
	#print("Errors: ")
	#print(err)
	outPipe = openObj.stdout.read()

	ret = openObj.returncode
	#print("OpenObj has finished. Result: ")
	#print(outPipe)

	# note: the outPipe contains binary data, shown as b''. b''.decode() will explicitly convert it to a string

	ln = outPipe.splitlines()[1].decode()
	#print(ln)
	res = re.match(".*[Ff]rom ?([^ ]*) \(?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*", ln)
	#print("Reached? " + str(res))
	if re.match(".*?Time to live exceeded.*",ln):
		ret_host = res.group(1)
		ret_ip = res.group(2)
		# host not yet reached
		#res = re.match("From ([^ ]*) \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*", ln)
		#ip = re.match(".*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*", ln)
		print("Hop " + ttl + ": " + ret_host + " (" + ret_ip + ")")
		exit(9)
	elif res:
		ret_host = res.group(1)
		ret_ip = res.group(2)
		print("Destination " + hostname + " reached: " + ret_host + " (" + ret_ip + ")")
		exit(0)
	else:
		# unhandled response
		print("Unhandled response")
		exit(1)

main()
