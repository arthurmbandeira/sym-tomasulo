class ReservationStation:
    """docstring for ReservationStation"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.op = ''
        self.qj = 0
        self.qk = 0
        self.vj = 0
        self.vk = 0
        self.A = 0
        self.busy = False
        self.ins = None


class Instruction(object):
    """docstring for Instruction"""
    def __init__(self, opcode, cycle_cost=0):
        self.opcode = opcode
        self.state = 0
        self.cycle_cost = cycle_cost

    def reset(self):
        self.state = 0

    def get_name(self):
        return self.__class__.__name__


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


class Register:
    """docstring for Register"""
    def __init__(self, size=8):
        self.qi = [0 for i in range(size+1)]
        self.val = [0 for i in range(size+1)]

    def reset(self):
        self.qi = [0 for i in range(len(self.qi))]
        self.val = [0 for i in range(len(self.val))]


class Memory:
    """docstring for Memory"""
    def __init__(self, size=1024):
        self.data = [0 for i in range(size)]

    def get_item(self, index):
        return self.data[index]

    def set_item(self, index, data_):
        self.data[index] = data_

    def reset(self):
        self.data = [0 for i in range(len(self.data))]


class AddUnit:
    """docstring for Unit"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.rs_id = -1
        self.end_time = 0
        self.busy = False
        self.result = 0


class MultUnit:
    """docstring for Unit"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.rs_id = -1
        self.end_time = 0
        self.busy = False
        self.result = 0


class MemUnit:
    """docstring for Unit"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.rs_id = -1
        self.end_time = 0
        self.result = 0
