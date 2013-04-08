#pragma once
#include "thread.h"
#include <vector>


struct Process {
  enum Type {
    SYSTEM,
    USER
  };

  // process ID
  int pid;

  // process type
  Type type;

  // threads belonging to this process
  std::vector<Thread*> threads;

  // constructor
  Process(int pid, Type type) : pid(pid), type(type) {}
};
