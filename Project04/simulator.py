#!/usr/bin/env python

# NOTE: This is made for python3.
# It MAY work for python2, but it was created for python3. 

import sys

#if sys.version_info < 3:
#    sys.stderr.write("Run this with python3. You should not be using python2 anymore")
#    exit(1)

from collections import deque
import heapq
import getopt
from datastructures import *

class MultiLevelFeedbackScheduler(Scheduler):
    def __init__(self, cpu=None):
        super().__init__(cpu)
        self.priority_queues = []
        self.io_queue = []
        for i in range(1, 21, 2):
            self.priority_queues.append(deque())

    def event_happens(self, event):
        stats.add_entry(self.cpu.cpu_time, event.thread, event.action)
        formalize_output(event.time, event)
        #stats.add_entry(self.cpu.cpu_time, next_thread, next_action)
        #print("Event happened: " + reverse_actions(event.action))
        if event.action == Actions.ARRIVAL:
            # Add it to the end of the lowest queue
            self.priority_queues[event.thread.priority].append(event.thread)
            #print("Time = %i, and %i has arrived" % (self.cpu.cpu_time, event.thread.tid))
        elif event.action == Actions.IO_BURST_DONE:
            # Add it to the queue it was in before
            self.priority_queues[event.thread.priority].append(event.thread)
            #print("Time = %i, and %i has IO BURST DONE" % (self.cpu.cpu_time, event.thread.tid))
        elif event.action == Actions.CPU_BURST_DONE:
            # Elevate to a less prioritized queue
            if event.thread.priority < len(self.priority_queues):
                event.thread.priority += 1
            self.priority_queues[event.thread.priority].append(event.thread)
            #print("Time = %i, and %i has CPU BURST DONE" % (self.cpu.cpu_time, event.thread.tid))
        elif event.action == Actions.SWITCH_DONE:
            #print("Time = %i, and %i has switch done" % (self.cpu.cpu_time, event.thread.tid))
            # Start executing it right now by forcing the next thread to be this one
            self.schedule_next_thread(event, event.thread)


        #if self.cpu.current_event:
            #print("The CPU's current event will finish at %i, and is %s" % (self.cpu.current_event.time, reverse_actions(self.cpu.current_event.action)))
        #if event.action != Actions.SWITCH_DONE and self.cpu.current_event.time <= self.cpu.cpu_time:

        # Experimental if. It may work out where if the cpu's current event has grown to maturity, then we're done with that, and should consider finding another thread
        # Also, we'll still maintain that after a switch is done, we need to do that work first
        if event.action != Actions.SWITCH_DONE and self.cpu.current_event == event:
            #print("Time = %i, and time to look for a new thread" % (self.cpu.cpu_time))
            self.schedule_next_thread(event)


    # Figure out what the next event to add will be next
    def schedule_next_thread(self, last_event, force_thread=None):
        # Get the lowest priority thread
        if force_thread:
            next_thread = force_thread
        else:
            next_thread = self.get_next_thread()

        if next_thread:
            #print("Time = %i, and got the next thread" % (self.cpu.cpu_time))
            next_action = None
            if next_thread.has_next():
                # To bootstrap, the cpu's first action is an arrival. If the CPU starts there, then we need to do a proc-swap
                delay = 0
                if self.cpu.current_event is None or next_thread.parent_process != last_event.thread.parent_process or self.cpu.current_event.action == Actions.ARRIVAL:
                    print("Proc swap needed")
                    delay += self.cpu.proc_overhead
                elif next_thread.tid != last_event.thread.tid:
                    print("Thread swap needed")
                    delay += self.cpu.thread_overhead

                #print("Delay is %i" % (delay))
                if delay > 0:
                    current_action = Actions.SWITCH_START
                    next_action = Actions.SWITCH_DONE
                else:
                    #print("Proc/Thread already swapped in")
                    next_burst = next_thread.next_burst_time()
                    if next_burst:
                        next_action = next_burst[1]
                        delay += next_burst[0]
                        if next_burst[1] == Actions.IO_BURST_DONE:
                            current_action = Actions.IO_BURST_START
                        elif next_burst[1] == Actions.CPU_BURST_DONE:
                            current_action = Actions.CPU_BURST_START
                        else:
                            sys.stderr.write("Not sure what the Action for the Next Burst is supposed to be")
                            return
                    else:
                        # Well, that thread must be done executing. Cool!
                        #stats.add_entry(self.cpu.cpu_time, next_thread, last_event.action)
                        sys.stderr.write("A thread claimed that it had remaining bursts, but it did not. Wtf?")
                        return
                #print("CPU THYME %i, next_action = %s" % (self.cpu.cpu_time, reverse_actions(next_action)))
                stats.add_entry(self.cpu.cpu_time, next_thread, current_action)
                formalize_output(cpu.cpu_time, Event(cpu.cpu_time, next_thread, current_action))

                #print("Scheduled next event %s for time %i" % (reverse_actions(next_action), self.cpu.cpu_time+delay))
                next_event = Event(self.cpu.cpu_time + delay, next_thread, next_action)
                heapq.heappush(self.cpu.event_queue, next_event)
                #print("Setting the CPU's current action to %s, and will happen at %i" % (reverse_actions(next_event.action), next_event.time))
                self.cpu.current_event = next_event
            else:
                # Thread has no more work to do. Cool. Let's forget about it then.
                pass
        else:
            # no known threads left to execute. So, we're either done, or waiting on IO
            pass


    def get_next_thread(self):
        for q in self.priority_queues:
            if q:
                return q.popleft()

global stats
stats = Statistics()

def formalize_output(time, event):
    if event.action == Actions.ARRIVAL: message = "arrived"
    elif event.action == Actions.IO_BURST_DONE:
        message = "finished an IO burst"
    elif event.action == Actions.IO_BURST_START:
        message = "began an IO burst"
    elif event.action == Actions.CPU_BURST_DONE:
        message = "finished a CPU burst"
    elif event.action == Actions.CPU_BURST_START:
        message = "began a CPU burst"
    elif event.action == Actions.SWITCH_DONE:
        message = "finished being swapped in"
    elif event.action == Actions.SWITCH_START:
        message = "began being swapped in"
    elif event.action == Actions.PREEMPT:
        message = "was preempted"
    else:
        message = "did something unheard of"

    print("At time %i, Thread %i, belonging to Process %i %s." % (time, event.thread.tid, event.thread.parent_process.pid, message))
    #stats.add_entry(event.time, event.thread, event.action)

def heapgen(heap):
    while heap:
        yield heapq.heappop(heap)

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

mlfb_scheduler = MultiLevelFeedbackScheduler()
cpu = CPU(thread_overhead, proc_overhead, mlfb_scheduler)
mlfb_scheduler.cpu = cpu
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
cpu.run()

stats.calc_utilization()
stats.calc_response_time()

#class CPU:
#
#    def __init__(self, thread_overhead, proc_overhead):
#        self.process_pool = []
#        self.event_queue = []
#
#        self.priority_queue = deque()
#
#        self.next_time = 0
#
#        self.thread_overhead = int(thread_overhead)
#        self.proc_overhead = int(proc_overhead)
#        self.cpu_time = 0
#
#    def simulate(self):
#        if len(self.event_queue) == 0:
#            self.create_event_queue()
#        for event in heapgen(self.event_queue):
#            #print("%s Event happened at %s, with thread %s" % (reverse_actions(event.action), event.time, event.thread))
#            # process the next event
#            # update our cpu_time to the time the event occurs
#            old_time = self.cpu_time
#            time_passed = event.time - self.cpu_time
#            self.cpu_time = event.time
#            #print("That took " + str(time_passed))
#            if time_passed < 0:
#                sys.stderr.write("Less than 0 time has passed. That's a neat trick!")
#
#            next_event_time = self.cpu_time
#
#            if event.action == Actions.ARRIVAL:
#                # Load the thread into the priority queue
#                #print("At time %i, Thread %i, belonging to Process %i arrived.")
#                formalize_output(self.cpu_time, event)
#                self.priority_queue.append(event.thread)
#                if len(self.priority_queue) == 1:
#                    self.schedule_next_thread(None)
#            elif event.action == Actions.IO_BURST_DONE:
#                next_burst = event.thread.next_burst_time()
#                if next_burst:
#                    if next_burst[1] == Actions.IO_BURST_DONE:
#                        current_action = Actions.IO_BURST_START
#                    elif next_burst[1] == Actions.CPU_BURST_DONE:
#                        current_action = Actions.CPU_BURST_START
#                    else:
#                        sys.stderr.write("Not sure what the Action for the Next Burst is supposed to be")
#                    stats.add_entry(self.cpu_time, event.thread, current_action)
#
#                    # schedule the completion of that burst
#                    #print("Next burst scheduled in " + str(next_burst[0]))
#                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
#                    formalize_output(self.cpu_time, next_event)
#                    #print("At time %i, Thread %i, belonging to Process %i .")
#                    heapq.heappush(self.event_queue, next_event)
#                else:
#                    # This thread is done executing. Let's schedule the next.
#                    self.schedule_next_thread(event)
#            elif event.action == Actions.CPU_BURST_DONE:
#                next_burst = event.thread.next_burst_time()
#                if next_burst:
#                    if next_burst[1] == Actions.IO_BURST_DONE:
#                        current_action = Actions.IO_BURST_START
#                    elif next_burst[1] == Actions.CPU_BURST_DONE:
#                        current_action = Actions.CPU_BURST_START
#                    else:
#                        sys.stderr.write("Not sure what the Action for the Next Burst is supposed to be")
#                    stats.add_entry(self.cpu_time, event.thread, current_action)
#
#                    # schedule the completion of that burst
#                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
#                    formalize_output(self.cpu_time, next_event)
#                    heapq.heappush(self.event_queue, next_event)
#                else:
#                    # This thread is done executing. Let's schedule the next.
#                    self.schedule_next_thread(event)
#            elif event.action == Actions.SWITCH_DONE:
#                if event.thread == self.priority_queue[0]:
#                    # good. now, lets start working on that thread
#                    next_thread = self.priority_queue.popleft()
#                    next_burst = next_thread.next_burst_time()
#
#                    if next_burst[1] == Actions.IO_BURST_DONE:
#                        current_action = Actions.IO_BURST_START
#                    elif next_burst[1] == Actions.CPU_BURST_DONE:
#                        current_action = Actions.CPU_BURST_START
#                    else:
#                        sys.stderr.write("Not sure what the Action for the Next Burst is supposed to be")
#                    stats.add_entry(self.cpu_time, next_thread, current_action)
#
#                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
#                    formalize_output(self.cpu_time, next_event)
#                    heapq.heappush(self.event_queue, next_event)
#                else:
#                    sys.stderr.write("event thread is not the top on the priority queue. Wat do")
#            else:
#                sys.stderr.write("Unknown Action " + event.action)
#
#    def simulate_fcfs(self):
#        if len(self.event_queue) == 0:
#            self.create_event_queue()
#        for event in heapgen(self.event_queue):
#            #print("%s Event happened at %s, with thread %s" % (reverse_actions(event.action), event.time, event.thread))
#            # process the next event
#            # update our cpu_time to the time the event occurs
#            old_time = self.cpu_time
#            time_passed = event.time - self.cpu_time
#            self.cpu_time = event.time
#            #print("That took " + str(time_passed))
#            if time_passed < 0:
#                sys.stderr.write("Less than 0 time has passed. That's a neat trick!")
#
#            next_event_time = self.cpu_time
#
#            if event.action == Actions.ARRIVAL:
#                # Load the thread into the priority queue
#                #print("At time %i, Thread %i, belonging to Process %i arrived.")
#                formalize_output(self.cpu_time, event)
#                self.priority_queue.append(event.thread)
#                if len(self.priority_queue) == 1:
#                    self.schedule_next_thread(None)
#            elif event.action == Actions.IO_BURST_DONE:
#                next_burst = event.thread.next_burst_time()
#                if next_burst:
#                    if next_burst[1] == Actions.IO_BURST_DONE:
#                        current_action = Actions.IO_BURST_START
#                    elif next_burst[1] == Actions.CPU_BURST_DONE:
#                        current_action = Actions.CPU_BURST_START
#                    else:
#                        sys.stderr.write("Not sure what the Action for the Next Burst is supposed to be")
#                    stats.add_entry(self.cpu_time, event.thread, current_action)
#
#                    # schedule the completion of that burst
#                    #print("Next burst scheduled in " + str(next_burst[0]))
#                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
#                    formalize_output(self.cpu_time, next_event)
#                    #print("At time %i, Thread %i, belonging to Process %i .")
#                    heapq.heappush(self.event_queue, next_event)
#                else:
#                    # This thread is done executing. Let's schedule the next.
#                    self.schedule_next_thread(event)
#            elif event.action == Actions.CPU_BURST_DONE:
#                next_burst = event.thread.next_burst_time()
#                if next_burst:
#                    if next_burst[1] == Actions.IO_BURST_DONE:
#                        current_action = Actions.IO_BURST_START
#                    elif next_burst[1] == Actions.CPU_BURST_DONE:
#                        current_action = Actions.CPU_BURST_START
#                    else:
#                        sys.stderr.write("Not sure what the Action for the Next Burst is supposed to be")
#                    stats.add_entry(self.cpu_time, event.thread, current_action)
#
#                    # schedule the completion of that burst
#                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
#                    formalize_output(self.cpu_time, next_event)
#                    heapq.heappush(self.event_queue, next_event)
#                else:
#                    # This thread is done executing. Let's schedule the next.
#                    self.schedule_next_thread(event)
#            elif event.action == Actions.SWITCH_DONE:
#                if event.thread == self.priority_queue[0]:
#                    # good. now, lets start working on that thread
#                    next_thread = self.priority_queue.popleft()
#                    next_burst = next_thread.next_burst_time()
#
#                    if next_burst[1] == Actions.IO_BURST_DONE:
#                        current_action = Actions.IO_BURST_START
#                    elif next_burst[1] == Actions.CPU_BURST_DONE:
#                        current_action = Actions.CPU_BURST_START
#                    else:
#                        sys.stderr.write("Not sure what the Action for the Next Burst is supposed to be")
#                    stats.add_entry(self.cpu_time, next_thread, current_action)
#
#                    next_event = Event(self.cpu_time + next_burst[0], event.thread, next_burst[1])
#                    formalize_output(self.cpu_time, next_event)
#                    heapq.heappush(self.event_queue, next_event)
#                else:
#                    sys.stderr.write("event thread is not the top on the priority queue. Wat do")
#            else:
#                sys.stderr.write("Unknown Action " + event.action)
#
#    def schedule_next_thread(self, last_event):
#        # switch to the next thread in the queue
#        switch_time = 0
#        if len(self.priority_queue) == 0:
#            # No more events are planned to happen. I guess that means we're done. Move along
#            print("No events in priority queue")
#            return
#        if not last_event or last_event.thread.parent_process != self.priority_queue[0].parent_process:
#            switch_time = self.proc_overhead
#        elif last_event.thread != self.priority_queue[0]:
#            switch_time = self.thread_overhead
#        else:
#            print("Somehow, we ran out of bursts for a thread, but the next scheduled thread is the same thread. Last thread: " + str(last_event.thread) + " | " + str(self.priority_queue[0]))
#        #print("Switching to thread for " + str(switch_time))
#        #print("Queue: " + str(self.priority_queue))
#
#        stats.add_entry(self.cpu_time, self.priority_queue[0], Actions.SWITCH_START)
#        
#        next_event = Event(self.cpu_time + switch_time, self.priority_queue[0], Actions.SWITCH_DONE)
#        formalize_output(self.cpu_time, next_event)
#        #print("At time %i, Thread %i, belonging to Process %i began being swapped into main memory.")
#        heapq.heappush(self.event_queue, next_event)
#
#    def create_event_queue(self):
#        for proc in self.process_pool:
#            for trd in proc.threads:
#                heapq.heappush(self.event_queue, Event(trd.arrival_time, trd, Actions.ARRIVAL))
#
