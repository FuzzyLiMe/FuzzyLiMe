/*
 * gcc vuln.c -o vuln
 * ./vuln aa %c%c
*/

#include <stdio.h>

int main(int argc, char **argv) {
    if (argc > 2) {
        sscanf(argv[1], argv[2]);
    }
}