#pragma once
#include <iostream>
#include <string>
#include <boost/thread/barrier.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/xtime.hpp>

using namespace std;

bool DEBUG = true;

// The iostreams are not guaranteed to be thread-safe
boost::mutex io_mutex;

// Causes the thread to sleep for the given number of seconds.
void make_thread_sleep(double secs) {
  boost::xtime xt;
  boost::xtime_get(&xt, boost::TIME_UTC);

  int int_part = int(secs);
  double rest = (secs - int_part) * 1000000000;

  xt.sec += int_part;
  xt.nsec += int(rest);

  boost::thread::sleep(xt);
}
