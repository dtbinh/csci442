#include <stdlib.h>
#include <string.h>
#include <stdio.h>
/* stdio is only needed for printf */

size_t begins_with(char* text, const char* beg) {
	size_t i = 0;
	//printf("Analysing %s to start with %s\n", text, beg);
	for (; text[i] && beg[i] && text[i] == beg[i]; i++);
	printf("I is %d\n", i);
	if (i == strlen(beg)) return i;
	return 0;
}

int main() {
	printf("kitten with k %d\n", begins_with("kitten", "k"));
	printf("kitten with ki %d\n", begins_with("kitten", "ki"));
	printf("kitten with kitt %d\n", begins_with("kitten", "kitt"));
}
