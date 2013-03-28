#pragma once

struct Burst {

  enum Type {
    CPU,
    IO
  };

  // type of burst
  Type type;

  // length of the burst
  int length;

  // constructor
  Burst(Type type, int length) : type(type), length(length) {}
};
