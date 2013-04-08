#!/usr/bin/env python

# NOTE: This is made for python3.
# It MAY work for python2, but it is explicitly created for python3. 

import sys

if sys.version_info < 3:
    sys.stderr.write("Run this with python3. You should not be using python2 anymore")
    exit(1)

import heapq
import getopt

class CPU:
    def __init__(self, thread_overhead, proc_overhead):
        self.process_pool = []
        self.event_queue = []
        self.thread_overhead = thread_overhead
        self.proc_overhead = proc_overhead
        self.cpu_time = 0
        self.algorithm = algorithm

    def simulate(self):
        if len(event_queue) == 0:
            self.create_event_queue()
        for event in heapgen(event_queue):
            # process the next event
            # update our cpu_time to the time the event occurs
            self.cpu_time = event.time




    def create_event_queue():
        for proc in self.process_pool:
            for trd in proc.threads:
                heapq.heappush(self.event_queue, Event(trd.arrival_time, trd, Event.Actions.ARRIVAL))

def heapgen(heap):
    while heap:
        yield heappop(heap)

def enum(**enums):
    return type('Enum', (), enums)

class Event:
    Actions = enum(ARRIVAL=0, IO_DONE=1)

    # Time is scheduled time (absolute). Thread is thread that wants to do something
    def __init__(self, time, thread, action):
        self.time = time
        self.thread = thread
        self.action = action

    def __lt__(self, other):
        return self.time < other.time

class Process:
    def __init__(self, pid, ptype):
        self.pid = pid
        self.ptype = ptype
        self.threads = []

class Thread:
    def __init__(self, arrival_time, proc):
        self.arrival_time = arrival_time
        self.parent_process = proc
        self.bursts = []

    def next_burst(self):
        for b in self.bursts:
            yield b


class Burst:
    def __init__(self, cpu_time, io_time):
        self.cpu_time = cpu_time
        self.io_time = io_time

def usage():
    print("sim [OPTIONS] <sim_file>\n")
    print("""OPTIONS:
    -d  Detailed Output
    -v  Verbose Output
    -h, --help  display this usage page
""")
    exit(0)

detailed = False
verbose = False

try:
    opts, args = getopt.getopt(sys.argv[1:], 'dvh', ['help'])
except getopt.GetoptError as err:
    usage()
    print(err)
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage()
        sys.exit(2)
    elif opt in ('-d'):
        detailed = True
    elif opt in ('-v'):
        verbose = True
    else:
        usage()
        sys.exit(2)

# read in the simulation file
if len(args) < 1:
    sys.stderr.write("Please provide a simulation file")
    exit(1)
in_file = open(args[0])


# first line contains   num_proc    thread_switch_overhead     proc_switch_overhead
nproc, thread_overhead, proc_overhead = in_file.readline().split()
if not nproc or not thread_overhead or not proc_overhead:
    print("Input file does not follow standard. Expected 3 values on line 0. Received: %s, %s, %s" % (nproc, thread_overhead, proc_overhead))

cpu = CPU(thread_overhead, proc_overhead)
first = False
for line in in_file.readlines():
    vals = line.split()
    if len(vals) == 3:
        # new process definition
        # The following line will be a thread definition
        first = True
        cpu.process_pool.append(Process(vals[0], vals[1]))
    elif len(vals) == 2:
        if first:
            # new thread definition
            first = False
            cpu.process_pool[-1].threads.append(Thread(vals[0], cpu.process_pool[-1]))
        else:
            # new CPU burst
            cpu.process_pool[-1].threads[-1].bursts.append(Burst(vals[0], vals[1]))
    elif len(vals) == 1:
        # must be last CPU burst
        # next line (after a gap) will be a new thread
        first = True
        cpu.process_pool[-1].threads[-1].bursts.append(Burst(vals[0], 0))
    else:
        # blank line. ignore
        continue
in_file.close()

cpu.create_event_queue()
cpu.simulate()
# Print out all the information
#print("CPU t_oh: %s, p_oh: %s" % (cpu.thread_overhead, cpu.proc_overhead))
#for p in cpu.process_pool:
#    print("Process %s, Type: %s" % (p.pid, p.ptype))
#    for t in p.threads:
#        print("Thread at %s" % (t.arrival_time))
#        for b in t.bursts:
#            print("Burst - CPU time: %s, IO time %s" % (b.cpu_time, b.io_time))
