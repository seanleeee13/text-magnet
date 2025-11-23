cd ..
cd text-magnet
del "./process.pyd"
g++ -O3 -shared -std=c++17 -fPIC cpp/process.cpp -o process.pyd -I C:/Users/seanl/AppData/Local/Python/pythoncore-3.12-64/Include -I C:/Users/seanl/AppData/Local/Python/pythoncore-3.12-64/Lib/site-packages/pybind11/include -L C:/Users/seanl/AppData/Local/Python/pythoncore-3.12-64/libs -l python312 -I ./data
pause