class Instruction(object):
    """docstring for Instruction"""
    def __init__(self, opcode, cycle_cost=0):
        self.opcode = opcode
        self.state = 0
        self.cycle_cost = cycle_cost

    def reset(self):
        self.state = 0


class BinOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, cycle_cost, rd, rs, rt=None, imm=None):
        super(BinOp, self).__init__(opcode, cycle_cost)
        self.rd = rd
        self.rs = rs
        self.rt = rt
        self.imm = imm


class LogicOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, cycle_cost, rd, rs, rt=None):
        super(LogicOp, self).__init__(opcode, cycle_cost)
        self.rd = rd
        self.rs = rs
        self.rt = rt


class BranchOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, cycle_cost, imm, rs=None, rt=None):
        super(BranchOp, self).__init__(opcode, cycle_cost)
        self.rs = rs
        self.rt = rt
        self.imm = imm


class MemOp(Instruction):
    """docstring for Instruction"""
    def __init__(self, opcode, cycle_cost, rd, rs, imm):
        super(MemOp, self).__init__(opcode, cycle_cost)
        self.rd = rd
        self.rs = rs
        self.imm = imm        