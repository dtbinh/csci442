#include <cstdlib>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <unistd.h>
#include <vector>

#include <readline/readline.h>
#include <readline/history.h>

#include <sys/wait.h>
#include <fcntl.h>

#include "builtins.h"

// Potentially useful #includes (either here or in builtins.h):
//	 #include <dirent.h>
//	 #include <errno.h>
//	 #include <fcntl.h>
//	 #include <signal.h>
//	 #include <sys/errno.h>
//	 #include <sys/param.h>
//	 #include <sys/types.h>
//	 #include <sys/wait.h>
//	 #include <unistd.h>

using namespace std;

// prototype for execute command. Move this once the command works
//int execute_single_command(vector<string> command, 

// Allocates and returns a char** from a vector of strings. This array is copied from the c_strs
char** vect_to_char(vector<string> str_list) {
	char** arr = (char**) malloc(sizeof(char*) * str_list.size() + 1);
	for (int i=0; i < str_list.size(); i++) {
		arr[i] = strdup(str_list[i].c_str());
		// arr[i] = (char*) malloc(sizeof(char) * str_list[i].length());
		// strcpy(arr[i], str_list[i].c_str());
	}
	arr[str_list.size()] = (char*) 0;
	return arr;
}


// The characters that readline will use to delimit words
const char* const WORD_DELIMITERS = " \t\n\"\\'`@><=;|&{(";

// An external reference to the execution environment
extern char** environ;

// Define 'command' as a type for built-in commands
typedef int (*command)(vector<string>&);

// A mapping of internal commands to their corresponding functions
map<string, command> builtins;

// Variables local to the shell
map<string, string> localvars;

char* historical_command(string line);



// Handles external commands, redirects, and pipes.
int execute_external_command(vector<string> tokens) {
	// exec command
	char** args = vect_to_char(tokens);
	//for (int k=0; k < tokens.size(); k++) {
	//	printf("arg %d: %s\n", k, args[k]);
	//}
	execvp(tokens[0].c_str(), args);
	//char* a[] = { "ls", (char*) 0 };
	//execvp("ls", a);
	
	/* TODO: OLD
	// division into sections which represent individual commands separated by pipe
	vector< vector<string> > commands;
	commands.push_back(vector<string>());
	printf("Number of tokens: %d\n", tokens.size());
	for (int i=0; i < tokens.size(); i++) {
		if (tokens[i] == "|") {
			commands.push_back(vector<string>());
		} else {
			commands.back().push_back(string(tokens[i]));
		}
	}

	 displays the commands
	printf("Commands: %d\n", commands.size());

	for (int i=0; i < commands.size(); i++) {
		printf("New Command. i=%d\n", i);
		for (int j=0; j < commands[i].size(); j++) {
			printf("Token: %s\n", commands[i][j].c_str());
		}
	}
	

	// We need to pipes. One on either end of a 'middle' process
	int ipc_old[2];
	int ipc_new[2];
	int return_val = 0;

	printf("Commands: %d\n", commands.size());
	for (int i=0; i < commands.size(); i++) {
		printf("Searching for <\n");
		bool has_filein = false;
		for (int j=0; j < commands[i].size(); j++) {
			if (commands[i][j] == "<") {
				has_filein = true;
				break;
			}
		}
		// TODO: File redirection

		// TODO: Error redirection
		
		// fork and exec!
		//printf("Pre Forking!\n");
		int id = fork();
		//printf("Post Forking!\n");
		if (id == 0) {
			bool has_com_after = i < commands.size()-1;
			bool has_com_before = i > 0;
			// I'm the child
			printf("I'm the child! ipc_old[0]=%u ipc_old[1]=%u\n", ipc_old[0], ipc_old[1]);

			// Setup input
			if (has_com_before) {
				// don't need write_side
				close(ipc_old[1]);

				// pipe -> stdin
				dup2(ipc_old[0], 0);
			}
			if (has_filein) {
				// dup2(file, 0);
			}

			// Setup output
			if (has_com_after) {
				// Setup a new pipe
				pipe(ipc_new);

				// don't need read-side
				close(ipc_new[0]);
				
				// stdout -> pipe
				dup2(ipc_new[1], 1);
			}

			// exec command
			char** args = vect_to_char(commands[i]);
			for (int k=0; k < commands[i].size(); k++) {
				printf("arg %d: %s\n", k, args[k]);
			}
			execvp(commands[i][0].c_str(), args);
			//char* a[] = { "ls", (char*) 0 };
			//execvp("ls", a);

			// Finish everything up
			// done reading
			int close_err = close(ipc_old[0]);	// doesn't matter if it fails. It probably means it's already been closed
			if (has_com_after) {
				// new -> old. the old pipe has now served its purpose
				ipc_old[0] = ipc_new[0];
				ipc_old[1] = ipc_new[1];
			}
		} else if(id > 0) {
			// I'm the parent
			printf("I'm the parent!\n");
			wait(NULL);
		} else {
			// Fork failed. We're in trouble
			printf("Fork failed! AHHH!!!\n");
			return -1;
		}
	}

	return return_val;
	TODO: OLD
	*/
}

// Executes 1 single command, and either waits on it, or forks to background


// Return a string representing the prompt to display to the user. It needs to
// include the current working directory and should also use the return value to
// indicate the result (success or failure) of the last command.
char* get_prompt(int return_value) {
	char* ps1 = (char*) calloc(sizeof(char), 255);
	char* working_dir = pwd();
	strcat(ps1, working_dir);
	if (return_value > 0) {
		// there was an error
		strcat(ps1, " =( ");
	} else {
		// 'sall good, man
		strcat(ps1, " =) ");
	}
	strcat(ps1, "% ");
	return ps1; // replace with your own code
}


// Return one of the matches, or NULL if there are no more.
char* pop_match(vector<string>& matches) {
	if (matches.size() > 0) {
		const char* match = matches.back().c_str();

		// Delete the last element
		matches.pop_back();

		// We need to return a copy, because readline deallocates when done
		char* copy = (char*) malloc(strlen(match) + 1);
		strcpy(copy, match);

		return copy;
	}

	// No more matches
	return NULL;
}


// Generates environment variables for readline completion. This function will
// be called multiple times by readline and will return a single cstring each
// time.
char* environment_completion_generator(const char* text, int state) {
	// A list of all the matches;
	// Must be static because this function is called repeatedly
	static vector<string> matches;

	// If this is the first time called, construct the matches list with
	// all possible matches
	if (state == 0) {
		// TODO: YOUR CODE GOES HERE
	}

	// Return a single match (one for each time the function is called)
	return pop_match(matches);
}


// Generates commands for readline completion. This function will be called
// multiple times by readline and will return a single cstring each time.
char* command_completion_generator(const char* text, int state) {
	// A list of all the matches;
	// Must be static because this function is called repeatedly
	static vector<string> matches;

	// If this is the first time called, construct the matches list with
	// all possible matches
	if (state == 0) {
		// TODO: YOUR CODE GOES HERE
	}

	// Return a single match (one for each time the function is called)
	return pop_match(matches);
}


// This is the function we registered as rl_attempted_completion_function. It
// attempts to complete with a command, variable name, or filename.
char** word_completion(const char* text, int start, int end) {
	char** matches = NULL;

	if (start == 0) {
		rl_completion_append_character = ' ';
		matches = rl_completion_matches(text, command_completion_generator);
	} else if (text[0] == '$') {
		rl_completion_append_character = ' ';
		matches = rl_completion_matches(text, environment_completion_generator);
	} else {
		rl_completion_append_character = '\0';
		// We get directory matches for free (thanks, readline!)
	}

	return matches;
}


// Transform a C-style string into a C++ vector of string tokens, delimited by
// whitespace.
vector<string> tokenize(const char* line) {
	vector<string> tokens;
	string token;

	// istringstream allows us to treat the string like a stream
	istringstream token_stream(line);

	while (token_stream >> token) {
		tokens.push_back(token);
	}

	// Search for quotation marks, which are explicitly disallowed
	/* TODO: Search for quotation marks, and combine the contents as 1 single token
	for (size_t i = 0; i < tokens.size(); i++) {

		if (tokens[i].find_first_of("\"'`") != string::npos) {
			cerr << "\", ', and ` characters are not allowed." << endl;

			tokens.clear();
		}
	}
	*/

	return tokens;
}

int execute_command(vector<string> tokens, bool run_in_parent, bool parent_waits) {
	if (tokens.size() < 1) { return -1; }

	int return_value = -1;
	
	// Builtin?
	map<string, command>::iterator cmd = builtins.find(tokens[0]);
	command builtin = NULL;

	if (cmd != builtins.end()) {
		builtin = cmd->second;
	}
	run_in_parent = (builtin != NULL);

	if (run_in_parent) {
		// we're disallowing external commands to take over the shell, so run the builtin
		if (builtin) {
			return_value = (*builtin)(tokens);
		} else {
			printf("External commands taking over the shell is EXPLICITLY dissallowed.\n");
			return_value = -1;
		}
	} else {
		// fork and exec!

		int pid = fork();
		if (pid < 0) {
			printf("FORK FAILED! AH MUH GYAD\n");
		} else if (pid == 0) {
			// I'm the child
			printf("I'm the child\n");
			if (builtin) {
				return_value = (*builtin)(tokens);
			} else {
				return_value = execute_external_command(tokens);
			}
		} else {
			// I'm the parent
			printf("I'm the parent. Wait? %d\n", parent_waits);
			if (parent_waits > 0) {
				// wait for all children to finish
				int* child_return;
				printf("Waiting on child\n");
				//waitpid(pid, child_return, 0);
				wait(NULL);
				printf("Child returned with %d\n", *child_return);
				//wait(NULL);
			}
		}
	}
	return return_value;
}

/*
 *	structure planning
 *
 *	execute_line
 *		create executable 'packets'
 *		loop:
 *			setup pipes/file redirection
 *			fork
 *				dup
 *				execution_step()
 *			close handlers
 *
 * execution_step()
 * 		takes file_handler[3] (in, out, err)
 * 		exec
 * 		call it good. let the parent function close everything
 *
 */


// Executes a line of input by either calling execute_external_command or
// directly invoking the built-in command.
int execute_line(vector<string>& tokens, map<string, command>& builtins) {
	/* Old, don't care
	int return_value = 0;

	if (tokens.size() != 0) {
		map<string, command>::iterator cmd = builtins.find(tokens[0]);

		if (cmd == builtins.end()) {
			return_value = execute_external_command(tokens);
		} else {
			return_value = ((*cmd->second)(tokens));
		}
	}

	return return_value;
	*/

	// division into sections which represent individual commands separated by pipe
	vector< vector<string> > commands;
	commands.push_back(vector<string>());
	//printf("Number of tokens: %d\n", tokens.size());
	for (int i=0; i < tokens.size(); i++) {
		if (tokens[i] == "|") {
			commands.push_back(vector<string>());
		} else {
			commands.back().push_back(string(tokens[i]));
		}
	}

	/* displays the commands
	printf("Commands: %d\n", commands.size());

	for (int i=0; i < commands.size(); i++) {
		printf("New Command. i=%d\n", i);
		for (int j=0; j < commands[i].size(); j++) {
			printf("Token: %s\n", commands[i][j].c_str());
		}
	}
	*/

	// We need two pipes. One on either end of a 'middle' process. if they aren't used, they aren't used
	// TODO: pipes
	int ipc_old[2];
	int ipc_new[2];
	int return_val = 0;

	//printf("Commands: %d\n", commands.size());
	for (int i=0; i < commands.size(); i++) { 
		//printf("Command: %s\n", commands[i][0].c_str());
		for (int j=0; j < commands[i].size(); j++) {
			//printf("Arg %d: %s\n", j, commands[i][j].c_str());
		}
		bool has_pipein = i > 0;
		bool has_pipeout = i < commands.size()-1;

		// filein is the index that has the file name
		int filein = -1;
		for (int j=0; j < commands[i].size(); j++) {
			if (commands[i][j] == "<") {
				filein = j;
				break; } }

		char* fi_name = NULL;
		char* fo_name = NULL;
		int read_type = -1;
		int write_type = -1;
		for (vector<string>::iterator j = commands[i].begin(); j != commands[i].end(); j++) {
			if (*j == ">") {
				commands[i].erase(j);
				fo_name = strdup((*j).c_str());
				write_type = O_WRONLY & O_APPEND;
				commands[i].erase(j);
				break; }
			if (*j == ">>") {
				commands[i].erase(j);
				fo_name = strdup((*j).c_str());
				write_type = O_WRONLY;
				commands[i].erase(j);
				break; }
			if (*j == "<") {
				commands[i].erase(j);
				fi_name = strdup((*j).c_str());
				read_type = O_RDONLY;
				commands[i].erase(j);
				break; }
		}
		
		//printf("Setting up handlers for %s\n", commands[i][0].c_str());
		// Setup the file handlers
		int handlers[3];
		int save_status[3];

		for (int j=0; j < 3; j++) {
			handlers[j] = j;
			save_status[j] = dup(j);
		}

		if (fi_name) {
			handlers[0] = open(fi_name, read_type);
		}
		if (has_pipein) {
			if (fi_name) {
				// close the pipe. We want the file instead
				close(ipc_old[0]);
			} else {
				// read from the pipe
				handlers[0] = ipc_old[0];
			}
		}

		if (fo_name) {
			handlers[1] = open(fo_name, write_type);
		}
		//printf("Pipe out? %d\n", has_pipeout);
		if (has_pipeout) {
			if (fo_name) {
				// don't write to pipe
				// close(ipc_new[1]);
				// no worries. ipc_new is trash
			} else {
				pipe(ipc_new);
				handlers[1] = ipc_new[1];
			}
		}
		
		for (int j=0; j < 3; j++) {
			if (handlers[j] != j) {
				//printf("Duping %u to %u\n", handlers[j], j);
				dup2(handlers[j], j);
			}
		}
		
		printf("Executing %s\n", commands[i][0].c_str());
		return_val = execute_command(commands[i], 0, 1);

		printf("Closing handlers\n");
		for (int i=0; i < 3; i++) {
			//int close_status = close(handlers[i]);	// dunno what to do with the close_status
			//TODO: close detection?
			close(handlers[i]);

			// reset status
			dup2(save_status[i], i);
		}
		if (has_pipeout) {
			close(ipc_new[1]);
		}

		ipc_old[0] = ipc_new[0];
		ipc_old[1] = ipc_new[1];
		ipc_new[0] = -1;
		ipc_new[1] = -1;
	}
	return return_val;
}


// Substitutes any tokens that start with a $ with their appropriate value, or
// with an empty string if no match is found.
void variable_substitution(vector<string>& tokens) {
	vector<string>::iterator token;

	for (token = tokens.begin(); token != tokens.end(); ++token) {

		if (token->at(0) == '$') {
			string var_name = token->substr(1);

			if (getenv(var_name.c_str()) != NULL) {
				*token = getenv(var_name.c_str());
			} else if (localvars.find(var_name) != localvars.end()) {
				*token = localvars.find(var_name)->second;
			} else {
				*token = "";
			}
		}
	}
}


// Examines each token and sets an env variable for any that are in the form
// of key=value.
void local_variable_assignment(vector<string>& tokens) {
	if (tokens[0] == "alias") return;

	vector<string>::iterator token = tokens.begin();

	while (token != tokens.end()) {
		string::size_type eq_pos = token->find("=");

		// If there is an equal sign in the token, assume the token is var=value
		if (eq_pos != string::npos) {
			string name = token->substr(0, eq_pos);
			string value = token->substr(eq_pos + 1);

			localvars[name] = value;

			token = tokens.erase(token);
		} else {
			++token;
		}
	}
}


// The main program
int main() {
	// Populate the map of available built-in functions
	builtins["ls"] = &com_ls;
	builtins["cd"] = &com_cd;
	builtins["pwd"] = &com_pwd;
	builtins["alias"] = &com_alias;
	builtins["unalias"] = &com_unalias;
	builtins["echo"] = &com_echo;
	builtins["exit"] = &com_exit;
	builtins["history"] = &com_history;

	// Specify the characters that readline uses to delimit words
	rl_basic_word_break_characters = (char *) WORD_DELIMITERS;

	// Tell the completer that we want to try completion first
	rl_attempted_completion_function = word_completion;

	// The return value of the last command executed
	int return_value = 0;

	// Loop for multiple successive commands 
	while (true) {

		// Get the prompt to show, based on the return value of the last command
		char* prompt = get_prompt(return_value);

		// Read a line of input from the user
		char* line = readline(prompt);

		// If the pointer is null, then an EOF has been received (ctrl-d)
		if (!line) {
			break;
		}

		// If the command is non-empty, attempt to execute it
		if (line[0]) {

			// Deal with ! commands
			char* output;
			int event_ret = history_expand(line, &output);
			if (event_ret == 1) {
				free(line);
				line = output;
			} else if (event_ret == 2 || event_ret == -1) {
				printf("History expand returned an unhandled value.\n");
			}

			// Add this command to readline's history
			add_history(line);

			// Break the raw input line into tokens
			vector<string> tokens = tokenize(line);

			// Handle local variable declarations
			local_variable_assignment(tokens);

			// Substitute variable references
			variable_substitution(tokens);

			// Execute the line
			return_value = execute_line(tokens, builtins);
		}

		// Free the memory for the input string
		free(line);
	}

	return 0;
}
