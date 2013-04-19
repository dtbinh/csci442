
import sys

from collections import deque
import heapq

# Suggested by http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class Scheduler:
    def __init__(self, cpu=None):
        self.cpu = cpu

    def event_happens(self, event):
        print("Event hapened: " + reverse_actions(event.action))

class PriorityQueue:
    def __init__(self):
        pass

class Statistics:
    stats = []

    def add_tuple(self, tpl):
        add_entry(tpl[0], tpl[1]. tpl[2])

    def add_entry(self, cpu_time, thread, action):
        self.stats.append((cpu_time, thread, action))

    def calc_utilization(self):
        # Grab the time from the last statistic
        tot_time = self.stats[-1][0]
        not_io = 0
        # Last...
        # 0 = CPU
        # 1 = switch
        lasts = [0, 0]
        last_cpu = 0
        last_switch = 0
        for stat in self.stats:
            #print("Stat: %i, %s, %i, %s" % (stat[0], stat[1].tid, stat[2], reverse_actions(stat[2])))

            if stat[2] == Actions.CPU_BURST_DONE:
                not_io += stat[0] - lasts[0]
            elif stat[2] == Actions.CPU_BURST_START:
                lasts[0] = stat[0]
            elif stat[2] == Actions.SWITCH_DONE:
                not_io += stat[0] - lasts[1]
            elif stat[2] == Actions.SWITCH_START:
                lasts[1] = stat[0]
        #print("Total time: %i, CPU Time: %i. Divided %i" % (tot_time, not_io, (not_io*100/tot_time)))
        if tot_time > 0:
            print("CPU Utilization: %i%%" % (not_io*100/tot_time))

    def calc_response_time(self):
        response_map = {}
        #print("Stats:", self.stats)
        for stat in self.stats:
            #print("Time %s, Thread %i, Action %s" % (stat[0], stat[1].tid, reverse_actions(stat[2])))
            if stat[1] not in response_map:
                # 0 = Arrival Time
                # 1 = Switch started
                # 2 = Response time
                response_map[stat[1]] = [None, None]

            if stat[2] == Actions.ARRIVAL:
                response_map[stat[1]][0] = stat[0]
            elif stat[2] is Actions.SWITCH_START and response_map[stat[1]][1] is None:
                # This is the first switch start for the thread
                #print("Thread %s will have a response of %i" % (stat[1], stat[0] - response_map[stat[1]][1]))
                response_map[stat[1]][1] = stat[0]
        #print("Response map:", response_map)

        tot_response = 0
        for key, value in response_map.items():
            try:
                print("Thread %i had a response time of %i" % (key.tid, value[1]-value[0]))
                tot_response += value[1] - value[0]
            except KeyError:
                sys.stderr.write("Wtf? A thread %s didn't have a response time..." % (value))
        if len(response_map) > 0:
            avg_response = tot_response/len(response_map)
            print("Average response time: %i" % (avg_response))

    def calc_total_time(self):
        # The final event's CPU timer should tell use when the CPU stopped doing things
        last_time = self.stats[-1][0]
        print("Total time to completion: %i" % (last_time))

Actions = enum(ARRIVAL=0, IO_BURST_DONE=1, IO_BURST_START=2, CPU_BURST_DONE=3, CPU_BURST_START=4, SWITCH_DONE=5, SWITCH_START=6, PREEMPT=7 )
def reverse_actions(val):
    if val == 0: return "ARRIVAL"
    elif val == 1: return "IO_BURST_DONE"
    elif val == 2: return "IO_BURST_START"
    elif val == 3: return "CPU_BURST_DONE"
    elif val == 4: return "CPU_BURST_START"
    elif val == 5: return "SWITCH_DONE"
    elif val == 6: return "SWITCH_START"
    elif val == 7: return "PREEMPT"

class CPU:
    def __init__(self, thread_overhead, proc_overhead, scheduler):
        self.process_pool = []
        self.event_queue = []

        #self.priority_queue = deque()

        self.thread_overhead = int(thread_overhead)
        self.proc_overhead = int(proc_overhead)
        self.cpu_time = 0
        self.scheduler = scheduler

        self.current_event = None

    def run(self):
        for event in heapgen(self.event_queue):
            self.cpu_time = event.time
            self.scheduler.event_happens(event)

    def add_event(self, event):
        heapq.heappush(self.event_queue, event)

    def create_event_queue(self):
        for proc in self.process_pool:
            for trd in proc.threads:
                heapq.heappush(self.event_queue, Event(trd.arrival_time, trd, Actions.ARRIVAL))
        self.current_event = self.event_queue[0]

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
        self.priority = 0
        self.next_index = 0

    def next_burst(self):
        for b in self.bursts:
            yield b

    def has_next(self):
        return self.next_index < len(self.bursts)*2

    def next_burst_time(self):
        # since bursts contain both a CPU, and an IO, the next_index represents a linear index for cpu/io/cpu/io/...
        if self.next_index < len(self.bursts)*2:
            burst_index = self.next_index // 2
            if self.next_index % 2 == 0:
                # CPU
                self.next_index += 1
                return (self.bursts[burst_index].cpu_time, Actions.CPU_BURST_DONE)
            else:
                # IO
                self.next_index += 1
                return (self.bursts[burst_index].io_time, Actions.IO_BURST_DONE)
        else:
            return None
        
    def reset_bursts(self):
        self.next_index = 0

    def next_burst_time_generator(self):
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
