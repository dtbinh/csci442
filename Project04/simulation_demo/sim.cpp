#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <fstream>
#include "simulation.h"
#include "process.h"
#include "thread.h"
#include "burst.h"

using namespace std;

int main(int argc, char** argv) {
  string filename;

  // you'll need to add flag parsing; this is just a simple example. =)

  // ensure proper number of arguments
  if (argc != 2) {
    cerr << "USAGE: sim simulation_file" << endl;
    exit(EXIT_FAILURE);
  }

  // open the simulation file
  ifstream file(argv[1]);

  if (!file) {
    cerr << "Could not open file " << filename << endl;
    exit(EXIT_FAILURE);
  }

  // create the simulation
  Simulation simulation(file);

  // do stuff with the simulation here

  // EXAMPLE: print all bursts in every thread in every process
  for (map<int, Process*>::iterator process_it = simulation.processes.begin();
      process_it != simulation.processes.end();
      ++process_it) {
    // processing a single process
    Process* process = process_it->second;

    cout << "Process "
        << process->pid
        << " (a "
        << (process->type == Process::SYSTEM ? "system" : "user")
        << " process) has the following threads:"
        << endl;

    for (vector<Thread*>::iterator thread_it = process->threads.begin();
        thread_it != process->threads.end();
        ++thread_it) {

      // processing a single thread
      Thread* thread = (*thread_it);

      cout << "  Thread "
          << thread->tid
          << " arrives at "
          << thread->arrival_time
          << " and has the following bursts:"
          << endl;

      for (vector<Burst*>::iterator burst_it = thread->bursts.begin();
          burst_it != thread->bursts.end();
          ++burst_it) {

        // processing a single burst
        Burst* burst = (*burst_it);

        cout << "    "
            << (burst->type == Burst::CPU ? "CPU" : "IO")
            << " burst for length "
            << burst->length
            << endl;
      }
    }
  }

  // EXAMPLE: using events and the priority queue
  // the threads specified are NULL in the example, but you should specify
  // your own

  // event 1 indicates that a process arrives at 50
  Event* event1 = new Event(Event::ARRIVAL, NULL, 50);

  // event 2 indicates that a thread is done with I/O at 27; the NULL would
  // specify the thread that was done with its I/O
  Event* event2 = new Event(Event::IO_DONE, NULL, 27);

  // add the events to the simulation
  simulation.events.push(event1);
  simulation.events.push(event2);

  // the first event to come back should be at 27, and the second should be 50
  cout << "The first event to return happens at "
      << simulation.events.top()->time
      << endl;
  simulation.events.pop();

  // get the next event
  cout << "The second event to return happens at "
      << simulation.events.top()->time
      << endl;
  simulation.events.pop();

  // close the file
  file.close();

  return EXIT_SUCCESS;
}
