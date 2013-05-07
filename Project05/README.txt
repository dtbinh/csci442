Project 5: Golf Course Simulation
Matt Buland

Contained files:
README.txt

example_input_files/easy
example_input_files/harder
example_input_files/medium

src/common.h
src/control_file.h
src/golf_course.h
src/makefile
src/player.h
src/saturday-morning.cpp

Spent on project: ~6 hrs. Mostly just trying to find boost documentation. Worst library ever.

Barriers enforce that a certain number of threads must wait on it before unblocking them, and letting them all continue
Condition variables enforce that a certain condition must be met before continueing. Also with it comes a unique lock; Once the condition is fulfilled, there's only one person that can lock the mutex.

Party play-throughs are possible because of the non-deterministic choice made by the recipient of a mutex lock after it's been unlocked. When a party takes control of the lock on a hole (line ####), it locks the mutex, disallowing any other party from playing on the hole. If there's already a party playing on the hole, the party will wait for the playing party to be done. When there are multiple parties waiting, and the playing party finishes, one of the waiting parties will receive the lock, but it's not guaranteed who, thus randomizing the party order.
