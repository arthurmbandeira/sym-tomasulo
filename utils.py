from instruction import *

def parse(p):
    if len(p) == 4:
        if p[0] == 'add':
            BinOp(opcode=p[0], rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'addi':
            BinOp(opcode=p[0], rd=p[1], rs=p[2], imm=p[3])
        elif p[0] == 'sub':
            BinOp(opcode=p[0], rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'subi':
            BinOp(opcode=p[0], rd=p[1], rs=p[2], imm=p[3])
        elif p[0] == 'mul':
            BinOp(opcode=p[0], rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'div':
            BinOp(opcode=p[0], rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'and':
            LogicOp(opcode=p[0], rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'or':
            LogicOp(opcode=p[0], rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'blt':
            BranchOp(opcode=p[0], rs=p[1], rt=p[2], imm=p[3])
        elif p[0] == 'bgt':
            BranchOp(opcode=p[0], rs=p[1], rt=p[2], imm=p[3])
        elif p[0] == 'beq':
            BranchOp(opcode=p[0], rs=p[1], rt=p[2], imm=p[3])
        else:
            raise Exception('Invalid opcode {0}'.format(p[0]))
    elif len(p) == 3:
        if p[0] == 'not':
            LogicOp(opcode=p[0], rd=p[1], rs=p[2])
        elif p[0] == 'lw':
            spt_reg = p[2].replace('(', ' ').replace(')', ' ').split()
            MemOp(opcode=p[0], rd=p[1], rs=spt_reg[1], imm=spt_reg[0])
        elif p[0] == 'sw':
            spt_reg = p[2].replace('(', ' ').replace(')', ' ').split()
            MemOp(opcode=p[0], rd=spt_reg[1], rs=p[1], imm=spt_reg[0])
        else:
            raise Exception('Invalid opcode {0}'.format(p[0]))
    elif len(p) == 2:
        if p[0] == 'j':
            BranchOp(opcode=p[0], imm=p[1])
        else:
            raise Exception('Invalid opcode {0}'.format(p[0]))
    else:
        raise Exception('Invalid input')