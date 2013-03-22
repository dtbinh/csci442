Readme for Matt Buland's shell project

Noteworthy changes from original project:
!n and !-n are implemented as getline_history, bash, zsh, etc all use them.
	!n executes the nth command, !-n executes the previous nth command
#1>&#2 	has been implemented: Redirects #1 to #2, if #2 exists. (will error if not)
