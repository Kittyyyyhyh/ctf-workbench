#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void win(void) {
    FILE *f = fopen("/flag.txt", "r");
    char buf[128];
    if (!f) {
        puts("flag file missing");
        exit(1);
    }
    fgets(buf, sizeof(buf), f);
    printf("flag: %s\n", buf);
    fclose(f);
}

void vuln(void) {
    char buf[64];
    puts("input> ");
    read(0, buf, 256);
    puts("bye");
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    vuln();
    return 0;
}
