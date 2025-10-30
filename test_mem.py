from ctypes import CDLL
import os

process = CDLL(os.path.join(os.getcwd(), "process.dll"))
a = process.hello()
print(a)
print(type(a))