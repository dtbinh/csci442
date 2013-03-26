#include "builtins.h"
#include "unistd.h"
#include <sys/stat.h>
#include <sys/types.h>
#include <regex.h>
#include <readline/history.h>

using namespace std;
map<string, string> alias_map;

bool dir_exists( const char* pzPath ) {
	return access(pzPath, F_OK) == 0;
}

/*
 * Check to see if the tokens list contains the flag. If so, it will be removed.
 */
bool has_flag(string flag, vector<string>& tokens) {
	for(vector<string>::iterator iter = tokens.begin(); iter != tokens.end(); iter++) {
		if (flag.compare(*iter) == 0) {
			tokens.erase(iter);
			return true;
		}
	}
	return false;
}

int com_ls(vector<string>& tokens) {
	if (has_flag("--help", tokens)) {
		printf("Usage: ls [options] [directories...]\n\tOptions:\n\t\t-a:\tShow hidden directories as well\n");
		return 0;
	}
	bool show_hidden = has_flag("-a", tokens);

	// if no directory is given, use the local directory
	if (tokens.size() < 2) {
		tokens.push_back(".");
	}

	// ls for all the directories supplied
	for (int i=1; i < tokens.size(); i++) {
		if (tokens.size() > 2) printf("%s:\n", tokens[i].c_str());
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
			if (show_hidden || current->d_name[0] != '.') {
				printf("%s\n", current->d_name);
			}
		}
		if (tokens.size() > 2) printf("\n");
	}

	// return success
	return 0;
}


int com_cd(vector<string>& tokens) {
	if (tokens.size() < 2) perror("Please provide a directory to change to.\n");
	if (!dir_exists(tokens[1].c_str())) {
		char error_string[PATH_MAX + 26];
		fprintf(stderr, "%s is not a valid directory\n", tokens[1].c_str());
		return -1;
	}

	return chdir(tokens[1].c_str());
}


int com_pwd(vector<string>& tokens) {
	printf("%s\n", pwd());
	return 0;
}


int com_alias(vector<string>& tokens) {
	if (tokens.size() == 1) {
		// print all the aliases
		for (map<string, string>::iterator iter = alias_map.begin(); iter != alias_map.end(); iter++) {
			string command = iter->second;
			string name = iter->first;

			printf("%s=%s\n", name.c_str(), command.c_str());
		}
	} else {
		// extract the mappings
		for (int i = 1; i < tokens.size(); i++) {
			int eq_idx = tokens[i].find_first_of('=');
			string name = tokens[i].substr(0, eq_idx);
			string command = tokens[i].substr(eq_idx+1, tokens[i].size()-eq_idx);

			alias_map[name] = command;
		}
	}
	return 0;
}


int com_unalias(vector<string>& tokens) {
	bool unalias_everything = false;
	if (has_flag("-a", tokens)) {
		unalias_everything = true;
		alias_map.clear();
	}

	// if unalias_everything, we don't have any aliases left
	if (!unalias_everything) {
		for (int i=1; i < tokens.size(); i++) {
			alias_map.erase(tokens[i]);
		}
	}
	return 0;
}


int com_echo(vector<string>& tokens) {
	for (int i=1; i < tokens.size(); i++) {
		printf("%s", tokens[i].c_str());
		if (i < tokens.size()-1) {
			printf(" ");
		}
	}
	printf("\n");
	return 0;
}


int com_exit(vector<string>& tokens) {
	exit(0);
}


int com_history(vector<string>& tokens) {
	HIST_ENTRY** all_hist = history_list();

	for (int i=where_history()-21; i < where_history() - 1; i++) {
		if (i >= 0) {
			printf("%d:\t%s\n", i, all_hist[i]->line);
		}
	}
	return 0;
}

char* pwd() {
	char* result;
	char* buffer = (char*) calloc(sizeof(char), 255);
	size_t size;
	result = getcwd(buffer, size);
	if (result == buffer) {
		// buffer holds the current working directory
		return buffer; 
	} else {
		// getcwd failed
		perror("Could not get PWD\n");
		return NULL;
	}
}
