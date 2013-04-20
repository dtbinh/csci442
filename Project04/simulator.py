#!/usr/bin/env python3

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
        super(MultiLevelFeedbackScheduler, self).__init__(cpu)
        self.priority_queues = []
        self.priority_quantums = [4, 5, 5, 6, 6, 7, 8, 9, 11, 15]
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

            # remove the thread from the io queue, and place it in a ready queue
            thread = None
            for t in self.io_queue:
                if t.tid == event.thread.tid:
                    thread = t
                    self.io_queue.remove(t)
                    break
            if thread is None:
                print("I have no idea how this thread got here. It's not in the io queue")
                return
            self.priority_queues[thread.priority].append(thread)

            #print("Time = %i, and %i has IO BURST DONE" % (self.cpu.cpu_time, event.thread.tid))
        elif event.action == Actions.CPU_BURST_DONE:
            # Not sure if I want to elevate it after every cpu burst
            # Elevate to a less prioritized queue
            #if event.thread.priority < len(self.priority_queues):
            #    event.thread.priority += 1

            # If the thread has an IO component next, go ahead and schedule it, so we can do some multi-tasking
            if event.thread.has_next():
                self.schedule_next_thread(event, event.thread)
            else:
                self.priority_queues[event.thread.priority].append(event.thread)
            #print("Time = %i, and %i has CPU BURST DONE" % (self.cpu.cpu_time, event.thread.tid))
        elif event.action == Actions.SWITCH_DONE:
            #print("Time = %i, and %i has switch done" % (self.cpu.cpu_time, event.thread.tid))
            # Start executing it right now by forcing the next thread to be this one
            self.schedule_next_thread(event, event.thread)
        elif event.action == Actions.PREEMPT:
            # Put the thread back in the ready queues, but with a higher penalty
            if event.thread.priority < len(self.priority_queues):
                event.thread.priority += 1
            self.priority_queues[event.thread.priority].append(event.thread)

        #if self.cpu.current_event:
            #print("The CPU's current event will finish at %i, and is %s" % (self.cpu.current_event.time, reverse_actions(self.cpu.current_event.action)))
        #if event.action == != Actions.SWITCH_DONE and self.cpu.current_event.time <= self.cpu.cpu_time:

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
                    #print("Proc swap needed")
                    delay += self.cpu.proc_overhead
                elif next_thread.tid != last_event.thread.tid:
                    #print("Thread swap needed")
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
                            self.io_queue.append(next_thread)
                        elif next_burst[1] == Actions.CPU_BURST_DONE:
                            current_action = Actions.CPU_BURST_START

                            # if the preempt will happen before the burst is done, we need to not make that burst not finish, but replace with it with a preemption
                            # Note. this must be here. IO operations do not need to be preempted, and system processes CANNOT be preempted
                            quantum = self.get_quantum(next_thread.priority)
                            if next_thread.parent_process.ptype > 0 and delay > quantum:
                                # we're going to cut it off before it's done. Schedule the preemption
                                next_action = Actions.PREEMPT
                                delay -= next_burst[0] - quantum

                                # correct the remaining burst time
                                next_thread.correct_burst(quantum)
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

                # if we just scheduled some IO, let's move on, since it's backgrounded
                if next_event.action == Actions.IO_BURST_DONE:
                    self.schedule_next_thread(next_event)
            else:
                # Thread has no more work to do. Cool. Let's forget about it then.
                #print("Thread %i has no more bursts" % (next_thread.tid), self.cpu.event_queue)
                # Let's try to schedule any remaining processes
                self.schedule_next_thread(last_event)
                pass
        else:
            # no known threads left to execute. So, we're either done, or waiting on IO
            #print("No more active threads", self.cpu.event_queue)
            pass

    # return a tuple containing the queue's preemption time, and the thread
    def get_next_thread(self):
        for q in self.priority_queues:
            if q:
                return q.popleft()

    def get_quantum(self, priority):
        return self.priority_quantums[priority]

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

    #print("At time %i, Thread %i, belonging to Process %i %s." % (time, event.thread.tid, event.thread.parent_process.pid, message))
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

# show this for all modes
stats.total_time()
#stats.total_time_per()
stats.utilization()
stats.response_time()

# show for detailed
if detailed or verbose:
    stats.arrival_time()
    stats.service_time()
    stats.finish_time()
if verbose:
    stats.all_events()
