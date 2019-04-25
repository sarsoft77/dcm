from disasm.header import *

def ReplaceWords(s, words):
    for k, v in words.items():
        s = s.replace(k, v)
    return s      


def run2bin(filenameBin, filenameAsm):
    pass

def bin2asm(filenameBin, filenameEqu, filenameAsm):

    global equ;
    equ = dict()
    with open(filenameEqu, 'r') as file:
        for str in file:
            e = str.split()
            if (len(e) == 3) and (e[1].lower() == 'equ'):
                equ[e[2]] = e[0]
    
    #print(equ)
    
    Datas = dict()
    with open(filenameBin, 'rb') as file:
        data = file.read(0x88)
        
        for adr in Stru: 
            Datas[adr] = int.from_bytes(data[adr[0]:adr[0] + adr[1]], 'big' if adr[2:3] == ('b',) else 'little')
        for adr, val in Datas.items():
            print(f'{adr[0]:04X} : {val:019_X}  # {Stru[adr]}')
            
        # Code
        adr_load = Datas[(0x08, 0x10)]
        file.seek(Datas[(0x68, 0x10)])
        for adr in range(Datas[(0x68, 0x10)], Datas[(0x68, 0x10)] + Datas[(0x78, 0x10)], 4):
            data = file.read(4)
            if data is None:
                break
            code = int.from_bytes(data, 'big')
            cmd = code2cmd(adr_load, code)
            CodeStr = f'{code:08X}'
            CodeStr = CodeStr[:2] + '.' + CodeStr[2:4] + '.' + CodeStr[4:6] + '.' + CodeStr[6:]
            print(f'{adr:04X} :  {adr_load:04X} :{CodeStr:11s}  {cmd}')
            adr_load += 4

        # Constants
        file.seek(Datas[(0x28, 0x10)])
        for adr in range(Datas[(0x28, 0x10)], Datas[(0x28, 0x10)] + Datas[(0x38, 0x10)], 16):
            data = file.read(16)
            if data is None:
                break
            print(f'{adr:04X} :', end='')
            for CodeStr in data:
                print(f' {CodeStr:02X}', end='')
            print()
                

def code2cmd(adr, code):
    T = code >> 30  # 2 бита тип команды
    OP = ((code >> 20) & 0x3FF)  # 10 бит код операции
    DD = code & 0xFFFFF  # 20 бит данных
    NameT = table_op[T][OP][0]  # имя шаблона
    StrT = table_op[T][OP][2]  # строка шаблона
    CmdAsm = table_op[T][OP][1]  # название команды на ассемблере
    StrByte, ArgAsm = DecodeTemplate(adr, T, NameT, StrT, DD)
    ArgAsmRepl = ReplaceWords(ArgAsm, equ)
    try:  
        sOut = f'{CmdAsm:6s} {ArgAsm:20s} # {ArgAsmRepl:20s}   # {T:02b} {OP:010b} {NameT:1s} {StrByte:25s}'
    except Exception:
        sOut = f'!!! {CmdAsm:6s} ' + ArgAsm + f' # {T:02b} {OP:010b} {NameT:1s} {StrByte:25s}'    
    return(sOut)

        
def DecodeTemplate(adr, T, NameT, StrT, code):
    b = f'{code:020b}'    
    if NameT == 'A':
        # 20
        b = b[:4] + ' ' + b[4:8] + ' ' + b[8:12] + ' ' + b[12:16] + ' ' + b[16:]
        imm = code & 0xFFFFF
        imm = f'0x{imm:05X}'
        imm20 = code & 0xFFFFF
        imm20 = (imm20 - (1 << 20)) if (imm20 >> 19) else imm20
        imm20 = ('$+' if imm20 >= 0 else '$') + f'{hex(imm20)} (0x{adr+4*imm20:04X})'
        imm10 = code & 0x3FF
        imm10 = f'0x{imm10:X}'
    elif NameT == 'B':
        # 5-0
        b = b[:5] + ' ' + b[5:] 
        r = (code >> 15) & 0x1F
        reg = f'{r:d}'
    elif NameT == 'C':
        # 5-15
        b = b[:5] + ' ' + b[5:8] + ' ' + b[8:12] + ' ' + b[12:16] + ' ' + b[16:]
        r = (code >> 15) & 0x1F
        reg = f'{r:d}'
        imm15 = code & 0x7FFF
        if (T == 0b10):
            imm15 = (imm15 - (1 << 15)) if (imm15 >> 14) else imm15
            imm15 = ('$+' if imm15 >= 0 else '$') + f'{hex(imm15)} (0x{adr+4*imm15:04X})'
        else:
            # Расширим до 128 битов    
            imm15 = f'0x{imm15:0X}'
    elif NameT == 'D':
        # 5-5-0
        b = b[:5] + ' ' + b[5:10] + ' ' + b[10:]
        r1 = (code >> 15) & 0x1F
        reg1 = f'{r1:d}'
        r2 = (code >> 10) & 0x1F
        reg2 = f'{r2:d}'
    elif NameT == 'E':
        b = b[:5] + ' ' + b[5:10] + ' ' + b[10:12] + ' ' + b[12:16] + ' ' + b[16:]
        r1 = (code >> 15) & 0x1F
        reg1 = f'{r1:d}'
        r2 = (code >> 10) & 0x1F
        reg2 = f'{r2:d}'
        imm = code & 0x3FF
        imm10 = f'0x{imm:03X}'
    elif NameT == 'F':
        b = b[:5] + ' ' + b[5:10] + ' ' + b[10:15] + ' ' + b[15:]
        r1 = (code >> 15) & 0x1F
        reg1 = f'{r1:d}'
        r2 = (code >> 10) & 0x1F
        reg2 = f'{r2:d}'
        r3 = (code >> 5) & 0x1F
        reg3 = f'{r3:d}'
    elif NameT == 'G':
        b = b[:5] + ' ' + b[5:10] + ' ' + b[10:15] + ' ' + b[15:]
        r1 = (code >> 15) & 0x1F
        reg1 = f'{r1:d}'
        r2 = (code >> 10) & 0x1F
        reg2 = f'{r2:d}'
        r3 = (code >> 5) & 0x1F
        reg3 = f'{r3:d}'
        r4 = code & 0x1F
        reg4 = f'{r4:d}'
    elif NameT == 'M':
        b = b[:5] + ' ' + b[5:10] + ' ' + b[10:15] + ' ' + b[15:19] + ' ' + b[19:]
        r = (code >> 15) & 0x1F
        reg = f'{r:d}'
        B = (code >> 10) & 0x1F
        # f'{NameR}{b:d}'
        ix = (code >> 5) & 0x1F
        # f'{NameR}{r3:d}'
        sf = (code >> 2) & 0x7
        # f'{NameR}{r3:d}'
        adress = B + ix * SF[sf]
        mem32 = f'0x{adress:04X}'
        mem64 = f'0x{adress:04X}'
        mem80 = f'0x{adress:04X}'
        mem128 = f'0x{adress:04X}'
    elif NameT == 'H':
        pass
    
    try:
        s = eval('f\'' + StrT + '\'')
    except Exception:
        s = '!!! (' + StrT + ') !!!'
        print(s)
    return (b, s)


def dump2bin(filenameDump, filenameBin):
    with open (filenameDump, "r") as myfile:
        data = myfile.readlines()
    
    bytes = bytearray()
    for s in data:
        hexs = s.split()
        for hex in hexs[1:]:
            bytes.append(int(hex, 16))
            
    with open (filenameBin, "wb") as myfile:
        myfile.write(bytes)
