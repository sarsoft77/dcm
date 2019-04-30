from disasm.asm import *
# from disasm.templates import *


def ReplaceWords(s, words):
    for k, v in words.items():
        s = s.replace(k, v)
    return s      


class Memory:
    '''
    Память
    '''

    def __init__(self):
        self.Data = None
        
    def __iter__(self):
        self.index = -1
        return(self)

    def __next__(self):
        self.index += 1
        if self.index >= len(self.Data):
            raise StopIteration
        offset = self.index * self.NumBytes
        offset_file = self.OffsetAddr + offset
        ip = self.BeginAddr + offset
        return(offset_file, ip, self.Data[self.index])

    def __getitem__(self, index):
        result = self.Data[index]
        return(result)
    
    def LoadFromFile(self, FilenameBin, OffsetAddr, Size, NumBytes, BeginAddr, ByteOrder='big'):
        '''
        Чтение из файла по ячеки памяти по NumBytes
        
        :param FilenameBin: имя файла
        :param OffsetAddr: начальный адрес области в файле
        :param Size: размер области
        :param NumBytes: длина в байтах одного значения
        :param BeginAddr: адрес в памяти
        :param ByteOrder: порядок следования байтов
        '''
        self.FilenameBin = FilenameBin
        self.OffsetAddr = OffsetAddr
        self.Size = Size
        self.ByteOrder = ByteOrder
        self.BeginAddr = BeginAddr
        self.NumBytes = NumBytes
        with open(FilenameBin, 'rb') as file:
            file.seek(self.OffsetAddr)
            
            self.Data = list()
            for i in range(Size // NumBytes):
                self.Data.append(int.from_bytes(file.read(NumBytes), ByteOrder))
            # Если есть еще данные меньшие NumBytes, то их тоже скачиваем 
            if Size % NumBytes: 
                # сдвигаем влево на NumBytes-Size % NumBytes 
                self.Data.append(int.from_bytes(file.read(NumBytes), ByteOrder) << 8 * (NumBytes - Size % NumBytes))


class CPU(Asm):
    '''
    Процессор
    '''
    adr = 0  # 128 бит  адрес
    code = 0  # 32  бит  команда    
    T = 0  # 2   бита тип команды
    OP = 0  # 10  бит  код операции
    DD = 0  # 20  бит  данных
    # имя шаблона, название команды на ассемблере, строка шаблона
    NameT = CmdAsm = StrT = ''
    equ = None

    FileNameBin = None
    HeaderSize = 0x88
    HeaderData = None
    
    ValueData = None
        
    Header = (
        filetype,
        begin_addr,
        ram_size,
        constants_offset,
        constants_size,
        variable_offset,
        variable_size,
        code_offset,
        code_size) = {
        (0x0, 0x8):'Тип файла 0x00cc383231d0d3cc',  # size_t             file_type=0x00cc383231d0d3cc   
        (0x08, 0x10):'Адрес загрузки LA',  # unsigned __int128  begin_addr_, 
        (0x18, 0x10):'Объем памяти нужный для выполнения, отсчитывается от LA',  # unsigned __int128  ram_size_,           
        (0x28, 0x10):'Смещение раздела констант от начала файла',  # unsigned __int128  entry_offset_,       
        (0x38, 0x10):'Объем раздела констант',  # unsigned __int128  volume_constants_,   
        (0x48, 0x10):'Смещение раздела переменных',  # unsigned __int128  variable_offset_,    
        (0x58, 0x10):'Объем раздела переменных',  # unsigned __int128  variable_size_,      
        (0x68, 0x10):'Смещение раздела кода',  # unsigned __int128  code_offset_,        
        (0x78, 0x10):'Объем раздела кода'  # unsigned __int128  size_code_,          
        }
    
    def __init__(self):
        pass

    def LoadBin(self, size, start=0):
        with open(self.FileNameBin, 'rb') as file:
            if not start:
                file.seek(start)
            self.FileData = file.read(size)

    def LoadHeader(self, filenameBin):
        '''
        Загрузка шапки файла с бинарным кодом    
        '''
        self.FileNameBin = filenameBin
        self.LoadBin(self.HeaderSize)
        self.HeaderData = dict()
        for adr in self.Header: 
            self.HeaderData[adr] = int.from_bytes(self.FileData[adr[0]:adr[0] + adr[1]], 'big' if adr[2:3] == ('b',) else 'little')
                
    def PrintHeader(self):
        '''
        Вывод шапки файла    
        '''
        for adr, val in self.HeaderData.items():
            print(f'{adr[0]:04X} : {val:019_X}  # {self.Header[adr]}')
            
    def LoadCode(self):
        '''
        Загрузка кода из файла, согласно шапки файла    
        '''
        self.CodeData = Memory()
        self.CodeData.LoadFromFile(self.FileNameBin, self.HeaderData[self.code_offset], self.HeaderData[self.code_size], 4, self.HeaderData[self.begin_addr]) 

    def CodeToAsm(self, adr, code):
        '''
        Разбор структуры кода,
        определение типа команды, кода операции, название команды
        имени шаблона, команды ассемблера    
        '''
        self.adr = adr
        self.code = code
        self.T, self.OP, self.DD = self.SplitBits(self.code, (2, 12, 32)).split(' ')
        self.T=int(self.T,2)
        self.OP=int(self.OP,2)
        self.DD=int(self.DD,2)
#         self.T = self.code >> 30  # 2 бита тип команды
#         self.OP = ((self.code >> 20) & 0x3FF)  # 10 бит код операции
#         self.DD = self.code & 0xFFFFF  # 20 бит данных
        # имя шаблона, название команды на ассемблере, строка шаблона 
        self.NameT, self.CmdAsm, self.StrT = self.OpToAsm[self.T][self.OP]
        ArgAsm = self.DecodeTemplate()
#         ArgAsm = self.Template[self.NameT](self.DD)
        ArgAsmRepl = ReplaceWords(ArgAsm, self.equ)
        return(f'{self.CmdAsm:6s} {ArgAsm:23s} # {ArgAsmRepl:23s}   # {self.T:02b} {self.OP:010b} {self.NameT:1s} {self.SplitBits(self.DD,self.Template[self.NameT]):25s}')

    def PrintCode(self):
        '''
        Вывод на печать кода из памяти    
        '''
        for offset_file, ip, code in self.CodeData:
            cmd = self.CodeToAsm(ip, code)
            CodeStr = self.SplitBits(code, (2, 4, 6, 8), '.', 'X')    
            print(f'{offset_file:04X}: {ip:04X}:{CodeStr:11s} {cmd}')

    def LoadConstants(self):
        '''
        Выделяем память под область констант сразу после области кода 
        '''
        self.ConstantsData = Memory()
        self.ConstantsData.LoadFromFile(self.FileNameBin, self.HeaderData[self.constants_offset], self.HeaderData[self.constants_size], 16, self.HeaderData[self.begin_addr] + self.HeaderData[self.code_size]) 

    def PrintConstants(self):
        '''
        Вывод на печать кода из памяти    
        '''
        for offset, addr, code in self.ConstantsData:
            CodeStr = self.SplitBits(code, range(2, 34, 2), '.', 'X')
            # cmd = ''.join([chr(int(b, 16)) for b in CodeStr.split('.')])
            print(f'{offset:04X} :  {addr:04X} :{CodeStr:32s}')

    def SetEqu(self, filenameEqu):
        '''
        Формирует словарь из файла определений    
        '''
        self.equ = dict()
        with open(filenameEqu, 'r') as file:
            for s in file:
                e = s.split()
                if (len(e) == 3) and (e[1].lower() == 'equ'):
                    self.equ[e[2]] = e[0]

    def SplitBits(self, d, t, s=' ', base='b'):
        '''
        Побайтная разбивка b по t c разделителем s
        
        :param d: число которое нужно разложить
        :param t: кортеж с разбивкой, последний элемент в котором общая длина
        :param s: разделитель
        :param base: b - бинарный, x - шестнадцатиричный 
        '''
        b = f'{d:0{t[-1]}{base}}'    
        if len(t):
            result = b[:t[0]]
            for p1, p2 in zip(t[:-1], t[1:]):
                result += s + b[p1:p2]
            return(result)
        else:
            return(b)
        
    def u2i(self, unsigned, numbits):
        '''
        Перевод беззнакового числа в целое для заданного количества бит 
        '''
        if (unsigned >> (numbits - 1)):
            return(unsigned - (1 << numbits))
        else:
            return(unsigned)

    def n2n (self, x, numbits1, numbits2, fill=0):
        '''
        Расширение разрядности слева нулем fill=0 или 
        '''
        if fill:
            return(x)
        else:    
            return(x)

    def DecodeTemplate(self):
        if self.NameT == 'A':
            imm = self.DD & 0xFFFFF
            imm = f'{imm:#07x}'
            imm20 = self.DD & 0xFFFFF
            imm20 = self.u2i(imm20, 20)
            imm20 = f'${imm20:+#07x} ({self.adr+4*imm20:#06x})'
            imm10 = self.DD & 0x3FF
            imm10 = f'{imm10:#x}'
        elif self.NameT == 'B':
            r = (self.DD >> 15) & 0x1F
            reg = f'{r:d}'
        elif self.NameT == 'C':
            r = (self.DD >> 15) & 0x1F
            reg = f'{r:d}'
            imm15 = self.DD & 0x7FFF
            if (self.T == 0b10):
                imm15 = self.u2i(imm15, 15)
                imm15 = f'${imm15:+#07x} ({self.adr+4*imm15:#06x})'
            else:
                # Расширим до 128 битов    
                imm15 = f'{imm15:#x}'
        elif self.NameT == 'D':
            # 5-5-0
            r1 = (self.DD >> 15) & 0x1F
            reg1 = f'{r1:d}'
            r2 = (self.DD >> 10) & 0x1F
            reg2 = f'{r2:d}'
        elif self.NameT == 'E':
            r1 = (self.DD >> 15) & 0x1F
            reg1 = f'{r1:d}'
            r2 = (self.DD >> 10) & 0x1F
            reg2 = f'{r2:d}'
            imm = self.DD & 0x3FF
            imm10 = f'{imm:#05X}'
        elif self.NameT == 'F':
            r1 = (self.DD >> 15) & 0x1F
            reg1 = f'{r1:d}'
            r2 = (self.DD >> 10) & 0x1F
            reg2 = f'{r2:d}'
            r3 = (self.DD >> 5) & 0x1F
            reg3 = f'{r3:d}'
        elif self.NameT == 'G':
            r1 = (self.DD >> 15) & 0x1F
            reg1 = f'{r1:d}'
            r2 = (self.DD >> 10) & 0x1F
            reg2 = f'{r2:d}'
            r3 = (self.DD >> 5) & 0x1F
            reg3 = f'{r3:d}'
            r4 = self.DD & 0x1F
            reg4 = f'{r4:d}'
        elif self.NameT == 'M':
            r = (self.DD >> 15) & 0x1F
            reg = f'{r:d}'
            B = (self.DD >> 10) & 0x1F
            # f'{NameR}{b:d}'
            ix = (self.DD >> 5) & 0x1F
            # f'{NameR}{r3:d}'
            sf = (self.DD >> 2) & 0x7
            # f'{NameR}{r3:d}'
            adress = B + ix * self.SF[sf]
            mem32 = f'{adress:#06X}'
            mem64 = f'{adress:#06X}'
            mem80 = f'{adress:#06X}'
            mem128 = f'{adress:#06X}'
        elif self.NameT == 'H':
            pass
        
        try:
            s = eval('f\'' + self.StrT + '\'')
        except Exception:
            s = '!!! (' + self.StrT + ') !!!'
            print(s)
        return (s)
        
# Stru = {
#     (0x0, 0x8):'МУР128М',                                                   # size_t             file_type=0x00cc383231d0d3cc   
#     (0x08, 0x10):'Адрес загрузки LA',                                       # unsigned __int128  begin_addr_, 
#     (0x18, 0x10):'Объем памяти нужный для выполнения, отсчитывается от LA', # unsigned __int128  ram_size_,           
#     (0x28, 0x10):'Смещение раздела констант от начала файла',               # unsigned __int128  entry_offset_,       
#     (0x38, 0x10):'Объем раздела констант',                                  # unsigned __int128  volume_constants_,   
#     (0x48, 0x10):'Смещение раздела переменных',                             # unsigned __int128  variable_offset_,    
#     (0x58, 0x10):'Объем раздела переменных',                                # unsigned __int128  variable_size_,      
#     (0x68, 0x10):'Смещение раздела кода',                                   # unsigned __int128  code_offset_,        
#     (0x78, 0x10):'Объем раздела кода',                                      # unsigned __int128  size_code_,          
#     (0x88, 0x10):'Начальное значение стека'                                 # unsigned __int128  initial_stack_value_,
#     }
