#pragma once
#include "burst.h"

// forward declaration
struct Process;


struct Thread {
  // arrival time
  int arrival_time;

  // thread id
  int tid;

  // all bursts that are a part of this thread
  //std::vector<Burst*> bursts;
  //
  // list of bursts that are part of this thread. Last element is NULL
  Burst** bursts;

  // the process assocated with this thread
  Process* process;

  // the time at which the last I/O burst started; if no active I/O burst,
  // then this should be set to -1
  int last_io_start;

  // constructor
  Thread(int arrival, int tid, Process* process) :
      arrival_time(arrival), tid(tid), process(process), last_io_start(-1) {}
};
