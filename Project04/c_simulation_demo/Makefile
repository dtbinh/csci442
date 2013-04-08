PROGRAM = sim
CC = g++
CCFLAGS = -g -Wall
OBJECTS := $(patsubst %.cpp,%.o,$(wildcard *.cpp))

all:    $(PROGRAM)

.cpp.o :
	$(CC) $(CCFLAGS) -c -o $@ $<

$(PROGRAM): $(OBJECTS)
	$(CC) $(CCFLAGS) $(LDFLAGS) -o $(PROGRAM) $(OBJECTS)

clean:
	rm -f *.o *.exe $(PROGRAM)
