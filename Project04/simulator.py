#!/usr/bin/env python

# NOTE: This is made for python3.
# It MAY work for python2, but it is explicitly created for python3. 

import sys

#if sys.version_info < 3:
#    sys.stderr.write("Run this with python3. You should not be using python2 anymore")
#    exit(1)

from collections import deque
import heapq
import getopt

# Suggested by http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

Actions = enum(ARRIVAL=0, IO_BURST_DONE=1, CPU_BURST_DONE=2, SWITCH_DONE=3)
def reverse_actions(val):
    if val == 0: return "ARRIVAL"
    elif val == 1: return "IO_BURST_DONE"
    elif val == 2: return "CPU_BURST_DONE"
    elif val == 3: return "SWITCH_DONE"

def formalize_output(time, event):
    message = ""
    if event.action == Actions.ARRIVAL:
        message = "arrived"
    elif event.action == Actions.IO_BURST_DONE:
        message = "began IO burst"
    elif event.action == Actions.CPU_BURST_DONE:
        message = "began CPU burst"
    elif event.action == Actions.SWITCH_DONE:
        message = "began being swapped in"

    print("At time %i, Thread %i, belonging to Process %i %s." % (time, event.thread.tid, event.thread.parent_process.pid, message))

class CPU:

    def __init__(self, thread_overhead, proc_overhead):
        self.process_pool = []
        self.event_queue = []

        self.priority_queue = deque()

        self.next_time = 0

        self.thread_overhead = int(thread_overhead)
        self.proc_overhead = int(proc_overhead)
        self.cpu_time = 0

    def simulate(self):
        if len(self.event_queue) == 0:
            self.create_event_queue()
        for event in heapgen(self.event_queue):
            #print("%s Event happened at %s, with thread %s" % (reverse_actions(event.action), event.time, event.thread))
            # process the next event
            # update our cpu_time to the time the event occurs
            time_passed = event.time - self.cpu_time
            self.cpu_time = event.time
            #print("That took " + str(time_passed))
            if time_passed < 0:
                sys.stderr.write("Less than 0 time has passed. That's a neat trick!")

            next_event_time = self.cpu_time

            if event.action == Actions.ARRIVAL:
                # Load the thread into the priority queue
                #print("At time %i, Thread %i, belonging to Process %i arrived.")
                formalize_output(self.cpu_time, event)
                self.priority_queue.append(event.thread)
                if len(self.priority_queue) == 1:
                    self.schedule_next_thread(None)
            elif event.action == Actions.IO_BURST_DONE:
                next_burst = event.thread.next_burst_time()
                if next_burst:
                    # schedule the completion of that burst
                    #print("Next burst scheduled in " + str(next_burst[0]))
                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
                    formalize_output(self.cpu_time, next_event)
                    #print("At time %i, Thread %i, belonging to Process %i .")
                    heapq.heappush(self.event_queue, next_event)
                else:
                    # This thread is done executing. Let's schedule the next.
                    self.schedule_next_thread(event)
            elif event.action == Actions.CPU_BURST_DONE:
                next_burst = event.thread.next_burst_time()
                if next_burst:
                    # schedule the completion of that burst
                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
                    formalize_output(self.cpu_time, next_event)
                    heapq.heappush(self.event_queue, next_event)
                else:
                    # This thread is done executing. Let's schedule the next.
                    self.schedule_next_thread(event)
            elif event.action == Actions.SWITCH_DONE:
                if event.thread == self.priority_queue[0]:
                    # good. now, lets start working on that thread
                    next_thread = self.priority_queue.popleft()
                    next_burst = next_thread.next_burst_time()

                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
                    formalize_output(self.cpu_time, next_event)
                    heapq.heappush(self.event_queue, next_event)
            else:
                sys.stderr.write("Unknown Action " + event.action)

    def schedule_next_thread(self, last_event):
        # switch to the next thread in the queue
        switch_time = 0
        if len(self.priority_queue) == 0:
            # No more events are planned to happen. I guess that means we're done. Move along
            print("No events in priority queue")
            return
        if not last_event or last_event.thread.parent_process != self.priority_queue[0].parent_process:
            switch_time = self.proc_overhead
        elif last_event.thread != self.priority_queue[0]:
            switch_time = self.thread_overhead
        else:
            print("Somehow, we ran out of bursts for a thread, but the next scheduled thread is the same thread. Last thread: " + str(last_event.thread) + " | " + str(self.priority_queue[0]))
        #print("Switching to thread for " + str(switch_time))
        #print("Queue: " + str(self.priority_queue))
        
        next_event = Event(self.cpu_time + switch_time, self.priority_queue[0], Actions.SWITCH_DONE)
        formalize_output(self.cpu_time, next_event)
        #print("At time %i, Thread %i, belonging to Process %i began being swapped into main memory.")
        heapq.heappush(self.event_queue, next_event)


    def create_event_queue(self):
        for proc in self.process_pool:
            for trd in proc.threads:
                heapq.heappush(self.event_queue, Event(trd.arrival_time, trd, Actions.ARRIVAL))

def heapgen(heap):
    while heap:
        yield heapq.heappop(heap)

class Event:

    # Time is scheduled time (absolute). Thread is thread that wants to do something
    def __init__(self, time, thread, action):
        self.time = int(time)
        self.thread = thread
        self.action = action

    def __lt__(self, other):
        return self.time < other.time
#from Event import Actions

class Process:
    def __init__(self, pid, ptype):
        self.pid = int(pid)
        self.ptype = ptype
        self.threads = []

class Thread:
    next_tid = 0
    def __init__(self, arrival_time, proc):
        self.arrival_time = arrival_time
        self.parent_process = proc
        self.bursts = []
        self.nbt = self.next_burst_time_gen()
        self.tid = Thread.next_tid
        Thread.next_tid += 1

    def next_burst(self):
        for b in self.bursts:
            yield b

    def next_burst_time(self):
        try:
            return next(self.nbt)
        except StopIteration:
            self.nbt = self.next_burst_time_gen()
            return None

    def next_burst_time_gen(self):
        for b in self.bursts:
            if b.cpu_time > 0:
                yield (b.cpu_time, Actions.CPU_BURST_DONE)
            if b.io_time > 0:
                yield (b.io_time, Actions.IO_BURST_DONE)

class Burst:
    Type = enum(CPU=0, IO=0)
    def __init__(self, cpu_time, io_time):
        self.cpu_time = int(cpu_time)
        self.io_time = int(io_time)

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
