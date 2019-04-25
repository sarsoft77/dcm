def ReplaceWords(s, words):
    for k, v in words.items():
        s = s.replace(k, v)
    return s      


Stru = {
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


class CPU:
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

    SF = (1, 2, 4, 8, 16, 10)

    # Шаблоны
    # разбивка на группы бит 
    Template = {
        'A':(4, 8, 12, 16),
        'B':(5,),
        'C':(5, 8, 12, 16),
        'D':(5, 10),
        'E':(5, 10, 12, 16),
        'F':(5, 10, 15),
        'G':(5, 10, 15),
        'M':(5, 10, 19),
        'H':()
    } 
    
    Template2 = {
        }

    OpToAsm = (
    # Т=00       
        (('F', 'addi', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000000000:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'addi', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000000001:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'subi', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000000010:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'subi', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000000011:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'muliu', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000000100:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'muliu', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000000101:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'mulis', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000000110:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'mulis', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000000111:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'diviu', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000001000:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'diviu', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000001001:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'divis', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000001010:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'divis', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000001011:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'modiu', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000001100:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'modiu', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000001101:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'modis', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000001110:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'modis', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000001111:{reg1}:{reg2}:{imm10} шаблон E 
        ('G', 'divmodiu', 'r{reg1}, r{reg2}, r{reg3}, r{reg4}'),  # 00:0000010000:{reg1}:{reg2}:{reg3}:{reg4} шаблон G 
        ('G', 'divmodis', 'r{reg1}, r{reg2}, r{reg3}, r{reg4}'),  # 00:0000010001:{reg1}:{reg2}:{reg3}:{reg4} шаблон G 
        ('F', 'cmpiu', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000010010:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'cmpiu', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000010011:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'cmpis', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000010100:{reg1}:{reg2}:{reg3}:00000 шаблон F 
        ('E', 'cmpis', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000010101:{reg1}:{reg2}:{imm10} шаблон E 
        ('F', 'and', 'r{reg1}, r{reg2},r{reg3}'),  # 00:0000010110:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'and', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000010111:{reg1}:{reg2}:{imm10} шаблон E
        ('F', 'or', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000011000:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'or', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000011001:{reg1}:{reg2}:{imm10} шаблон E
        ('F', 'xor', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000011010:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'xor', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000011011:{reg1}:{reg2}:{imm10} шаблон E
        ('F', 'andn', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000011100:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'andn', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000011101:{reg1}:{reg2}:{imm10} шаблон E
        ('F', 'orn', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000011110:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'orn', 'r{reg1}, r{reg2}, {imm10}'),  #  00:0000011111:{reg1}:{reg2}:{imm10} шаблон E
        ('F', 'xorn', 'r{reg1}, r{reg2}, r{reg3}'),  #  00:0000100000:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'xorn', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000100001:{reg1}:{reg2}:{imm10} шаблон E
        ('E', 'lshift', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000100010:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'lshift', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000100011:{reg1}:{reg2}:{imm10} шаблон E
        ('E', 'rshift', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000100100:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'rshift', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000100101:{reg1}:{reg2}:{imm10} шаблон E
        ('E', 'rshifts', 'r{reg1}, r{reg2}, r{reg3}'),  # 00:0000100110:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('E', 'rshifts', 'r{reg1}, r{reg2}, {imm10}'),  # 00:0000100111:{reg1}:{reg2}:{imm10} шаблон E
        ('D', 'not', 'r{reg1}, r{reg2}'),  # 00:0000101000:{reg1}:{reg2}:0000000000 шаблон D
        ('C', 'not', 'r{reg}, {imm15}')),  # 00:0000101001:{reg}:imm15  шаблон C
    # Т=01       
        (('F', 'addf', 'f{reg1}, f{reg2}, f{reg3}'),  # 01:0000000000:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('F', 'subf', 'f{reg1}, f{reg2}, f{reg3}'),  # 01:0000000001:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('F', 'mulf', 'f{reg1}, f{reg2}, f{reg3}'),  # 01:0000000010:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('F', 'divf', 'f{reg1}, f{reg2}, f{reg3}'),  # 01:0000000011:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('F', 'cmpf', 'r{reg1}, f{reg2}, f{reg3}'),  # 01:0000000100:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('F', 'roundn', 'r{reg1}, f{reg2}'),  # 01:0000000101:{reg1}:{reg2}:0000000000 шаблон D
        ('F', 'roundl', 'r{reg1}, f{reg2}'),  # 01:0000000110:{reg1}:{reg2}:0000000000 шаблон D
        ('F', 'roundg', 'r{reg1}, f{reg2}'),  # 01:0000000111:{reg1}:{reg2}:0000000000 шаблон D
        ('F', 'roundt', 'r{reg1}, f{reg2}'),  # 01:0000001000:{reg1}:{reg2}:0000000000 шаблон D
        ('F', 'frac', 'f{reg1}, f{reg2}'),  # 01:0000001001:{reg1}:{reg2}:0000000000 шаблон D
        ('F', 'absf', 'f{reg1}, f{reg2}'),  # 01:0000001010:{reg1}:{reg2}:0000000000 шаблон D
        ('F', 'mul2f', 'f{reg1}, f{reg2}, r{reg3}'),  # 01:0000001011:{reg1}:{reg2}:{reg3}:00000 шаблон F
        ('F', 'mul2f', 'f{reg1}, f{reg2}, {imm10}', 'z'),  # 01:0000001011:{reg1}:{reg2}:{imm10}:00000 шаблон E
        ('F', 'chsf', 'f{reg1}, f{reg2}')),  # 01:0000000101:{reg1}:{reg2}:0000000000 шаблон D
    # Т=10       
        (('B', 'jmp', 'r{reg}'),  # 10:0000000000:{reg}:000000000000000 шаблон B
        ('D', 'jmps', 'r{reg1}, r{reg2}'),  # 10:0000000001:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpz', 'r{reg1}, r{reg2}'),  # 10:0000000010:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpp', 'r{reg1}, r{reg2}'),  # 10:0000000011:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpnz', 'r{reg1}, r{reg2}'),  # 10:0000000100:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpge', 'r{reg1}, r{reg2}'),  # 10:0000000101:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmple', 'r{reg1}, r{reg2}'),  # 10:0000000110:{reg1}:{reg2}:0000000000 шаблон D
        ('B', 'jmpr', 'r{reg1}'),  # 10:0000000111:{reg}:000000000000000 шаблон B
        ('D', 'jmpsr', 'r{reg1}, r{reg2}'),  # 10:0000001000:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpzr', 'r{reg1}, r{reg2}'),  # 10:0000001001:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmppr', 'r{reg1}, r{reg2}'),  # 10:0000001010:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpnzr', 'r{reg1}, r{reg2}'),  # 10:0000001011:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpger', 'r{reg1}, r{reg2}'),  # 10:0000001100:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'jmpler', 'r{reg1}, r{reg2}'),  # 10:0000001101:{reg1}:{reg2}:0000000000 шаблон D
        ('A', 'jmpr', '{imm20}'),  # 10:0000001110:{imm20} шаблон A
        ('C', 'jmpsr', 'r{reg}, {imm15}'),  # 10:0000001111:{reg}:{imm15}  шаблон C
        ('C', 'jmpzr', 'r{reg}, {imm15}'),  # 10:0000010000:{reg}:{imm15}  шаблон C
        ('C', 'jmppr', 'r{reg}, {imm15}'),  # 10:0000010001:{reg}:{imm15}  шаблон C
        ('C', 'jmpnzr', 'r{reg}, {imm15}'),  # 10:0000010010:{reg}:{imm15}  шаблон C
        ('C', 'jmpger', 'r{reg}, {imm15}'),  # 10:0000010011:{reg}:{imm15}  шаблон C
        ('C', 'jmpler', 'r{reg}, {imm15}'),  # 10:0000010100:{reg}:{imm15}  шаблон C
        ('B', 'call', 'r{reg}'),  # 10:0000010101:{reg}:000000000000000 шаблон B
        ('D', 'calls', 'r{reg1}, r{reg2}'),  # 10:0000010110:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callz', 'r{reg1}, r{reg2}'),  # 10:0000010111:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callp', 'r{reg1}, r{reg2}'),  # 10:0000011000:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callnz', 'r{reg1}, r{reg2}'),  # 10:0000011001:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callge', 'r{reg1}, r{reg2}'),  # 10:0000011010:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callle', 'r{reg1}, r{reg2}'),  # 10:0000011011:{reg1}:{reg2}:0000000000 шаблон D
        ('B', 'callr', 'r{reg1}'),  # 10:0000011100:{reg}:000000000000000 шаблон B
        ('D', 'callsr', 'r{reg1}, r{reg2}'),  # 10:0000011101:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callzr', 'r{reg1}, r{reg2}'),  # 10:0000011110:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callpr', 'r{reg1}, r{reg2}'),  # 10:0000011111:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callnzr', 'r{reg1}, r{reg2}'),  # 10:0000100000:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'callger', 'r{reg1}, r{reg2}'),  # 10:0000100001:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'calller', 'r{reg1}, r{reg2}'),  # 10:0000100010:{reg1}:{reg2}:0000000000 шаблон D
        ('A', 'callr', '{imm20}'),  # 10:0000100011:{imm20} шаблон A
        ('C', 'callsr', 'r{reg}, {imm15}'),  # 10:0000100100:{reg}:{imm15}  шаблон C
        ('C', 'callzr', 'r{reg}, {imm15}'),  # 10:0000100101:{reg}:{imm15}  шаблон C
        ('C', 'callpr', 'r{reg}, {imm15}'),  # 10:0000100110:{reg}:{imm15}  шаблон C
        ('C', 'callnzr', 'r{reg}, {imm15}'),  # 10:0000100111:{reg}:{imm15}  шаблон C
        ('C', 'callger', 'r{reg}, {imm15}'),  # 10:0000101000:{reg}:{imm15}  шаблон C
        ('C', 'calller', 'r{reg}, {imm15}'),  # 10:0000101001:{reg}:imm15  шаблон C
        ('H', 'ret', ''),  # 10:0000101010:00000000000000000000 шаблон H
        ('B', 'rets', 'r{reg}'),  # 10:0000101011:{reg}:000000000000000 шаблон B
        ('B', 'retz', 'r{reg}'),  # 10:0000101100:{reg}:000000000000000 шаблон B
        ('B', 'retp', 'r{reg}'),  # 10:0000101101:{reg}:000000000000000 шаблон B
        ('B', 'retnz', 'r{reg}'),  # 10:0000101110:{reg}:000000000000000 шаблон B
        ('B', 'retge', 'r{reg}'),  # 10:0000101111:{reg}:000000000000000 шаблон B
        ('B', 'retle', 'r{reg}'),  # 10:0000110000:{reg}:000000000000000 шаблон B
        ('B', 'reta', 'r{reg}'),  # 10:0000110001:{reg}:000000000000000 шаблон B
        ('D', 'retasr', 'r{reg1}, r{reg2}'),  # 10:0000110010:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'retazr', 'r{reg1}, r{reg2}'),  # 10:0000110011:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'retapr', 'r{reg1}, r{reg2}'),  # 10:0000110100:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'retanzr', 'r{reg1}, r{reg2}'),  # 10:0000110101:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'retager', 'r{reg1}, r{reg2}'),  # 10:0000110110:{reg1}:{reg2}:0000000000 шаблон D
        ('D', 'retaler', 'r{reg1}, r{reg2}'),  # 10:0000110111:{reg1}:{reg2}:0000000000 шаблон D
        ('A', 'reta', '{imm20}'),  # 10:0000111000:{imm20} шаблон A
        ('C', 'retasr', 'r{reg}, {imm15}'),  # 10:0000111001:{reg}:{imm15}  шаблон C
        ('C', 'retazr', 'r{reg}, {imm15}'),  # 10:0000111010:{reg}:{imm15}  шаблон C
        ('C', 'retapr', 'r{reg}, {imm15}'),  # 10:0000111011:{reg}:{imm15}  шаблон C
        ('C', 'retanzr', 'r{reg}, {imm15}'),  # 10:0000111100:{reg}:{imm15}  шаблон C
        ('C', 'retager', 'r{reg}, {imm15}'),  # 10:0000111101:{reg}:{imm15}  шаблон C
        ('C', 'retaler', 'r{reg}, {imm15}'),  # 10:0000111110:{reg}:{imm15}  шаблон C
        ('B', 'trap', 'r{reg}'),  # 10:0000111111:{reg}:000000000000000 шаблон B
        ('A', 'trap', '{imm10}'),  # 10:0001000000:0000000000{imm10} шаблон A
        ('H', 'reti', '')),  # 10:0001000001:00000000000000000000 шаблон H
    # Т=11       
        (('D', 'mov', 'r{reg1}, r{reg2}'),  # 11:0000000000:{reg1}:{reg2}:0000000000 шаблон D
        ('C', 'movu', 'r{reg}, {imm15}'),  # 11:0000000001:{reg}:imm15  шаблон C 
        ('C', 'movs', 'r{reg}, {imm15}'),  # 11:0000000010:{reg}:imm15  шаблон C 
        ('M', 'mov', 'r{reg}, [{mem128}]'),  # 11:0000000011:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov8u', 'r{reg}, [{mem8}]'),  # 11:0000000100:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov16u', 'r{reg}, [{mem16}]'),  # 11:0000000101:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov32u', 'r{reg}, [{mem32}]'),  # 11:0000000110:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov64u', 'r{reg}, [{mem64}]'),  # 11:0000000111:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov8s', 'r{reg}, [{mem8}]'),  # 11:0000001000:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov16u', 'r{reg}, [{mem16}]'),  # 11:0000001001:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov32u', 'r{reg}, [{mem32}]'),  # 11:0000001010:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov64u', 'r{reg}, [{mem64}]'),  # 11:0000001011:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov', '[{mem128}],r{reg}'),  # 11:0000001100:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov8', '[{mem8}],r{reg}'),  # 11:0000001101:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov16', '[{mem16}],r{reg}'),  # 11:0000001110:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov32', '[{mem32}],r{reg}'),  # 11:0000001111:{reg}:B:IX:SF:00 шаблон M 
        ('M', 'mov64', '[{mem64}],r{reg}'),  # 11:0000010000:{reg}:B:IX:SF:00 шаблон M 
        ('D', 'push', 'r{reg1}-r{reg2}'),  # 11:0000010001:r$i$:r$j$:0000000000 шаблон D
        ('D', 'pop', 'r{reg1}-r{reg2}'),  # 11:0000010010:r$i$:r$j$:0000000000 шаблон D
        ('D', 'mov', 'f{reg1}, f{reg2}'),  # 11:0000010011:{reg1}:{reg2}:0000000000 шаблон D
        ('M', 'mov', 'f{reg}, [{mem128}]'),  # 11:0000010100:{reg}:B:IX:SF:00 шаблон M
        ('M', 'mov32f', 'f{reg}, [{mem32}]'),  # 11:0000010101:{reg}:B:IX:SF:00 шаблон M
        ('M', 'mov64f', 'f{reg}, [{mem64}]'),  # 11:0000010110:{reg}:B:IX:SF:00 шаблон M
        ('M', 'mov80f', 'f{reg}, [{mem80}]'),  # 11:0000010111:{reg}:B:IX:SF:00 шаблон M
        ('M', 'mov32f', '[{mem32}], f{reg}'),  # 11:0000011000:{reg}:B:IX:SF:00 шаблон M
        ('M', 'mov64f', '[{mem64}], f{reg}'),  # 11:0000011001:{reg}:B:IX:SF:00 шаблон M
        ('M', 'mov80f', '[{mem64}], f{reg}'),  # 11:0000011010:{reg}:B:IX:SF:00 шаблон M
        ('D', 'push', 'f{reg1}-f{reg2}'),  # 11:0000011011:f$i$:f$j$:0000000000 шаблон D
        ('D', 'pop', 'f{reg1}-f{reg2}'),  # 11:0000011100:f$i$:f$j$:0000000000 шаблон D
        ('B', 'fld1', 'f{reg}'),  # 11:0000011101:{reg}:000000000000000 шаблон B
        ('B', 'fldz', 'f{reg}')))  # 11:0000011110:{reg}:000000000000000 шаблон B
    
    def __init__(self):
        pass
        
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

    def NewCode(self, adr, code):
        '''
        Заносит новый адрес и код в процессор    
        '''
        self.adr = adr
        self.code = code
        
    def SplitCode(self):
        '''
        Разбор структуры кода,
        определение типа команды, кода операции, название команды
        имени шаблона, команды ассемблера    
        '''
        self.T = self.code >> 30  # 2 бита тип команды
        self.OP = ((self.code >> 20) & 0x3FF)  # 10 бит код операции
        self.DD = self.code & 0xFFFFF  # 20 бит данных
        # имя шаблона, название команды на ассемблере, строка шаблона 
        self.NameT, self.CmdAsm, self.StrT = self.OpToAsm[self.T][self.OP]

    def CodeToAsm(self):
        self.SplitCode()
        ArgAsm = self.DecodeTemplate()
        ArgAsmRepl = ReplaceWords(ArgAsm, self.equ)
        return(f'{self.CmdAsm:6s} {ArgAsm:23s} # {ArgAsmRepl:25s}   # {self.T:02b} {self.OP:010b} {self.NameT:1s} {self.SplitBit():25s}')
        
    def SplitBit(self):
        pos = self.Template[self.NameT]
        b = f'{self.DD:020b}'    
        if len(pos):
            result = b[:pos[0]] + ' '
            for p1, p2 in zip(pos[:-1], pos[1:]):
                result += b[p1:p2] + ' '
            result += b[pos[-1]:]
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
