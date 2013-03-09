OBJS = shell.cpp builtins.cpp
NAME = MyShell

all: $(NAME)

MyShell: $(OBJS)
	g++ $(OBJS) -l readline -o $(NAME)
	
clean:
	rm -rf $(NAME)