from disasm.header import *


def run2bin(filenameBin, filenameAsm):
    pass


def bin2asm(filenameBin, filenameEqu, filenameAsm):
    '''
    Дисассемблер
    '''
    C = CPU()
    # print(equ)
    C.SetEqu(filenameEqu)
    C.LoadHeader(filenameBin)
    C.PrintHeader()
    C.LoadCode()
    C.PrintCode()
#     C.LoadConstant()
#     C.PrintConstats()
#     
#     # Code
#     adr_load = Datas[(0x08, 0x10)]
#     file.seek(Datas[(0x68, 0x10)])
#     for adr in range(Datas[(0x68, 0x10)], Datas[(0x68, 0x10)] + Datas[(0x78, 0x10)], 4):
#         data = file.read(4)
#         if data is None:
#             break
#         code = int.from_bytes(data, 'big')
#         C.NewCode(adr_load, code)
#         cmd = C.CodeToAsm()    
#         CodeStr = f'{code:08X}'
#         CodeStr = CodeStr[:2] + '.' + CodeStr[2:4] + '.' + CodeStr[4:6] + '.' + CodeStr[6:]
#         print(f'{adr:04X} :  {adr_load:04X} :{CodeStr:11s}  {cmd}')
#         adr_load += 4
# 
#     # Constants
#     file.seek(Datas[(0x28, 0x10)])
#     for adr in range(Datas[(0x28, 0x10)], Datas[(0x28, 0x10)] + Datas[(0x38, 0x10)], 16):
#         data = file.read(16)
#         if data is None:
#             break
#         print(f'{adr:04X} :', end='')
#         for CodeStr in data:
#             print(f' {CodeStr:02X}', end='')
#         print()


def dump2bin(filenameDump, filenameBin):
    '''
    Конвертер dump файлов в bin
    '''
    with open (filenameDump, "r") as myfile:
        data = myfile.readlines()
    
    bytes = bytearray()
    for s in data:
        hexs = s.split()
        for hex in hexs[1:]:
            bytes.append(int(hex, 16))
            
    with open (filenameBin, "wb") as myfile:
        myfile.write(bytes)
