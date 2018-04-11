import sys

def readAsmFile(filepath):
    f = open(filepath, 'rb')
    lines = f.readlines()
    f.close()
    return lines


def readAsmLine(line):
    if line[0] == '.':
        return ['.', '.', '.']

    line_split = line.split()
    line_label = ''
    line_opcode = ''
    line_operand = ''
    if len(line_split) == 1:
        line_opcode = line_split[0]
    if len(line_split) == 2:
        line_opcode, line_operand = line_split
    elif len(line_split) == 3:
        line_label, line_opcode, line_operand = line_split
    return [line_label, line_opcode, line_operand]


def printStart_add(start_addr):
    print 'Start address is', start_addr


def cal_displacement(target_address, pc):
    return target_address - pc


def build_object_code(op_value, is_immediate, is_pc_relative, displacement):
    # print '\n'
    # print 'op_value :', op_value
    # print 'is_immediate :', is_immediate
    # print 'is_pc_relative :', is_pc_relative
    # print 'displacement :', displacement

    if is_immediate:
        one = op_value + 1
    else:
        one = op_value + 3

    if is_pc_relative:
        two = 2
    else:
        two = 0

    # print 'one :', one
    # print 'two :', two
    # return format(one, 'X').zfill(2) + ' ' + format(two, 'X') + ' ' + format(displacement, 'X').zfill(3)
    return format(one, 'X').zfill(2) + format(two, 'X') + format(displacement, 'X').zfill(3)

# -- depth 2


def checkArgv():
    if len(sys.argv) == 1:
        print 'Please set asm filename'
        exit()
    elif len(sys.argv) >= 3:
        print 'Please only set 1 argument for asm filename'
        exit()


def pass1(intermediate_file, SYMTAB, OPTAB):
    LOCCTR = 0
    start_addr = 0
    lines = readAsmFile(sys.argv[1])
    for line in lines:
        line_label, line_opcode, line_operand = readAsmLine(line)
        if line_opcode == 'START':
            start_addr = int(line_operand)
            LOCCTR = start_addr

            # printStart_add(start_addr)
        elif line_opcode != 'END':
            if not line_label == '.':  # this is not a comment line
                if not line_label == '':  # there is a symbol in the LABEL field
                    if line_label in SYMTAB:  # search SYMTAB for LABEL, if found then set error flag
                        print 'ERROR: duplicated symbol'
                        exit()
                    else:
                        SYMTAB[line_label] = LOCCTR  # insert (LABEL, LOCCTR) into SYMTAB

                # write line to intermediate file
                intermediate_file.append([LOCCTR, line_label, line_opcode, line_operand])
                if line_opcode in OPTAB:  # search OPTAB for OPCODE
                    LOCCTR += 3
                elif line_opcode == 'WORD':
                    LOCCTR += 3
                elif line_opcode == 'RESW':
                    LOCCTR += 3 * int(line_operand)
                elif line_operand == 'RESB':
                    LOCCTR += int(line_operand)
                elif line_operand == 'BYTE':
                    print 'implement later'
                else:
                    print 'ERROR: invalid operation code'
                    exit()
    program_length = LOCCTR - start_addr

    """
    print 'program length is', program_length, '\n'
    print SYMTAB.items(), '\n'
    for line in intermediate_file:
        print line
    # """


def pass2(intermediate_file, SYMTAB, OPTAB):
    for line in intermediate_file:

        line_address, line_label, line_opcode, line_operand = line

        if line_opcode in OPTAB:
            if line_operand != '':
                if line_operand[0] == '#':
                    is_immediate = 1
                    is_pc_relative = 0
                    displacement = int(line_operand[1:])
                else:
                    is_immediate = 0
                    is_pc_relative = 1
                    target_address = SYMTAB[line_operand]
                    displacement = cal_displacement(target_address, intermediate_file[intermediate_file.index(line)+1][0])
            else:
                is_immediate = 0
                is_pc_relative = 0
                displacement = 0
            object_code = build_object_code(OPTAB[line_opcode], is_immediate, is_pc_relative, displacement)

        elif line_opcode == 'WORD':
            displacement = format(int(line_operand), 'X')
            object_code = displacement.zfill(6)

        else:
            object_code = ''.zfill(6)

        print format(line_address, 'X').zfill(5), object_code

# - depth 1


def main():
    intermediate_file = []
    SYMTAB = {}
    OPTAB = {'START': '', 'LDA': 0x00, 'STA': 0x0C, 'ADD': 0x18, 'RSUB': 0x4C}

    checkArgv()
    pass1(intermediate_file, SYMTAB, OPTAB)
    pass2(intermediate_file, SYMTAB, OPTAB)

main()
