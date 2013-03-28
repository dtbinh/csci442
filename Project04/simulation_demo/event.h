#pragma once
#include "thread.h"
#include "burst.h"
#include "process.h"
#include <iostream>


struct Event {

  enum Type {
    // feel free to add your own events
    ARRIVAL,
    IO_DONE
  };

  // the type of event
  Type type;

  // the thread for which the event applies
  Thread* thread;

  // the time at which the event occurs
  int time;

  // constructor
  Event(Type type, Thread* thread, int time) :
      type(type), thread(thread), time(time) {}
};

// comparator for std::priority_queue to correctly order event pointers
struct EventComparator {
  bool operator()(Event* e1, Event* e2) {
     return e1->time >= e2->time;
  }
};
