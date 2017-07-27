class Instruction():
    """docstring for Instruction"""
    def __init__(self, opcode):
        self.opcode = opcode
        self.state = 0
        self.cycle_cost = 0


# class RegInst(Instruction):
#     """docstring for Instruction"""
#     def __init__(self, opcode, rd, rs, rt):
#         # self.opcode = opcode
#         self


# class ImmInst(Instruction):
#     """docstring for Instruction"""
#     def __init__(self):
#         self.opcode = opcode


# class MemInst(Instruction):
#     """docstring for Instruction"""
#     def __init__(self):
#         self.opcode = opcode


class BinOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, rd, rs, rt=None, imm=None):
        # self.opcode = opcode
        self.rd = rd
        self.rs = rs
        self.rt = rt
        self.imm = imm


class LogicOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, rd, rs, rt=None):
        self.rd = rd
        self.rs = rs
        self.rt = rt


class BranchOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, imm, rs=None, rt=None):
        self.rs = rs
        self.rt = rt
        self.imm = imm


class MemOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, rd, rs, imm):
        self.rd = rd
        self.rs = rs
        self.imm = imm
        