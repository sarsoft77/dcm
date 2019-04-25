from ctypes import *
from disasm.dump2bin import *

if __name__ == '__main__':
    test=r'../../test'
    test += '//' 
    dump2bin(test+'kurs2.dump',test+'kurs2.bin')
    bin2asm(test+'kurs2.bin', test+'kurs2.equ', test+'kurs2.asm')
