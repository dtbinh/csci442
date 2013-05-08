#pragma once
#include "common.h"
#include <vector>

struct GolfCourse {
    vector<boost::barrier*> party_barriers;
    vector<boost::mutex*> hole_locks;
	vector<boost::condition_variable*> hole_conditions;

	vector<int> hole_locked;
    vector<int> party_nums;

	GolfCourse() {
		for (int i = 0; i < 18; i++) {
			// This is where you will initialize your barriers, condition variables,
			// and any other shared variables or synchronization primitives.
            //party_barriers.push_back(new boost::barrier(4));
            hole_locks.push_back(new boost::mutex());
			hole_locked.push_back(-1);
			hole_conditions.push_back(new boost::condition_variable());
		}
	}

	~GolfCourse() {
		cout <<"Deconstructing golf course\n";
		for (vector<boost::barrier*>::iterator iter = party_barriers.begin(); iter != party_barriers.end(); iter++) {
			free(*iter);
			iter = party_barriers.erase(iter);
		}
		for (vector<boost::mutex*>::iterator iter = hole_locks.begin(); iter != hole_locks.end(); iter++) {
			free(*iter);
			iter = hole_locks.erase(iter);
		}
		for (vector<boost::condition_variable*>::iterator iter = hole_conditions.begin(); iter != hole_conditions.end(); iter++) {
			free(*iter);
			iter = hole_conditions.erase(iter);
		}
	}

	// Compute the average turnaround time over all the golfers that have
	// completed the course.
	double average_turnaround_time() {
		boost::xtime sum;
		sum.sec = 0;
		sum.nsec = 0;

		vector<boost::xtime>::iterator it;

		for (it = turnaround_times.begin(); it != turnaround_times.end(); ++it) {
			sum.sec += it->sec;
			sum.nsec += it->nsec;
		}

		double sum_sec = (double) sum.sec + ((double) sum.nsec) / 1000000000.0;
		return sum_sec / turnaround_times.size();
	}

	// This is where you will define your barriers, condition variables, and any
	// other shared variables or synchronization primitives. The variables are
	// currently public to keep it simple.
	vector<boost::xtime> turnaround_times;

};
