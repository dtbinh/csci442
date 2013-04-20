Matt Buland

>30hrs so far.
    Yah... It's been a long week

simulation.py       -- Main simulation executable
datastructures.py   -- Class definitions for non-scheduling algorithm

Usage:
    simulation [options] <simulation_file>

Unusual/Interesting features:
    None to note

Hardest Part:
    The hardest part was trying to organize the program like a CPU, but without spending too much time emulating every little detail that happens

Additional Comments:

Essay Explanation:
    My Scheduling algorithm implements a multi-level feedback solution in a
    round robin manor at the individual queue level. When a process gets
    preempted (when it runs for longer than the time slice), it gets pushed to
    a less prioritized queue. This means it'll be less likely to return into
    execution, relaying to newer, shorter functions. There's no implementation
    for bringing a process/thread into a more prioritized queue. Each queue
    is individually a first come first server queue, and on the macro scale,
    there queues are chosen from in a most-important first fasion.

    First, it's assumed that the file adheres to logical paradigms, such as
    positive values, and the process swap time being greater than thread swap
    time. Next, based on my implementation, the statistic recorder assumes that
    the list of statistics is filled in chronological order.

Short Answer
    a)
        Yes, of course. When the first process/thread arrives, it wouldn't make
        any sense if it were already in memory, because then it would have had
        to go from new to running (in some way) already. Thus, yes, the very
        first arrival must go through a swap into memory before executing any
        bursts.
    b)
        Yes. It should be the case that when the CPU is idle, its current 'event'
        has a thread that is different than that of the next thread. It will
        thus go through a thread swap to begin executing.
    c)
        No. It would make no sense to swap a process that's currently running.
        It's already in memory, and does not need to be put into memory.
    d)
        No. When a preemption happens, the process/thread still exists in memory
        until another process/thread will take it's place. It's assumed that
        a 'swap' includes the code to save the current state into more permanent
        memory, and the code to place the new one into memory.
