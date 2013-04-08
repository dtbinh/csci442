#pragma once
#include <fstream>
#include <map>
#include <queue>
#include "event.h"
#include "process.h"

class Simulation {
  public:
    // map of pid -> process
    std::map<int, Process*> processes;

    // events, where the priority is the time (soonest first)
    std::priority_queue<Event*, std::vector<Event*>, EventComparator> events;

    // thread overheads for context switching
    int thread_overhead;
    int process_overhead;

    // create a simulation from a specification
    Simulation(std::ifstream& file);
};
