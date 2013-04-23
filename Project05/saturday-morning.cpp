#include "common.h"
#include "player.h"
#include "golf_course.h"
#include "control_file.h"
#include <sstream>
#include <fstream>

int main(int argc, char **argv) {

  if (argc != 2) {
    cerr << "Usage: " << argv[0] << " control-file" << endl;
    return 1;
  }

  boost::thread_group threads;
  boost::xtime create_time;

  GolfCourse* golf_course = new GolfCourse();
  ControlFile control_file(argv[1]);

	// Create all the players in the control file, giving them unique ids and
  // assiging them to parties in the order they arrive.
  int id = 0;

  for (unsigned int i = 0; i < control_file.data.size(); i++) {
    int party_number = id / 4; // integer division

    boost::xtime_get(&create_time, boost::TIME_UTC);

    Player p(id, control_file.data[i].name, control_file.data[i].mean,
        control_file.data[i].sigma, party_number, golf_course, create_time);

    threads.create_thread(p);

    // Wait to create the next thread
    make_thread_sleep(control_file.data[i].sleep);
    ++id;
  }

  // Don't let main() exit until all the threads have reached this point.
  threads.join_all();

  cout << "Average turnaround time: " << golf_course->average_turnaround_time()
       << " seconds." << endl;

  return 0;
}
