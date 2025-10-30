#include <iostream>
#include <vector>

using namespace std;

int a[121][6];

extern "C" __declspec(dllexport) void calculate(char *p) {
    
}

extern "C" __declspec(dllexport) int get(int x, int y) {
    return a[x][y];
}