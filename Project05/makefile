# If you install Boost somewhere else, update this
BOOST_ROOT = /usr/lib
CC = g++
CFLAGS = -g -Wall -I $(BOOST_ROOT) -D_REENTRANT
LFLAGS = -L $(BOOST_ROOT)/stage/lib

LIBS = -lboost_thread -pthread

TARGETS = saturday-morning
HEADERS = common.h control_file.h player.h golf_course.h
DEPENDS =

%.o: %.cpp $(HEADERS)
	$(CC) $(CFLAGS) -c $<

all: $(TARGETS)

saturday-morning: saturday-morning.o $(DEPENDS) $(HEADERS)
	$(CC) -o $@ $(LFLAGS) $< $(DEPENDS) $(LIBS)

clean:
	rm -f $(TARGETS) *.o *~
