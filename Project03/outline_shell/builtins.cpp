#include "builtins.h"

using namespace std;


int com_ls(vector<string>& tokens) {
	// if no directory is given, use the local directory
	if (tokens.size() < 2) {
		tokens.push_back(".");
	}

	// open the directory
	DIR* dir = opendir(tokens[1].c_str());

	// catch an errors opening the directory
	if (!dir) {
		// print the error from the last system call with the given prefix
	  	perror("ls error: ");

	  	// return error
	  	return 1;
	}

	// output each entry in the directory
	for (dirent* current = readdir(dir); current; current = readdir(dir)) {
		cout << current->d_name << endl;
	}

	// return success
	return 0;
}


int com_cd(vector<string>& tokens) {
	// TODO: YOUR CODE GOES HERE
	cout << "CD's args: " << tokens[0] << ", " << tokens[1] << endl;
	//chdir(tokens[0]);
	cout << "cd called" << endl; // delete when implemented
	return 0;
}


int com_pwd(vector<string>& tokens) {
	// TODO: YOUR CODE GOES HERE
	// HINT: you should implement the actual fetching of the current directory in
	// pwd(), since this information is also used for your prompt
	cout << "pwd called" << endl; // delete when implemented
	return 0;
}


int com_alias(vector<string>& tokens) {
	// TODO: YOUR CODE GOES HERE
	cout << "alias called" << endl; // delete when implemented
	return 0;
}


int com_unalias(vector<string>& tokens) {
	// TODO: YOUR CODE GOES HERE
	cout << "unalias called" << endl; // delete when implemented
	return 0;
}


int com_echo(vector<string>& tokens) {
	// TODO: YOUR CODE GOES HERE
	cout << "echo called" << endl; // delete when implemented
	return 0;
}


int com_exit(vector<string>& tokens) {
	cout << "exit called" << endl; // delete when implemented
	exit(0);
}


int com_history(vector<string>& tokens) {
	// TODO: YOUR CODE GOES HERE
	cout << "history called" << endl; // delete when implemented
	return 0;
}

string pwd() {
	// TODO: YOUR CODE GOES HERE
	return NULL;
}

