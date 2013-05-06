#pragma once
#include "golf_course.h"
#include <boost/random/variate_generator.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/lognormal_distribution.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/xtime.hpp>
#include <ctime>
#include <cstdio>

class Player {
public:
	Player(int id, string name, double m, double s, int pNum,
			GolfCourse* course, boost::xtime start) :
		myId(id), myName(name), mean(m), sigma(s), myParty(pNum), gc(course),
		startTime(start) {

		// Seed our random number generator. Comment out these lines if you want to
		// test your code on a constant play durations
		unsigned int seed = static_cast<unsigned int>(std::time(0));
		rng.seed(static_cast<unsigned int>(seed));

		// Set up the generator the will spit out numbers from the log normal
		// distribution.	Once the generator is set up, you get random numbers
		// from it by calling it like a function, that is, operator()
		log_norm = new boost::lognormal_distribution<>(mean, sigma);
		log_norm_generator = new boost::variate_generator<boost::mt19937,
			 boost::lognormal_distribution<> >(rng, *log_norm);

		boost::mutex::scoped_lock io_lock(io_mutex);

        if (!int_in(gc->party_nums, myParty) ) {
            // create their party barrier
			printf("Adding party %i to the list of parties\n", *(&myParty));

            gc->party_nums.push_back(new int(myParty));
            gc->party_barriers.push_back(new boost::barrier(4));
        } else {
			printf("Party %i already exists in the list of parties at the index %i\n", myParty, int_find(gc->party_nums, myParty));
		}

		cout << "+++++ Player #" << myId << " (" << myName
			 << ") added to party " << myParty << endl;
	}

	bool int_in(vector<int*> vect, int item) {
        for ( int i=0; i < vect.size(); i++) {
            if ( *(vect[i]) == item ) {
                return true;
            }
        }
        return false;
	}

	bool int_find(vector<int*> vect, int item) {
        for ( int i=0; i < vect.size(); i++) {
            if ( *(vect[i]) == item ) {
                return i;
            }
        }
        return -1;
	}

	// This operator and the included function get called when the thread is
	// created
	void operator()() {
		playCourse();
	}

	// I don't think you will need to modfiy this function.
	void playCourse() {
		// Playing the course simply means playing each hole.
		for (int i = 0; i < 18; i++) {
			playHole(i);
		}

		// computing turnaround time
		boost::xtime endTime, turnaround;
		boost::xtime_get(&endTime, boost::TIME_UTC);	// record the end time
		turnaround.sec = endTime.sec - startTime.sec;
		turnaround.nsec = endTime.nsec - startTime.nsec;
		gc->turnaround_times.push_back(turnaround);
		boost::mutex::scoped_lock io_lock(io_mutex);
		double tat = (double) endTime.sec - startTime.sec +
			((double)endTime.nsec - startTime.nsec) / 1000000000;
		cout << "----- Player #" << myId << " (" << myName
			 << ") finished.	Turnaround time = "
			 << tat << " seconds." << endl;
	}

	// This is the function where you will spend the most effort. I left a few
	// fragments from my solution, but it will need lots of modification.
	void playHole(int hole) {
		if (DEBUG) {
			boost::mutex::scoped_lock io_lock(io_mutex);
			cout << "##### Player #" << myId << " (" << myName
				 << ") waiting for hole " << hole << endl;
		}

		int party_index = int_find(gc->party_nums, &myParty);
		if (DEBUG) {
			boost::mutex::scoped_lock io_lock(io_mutex);
			printf("##### Player # %i (%s) myGroup: %i party_index: %i\n", myId, myName.c_str(), myParty, party_index);
		}
        // wait for your party to catch-up

        bool i_have_responsibility = gc->party_barriers[party_index]->wait();

        //gc->hole_barriers[hole]->wait();

		boost::unique_lock<boost::mutex> lock(*(gc->hole_locks[hole]), boost::defer_lock);
		if (i_have_responsibility) {
			if (DEBUG) {
				boost::mutex::scoped_lock io_lock(io_mutex);
				cout << "##### Player #" << myId << " (" << myName
					 << ") has responsibility! " << endl;
			}

			lock.lock();

			if (DEBUG) {
				boost::mutex::scoped_lock io_lock(io_mutex);
				cout << "##### Player #" << myId << " (" << myName
					 << ") gained control over the hole " << hole << endl;
			}
		}

		// wait for our resident party member to finish inter-group negotiations
        gc->party_barriers[party_index]->wait();

		// acquire hole-lock

		// Syntax is a little funny because we have a pointer to a generator.
		// Normally, you just call generator()
		double sleep_duration = (*log_norm_generator)();

		if (DEBUG) {
			boost::mutex::scoped_lock io_lock(io_mutex);
			cout << "Player #" << myId << " (" << myName
				 << ") playing hole " << hole << " will take "
				 << sleep_duration << " seconds." << endl;
		}

		make_thread_sleep(sleep_duration/20);

		// release hole-lock
		//
		if (DEBUG) {
			boost::mutex::scoped_lock io_lock(io_mutex);
			cout << "Player #" << myId << " (" << myName
				 << ") finished playing hole " << hole << " it took "
				 << sleep_duration << " seconds." << endl;
		}

		// wait for party to finish
		gc->party_barriers[party_index]->wait();

		if (i_have_responsibility) {
			lock.unlock();

			if (DEBUG) {
				boost::mutex::scoped_lock io_lock(io_mutex);
				cout << "----- Player #" << myId << " (" << myName
					 << ") notified all on hole " << hole << endl;
			}
		}

		if (DEBUG) {
			boost::mutex::scoped_lock io_lock(io_mutex);
			cout << "$$$$$ Player #" << myId << " (" << myName
				 << ") notified."	<< endl;
		}
	}

	// Exactly one player in each party much call this function for each hole.
	void announcePlaying(int hole) {
		boost::mutex::scoped_lock io_lock(io_mutex);
		cout << ">>>>> Party number " << myParty << " is playing hole "
			 << hole << endl;
	}

	// Exactly one player in each party much call this function for each hole.
	void announceLeaving(int hole) {
		boost::mutex::scoped_lock io_lock(io_mutex);
		cout << "<<<<< Party number " << myParty << " is leaving hole "
			 << hole << endl;
	}


private:
	int myId;
	string myName;
	double mean, sigma;
	int myParty;
	GolfCourse* gc;

	boost::xtime startTime;
	boost::mt19937 rng;
	boost::lognormal_distribution<>* log_norm;
	boost::variate_generator<boost::mt19937, boost::lognormal_distribution<> >*
		log_norm_generator;
};
