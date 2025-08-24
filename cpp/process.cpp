#include <iostream>

using namespace std;

extern "C" __declspec(dllexport) void hello() {
    cout << "Hello C++!\n";
}

extern "C" __declspec(dllexport) const char* get() {
    return "Hello Python!";
}