#include "simulation.h"

Simulation::Simulation(std::ifstream &file) {
  int num_processes;

  file >> num_processes >> thread_overhead >> process_overhead;

  for (int process = 0; process < num_processes; process++) {
    int pid;
    int ptype;
    int num_threads;

    file >> pid >> ptype >> num_threads;

    Process::Type type = (ptype == 0) ? Process::SYSTEM : Process::USER;
    Process* p = new Process(pid, type);

    // retrieve the values for each thread
    for (int thread = 0; thread < num_threads; thread++) {
      int arrival_time;
      int num_bursts;

      file >> arrival_time >> num_bursts;

      Thread* t = new Thread(arrival_time, thread, p);

      // retrieve the values for each burst
      bool burst_type_cpu = true;

      for (int burst = 0; burst < num_bursts * 2 - 1; burst++) {
        int burst_length;

        file >> burst_length;

        Burst::Type burst_type = (burst_type_cpu ? Burst::CPU : Burst::IO);

        t->bursts.push_back(new Burst(burst_type, burst_length));

        burst_type_cpu = !burst_type_cpu;
      }

      // done processing the bursts
      // add the thread to the process
      p->threads.push_back(t);
    }

    // done processing all threads for the process
    // save the process in the simulation
    this->processes[pid] = p;
  }
}
