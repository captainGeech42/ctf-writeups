#include <stdio.h>
#include <stdlib.h>

void read_in(const char *filename, char **data) {
	*data = malloc(sizeof(char) * 203);
	FILE *f = fopen(filename, "rb");
	fgets(*data, 203, f);
	fclose(f);
}

void write_out(const char *filename, const char *data) {
	FILE *f = fopen(filename, "wb");
	fputs(data, f);
	fclose(f);
}

int main() {
	char *stuff, *stuff2;
	read_in("stuff.bin", &stuff);
	read_in("stuff2.bin", &stuff2);

	for (int i = 0; i < 203; i++) {
		stuff[i] = stuff2[202-i] ^ (stuff[i] - 1);
	}

	write_out("newstuff.bin", stuff);

	free(stuff);
	free(stuff2);

	return 0;
}
