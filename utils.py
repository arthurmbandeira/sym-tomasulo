import sys
from structs import *


def parse(p):
    if len(p) == 4:
        if p[0] == 'add':
            return BinOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'addi':
            return BinOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=p[2], imm=p[3])
        elif p[0] == 'sub':
            return BinOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'subi':
            return BinOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=p[2], imm=p[3])
        elif p[0] == 'mul':
            return BinOp(opcode=p[0], cycle_cost=10, rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'div':
            return BinOp(opcode=p[0], cycle_cost=20, rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'and':
            return LogicOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'or':
            return LogicOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=p[2], rt=p[3])
        elif p[0] == 'blt':
            return BranchOp(opcode=p[0], cycle_cost=5, rs=p[1], rt=p[2], imm=p[3])
        elif p[0] == 'bgt':
            return BranchOp(opcode=p[0], cycle_cost=5, rs=p[1], rt=p[2], imm=p[3])
        elif p[0] == 'beq':
            return BranchOp(opcode=p[0], cycle_cost=5, rs=p[1], rt=p[2], imm=p[3])
        else:
            raise Exception('Invalid opcode {0}'.format(p[0]))
    elif len(p) == 3:
        if p[0] == 'not':
            return LogicOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=p[2])
        elif p[0] == 'lw':
            spt_reg = p[2].replace('(', ' ').replace(')', ' ').split()
            return MemOp(opcode=p[0], cycle_cost=5, rd=p[1], rs=spt_reg[1], imm=spt_reg[0])
        elif p[0] == 'sw':
            spt_reg = p[2].replace('(', ' ').replace(')', ' ').split()
            return MemOp(opcode=p[0], cycle_cost=5, rd=spt_reg[1], rs=p[1], imm=spt_reg[0])
        else:
            raise Exception('Invalid opcode {0}'.format(p[0]))
    elif len(p) == 2:
        if p[0] == 'j':
            return BranchOp(opcode=p[0], cycle_cost=5, imm=p[1])
        else:
            raise Exception('Invalid opcode {0}'.format(p[0]))
    else:
        raise Exception('Invalid input')


def parse_register(r):
    return int(r[1:])


