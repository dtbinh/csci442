#pragma once
#include "common.h"
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <boost/thread/xtime.hpp>

using namespace std;

struct control_struct {
  string name;
  double mean;
  double sigma;
  int sleep;
};

struct ControlFile {
  ControlFile(char* filename) {
    ifstream input_file(filename);
    string line;

    while (getline(input_file, line)) {
      control_struct cs;

      if (line[0] != '#' && line.size() > 0) {
        istringstream ist(line);
        ist >> cs.name >> cs.mean >> cs.sigma >> cs.sleep;
        data.push_back(cs);
      }
    }

    input_file.close();
  }

  vector<control_struct> data;
};
