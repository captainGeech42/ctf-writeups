#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

const char *CHARACTER_SET = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbn/+m1234567890{}_!@#$%^&*()-=_+[]\\|;:',./<>?";
const char *CORRECT = "ZXFWtmKgDZCyrmC5B+CiVfsyXUCQVfsyZRFzDU4yX2YCD/F5Ih8=";

char* unknown(char* a1) {
    int v2; // [rsp+10h] [rbp-60h]
    int v3; // [rsp+14h] [rbp-5Ch]
    int v4; // [rsp+18h] [rbp-58h]
    int v5; // [rsp+1Ch] [rbp-54h]
    int v6; // [rsp+20h] [rbp-50h]
    int v7; // [rsp+24h] [rbp-4Ch]
    int v8; // [rsp+28h] [rbp-48h]
    int v9; // [rsp+2Ch] [rbp-44h]
    int v10; // [rsp+30h] [rbp-40h]
    int v11; // [rsp+34h] [rbp-3Ch]
    int v12; // [rsp+38h] [rbp-38h]
    int v13; // [rsp+3Ch] [rbp-34h]
    char* v14; // [rsp+40h] [rbp-30h]
    int v15; // [rsp+4Ch] [rbp-24h]
    int v16; // [rsp+50h] [rbp-20h]
    int v17; // [rsp+54h] [rbp-1Ch]
    const char *v18; // [rsp+58h] [rbp-18h]
    int i; // [rsp+64h] [rbp-Ch]
    int v20; // [rsp+68h] [rbp-8h]
    int v21; // [rsp+6Ch] [rbp-4h]

    v18 = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbn/+m1234567890";
    v17 = strlen(a1);
    v16 = v17 % 3;
    v15 = v17 / 3;

    v21 = 4 * (v17 / 3) + 1;
    if ( v17 % 3 > 0 )
        v21 += 4;
    v14 = malloc(v21);
    memset(v14, 0LL, v21);
    *(unsigned char *)(v21 + v14) = 0;
    v13 = 0;
    v2 = 0;
    v20 = 0;
    v12 = 16515072;
    v11 = 258048;
    v10 = 4032;
    v9 = 63;
    for (int i = 0; i < v15; ++i )
    {
        v8 = 3 * i;
        memmove(&v2, 3 * i + a1, 3LL);
        v20 = v2 & 0xFF00 | (v2 << 16) & 0xFF0000 | (v2 >> 16);
        v7 = (v12 & v20) >> 18;
        v6 = (v11 & v20) >> 12;
        v5 = (v10 & v20) >> 6;
        v13 = v9 & v20;
        *(unsigned char*)(4 * i + v14) = v18[v7];
        *(unsigned char*)(4 * i + 1LL + v14) = v18[v6];
        *(unsigned char*)(4 * i + 2LL + v14) = v18[v5];
        *(unsigned char*)(4 * i + 3LL + v14) = v18[v13];
    }
    if ( v16 > 0 )
    {
        v4 = 3 * v15;
        v3 = 4 * v15;
        memmove(&v2, a1 + 3 * v15, v16);
        if ( v16 == 1 )
        {
            v6 = v9 & v20;
            v7 = v9 & (v20 >> 6);
            *(unsigned char*)(v3 + v14) = v18[v9 & (v20 >> 6)];
            *(unsigned char*)(v3 + 1LL + v14) = v18[v6];
            *(unsigned char*)(v3 + 2LL + v14) = 61;
            *(unsigned char*)(v3 + 3LL + v14) = 61;
        }
        if ( v16 == 2 )
        {
            v20 = v2 >> 8;
            v5 = v9 & (v2 >> 8);
            v6 = v9 & (v2 >> 14);
            v7 = v9 & (v2 >> 20);
            *(unsigned char *)(v3 + v14) = v18[v9 & (v2 >> 20)];
            *(unsigned char *)(v3 + 1LL + v14) = v18[v6];
            *(unsigned char *)(v3 + 2LL + v14) = v18[v5];
            *(unsigned char *)(v3 + 3LL + v14) = 61;
        }
    }
    return v14;
}

bool permute(char *str, int indexes[3]) {
    const int NUM_CHARS = strlen(CHARACTER_SET);
    indexes[0]++;
    if (indexes[0] == NUM_CHARS) {
        indexes[1]++;
        indexes[0] = 0;
        // puts("overflow 0");
    }
    if (indexes[1] == NUM_CHARS) {
        indexes[2]++;
        indexes[1] = 0;
        // puts("overflow 1");
    }
    if (indexes[2] == NUM_CHARS) {
        // fputs("maxed out permutation", stderr);
        // exit(1);
        return false;
    }

    for (int i = 0; i < 3; i++) memcpy(str+i, CHARACTER_SET+indexes[i], 1);
    // puts(str);
    return true;
}

int main(int argc, char **argv) {
    char str[4] = "aaa";
    int indexes[3] = {-1,0,0};

    char *solution = malloc(1000 * sizeof(char));
    memset(solution, 0, 1000);
    char *test = malloc(1000 * sizeof(char));
    memset(test, 0, 1000);

    while (true) {
        if (!permute(str, indexes)) break;
        // puts(test);
        // puts(solution);
        // puts(" ");
        strcpy(test, solution);
        strcat(test, str);
        // puts(test);

        char *ret = unknown(test);

        if (strstr(CORRECT, ret) == CORRECT) {
            strcpy(solution, test);
            puts(solution);
            indexes[0] = -1;
            indexes[1] = 0;
            indexes[2] = 0;
        }

        free(ret);
        memset(test, 0, 1000);
    }

    indexes[0] = -1;
    indexes[1] = 0;
    indexes[2] = 0;

    while (true) {
        if (!permute(str, indexes)) break;

        strcpy(test, solution);
        strncat(test, str, 1);

        char *ret = unknown(test);

        if (strstr(CORRECT, ret) == CORRECT) {
            strcpy(solution, test);
            puts(solution);
            indexes[0] = -1;
            indexes[1] = 0;
            indexes[2] = 0;
        }

        free(ret);
        memset(test, 0, 1000);

        strcpy(test, solution);
        strncat(test, str, 2);

        ret = unknown(test);

        if (strstr(CORRECT, ret) == CORRECT) {
            strcpy(solution, test);
            puts(solution);
            indexes[0] = -1;
            indexes[1] = 0;
            indexes[2] = 0;
        }

        free(ret);
        memset(test, 0, 1000);

        strcpy(test, solution);
        strncat(test, str, 3);

        ret = unknown(test);

        if (strstr(CORRECT, ret) == CORRECT) {
            strcpy(solution, test);
            puts(solution);
            indexes[0] = -1;
            indexes[1] = 0;
            indexes[2] = 0;
        }

        free(ret);
        memset(test, 0, 1000);
    }

    return 0;
}
