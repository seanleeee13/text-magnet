del "./process.dll"
g++ -shared -o process.dll ./cpp/process.cpp -Wl,-Bstatic -lpthread -static-libgcc -static-libstdc++
pause