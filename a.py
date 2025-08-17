from ctypes import CDLL

c_test = CDLL('./test.dll')
c_test.hello()
a = c_test.get()
print(a)