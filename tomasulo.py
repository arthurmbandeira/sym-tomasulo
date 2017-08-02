import sys
from structs import *
from utils import *

class Tomasulo:
    """docstring for Tomasulo"""
    def __init__(self, ins_list):
        self.ins_list = ins_list
        self.ins_current_id = 0

        self.reg_size = 8
        self.mem_size = 1024
        self.registers = Register(size=self.reg_size)
        self.memory = Memory(size=self.mem_size)

        self.rs_lst = [ReservationStation() for i in range(20)]
        self.rs_map = {'add': (0, 4), 'addi': (0, 4), 'sub': (0, 4), 'subi': (0, 4),
                       'and': (0, 4), 'or': (0, 4), 'not': (0, 4),
                       'blt': (0, 4), 'bgt': (0, 4), 'beq': (0, 4), 'j': (0, 4),
                       'mul': (4, 12), 'div': (4, 12),
                       'lw': (12, 20), 'sw': (12, 20)
                       }

        self.mem_unit = MemUnit()
        self.add_unit = AddUnit()
        self.sub_unit = AddUnit()
        self.mul_unit = MultUnit()
        self.div_unit = MultUnit()

        self.mem_queue = []

        self.clock_now = 0

        self.run()

    def reset(self):
        for i in self.ins_list:
            i.reset()

        self.registers.reset()
        self.memory.reset()

        for r in self.rs_lst:
            r.reset()

        self.mem_unit.reset()
        self.add_unit.reset()
        self.sub_unit.reset()
        self.mul_unit.reset()
        self.div_unit.reset()

        self.mem_queue = []

        self.ins_current_id = 0
        self.clock_now = 0

    def write_memory(self, index, data):
        self.memory.set_item(index/4, float(data))

    def read_memory(self, index):
        return self.memory.get_item(index/4)

    def print_state(self):
        print("Time: {0}".format(self.clock_now))
        for ins in self.ins_list:
            if ins.get_name() == 'MemOp':
                print("{0} {1} {2}: {3}".format(ins.opcode, ins.rd, ins.rs, ins.state))
            else:
                print("{0} {1} {2} {3}: {4}".format(
                    ins.opcode, ins.rd, ins.rs, ins.rt, ins.state)
                )
        print

    def print_reg(self):
        for r_id in range(self.reg_size):
            print("Registers: Q[{0}]: {1}, Value[{2}]: {3}".format(r_id, 
                self.registers.qi[r_id], 
                r_id, 
                self.registers.val[r_id])
            )

    def print_rs(self):
        for r_id in range(len(self.rs_lst)):
            print("RS #{0}, Op: {1}, Qj: {2}, Qk: {3}, Vj: {4}, Vk: {5}, busy: {6}, A: {7}".format(
                r_id, 
                self.rs_lst[r_id].op, 
                self.rs_lst[r_id].qj, 
                self.rs_lst[r_id].qk,
                self.rs_lst[r_id].vj,
                self.rs_lst[r_id].vk,
                self.rs_lst[r_id].busy,
                self.rs_lst[r_id].A
                )
            )

    def print_units(self):
        print("Add Unit: rs_id: {0}, result: {1}, busy: {2}, end_time: {3}".format(
            self.add_unit.rs_id,
            self.add_unit.result,
            self.add_unit.busy,
            self.add_unit.end_time
            )
        )
        print("Mult Unit: rs_id: {0}, result: {1}, busy: {2}, end_time: {3}".format(
            self.mul_unit.rs_id,
            self.mul_unit.result,
            self.mul_unit.busy,
            self.mul_unit.end_time
            )
        )

    def done(self):
        for i in self.ins_list:
            if i.state <= 2:
                return False
        return True

    def run(self):
        while True:
            if self.done():
                break

            self.step()
            self.print_rs()
            self.print_state()
            self.print_units()

    def step(self):

        self.clock_now += 1

        self.update()
        self.execute()
        self.influx()

        # self.writeback()
        # self.execution()
        # self.dispatch()

    def influx(self):
        if self.ins_current_id >= len(self.ins_list):
            return

        current_ins = self.ins_list[self.ins_current_id]
        # print(current_ins.state)
        # sys.exit()

        # print(self.rs_map[current_ins.opcode][0], self.rs_map[current_ins.opcode][1])

        # self.ins_current_id += 1


        for i in range(self.rs_map[current_ins.opcode][0], self.rs_map[current_ins.opcode][1]):
            if not self.rs_lst[i].busy:
                current_ins.state = 1

                self.rs_lst[i].op = current_ins.opcode
                self.rs_lst[i].busy = True

                if current_ins.opcode == 'lw' or current_ins.opcode == 'sw':
                    
                    self.rs_lst[i].A = (current_ins.imm+'+'+current_ins.rs)

                    # load
                    if current_ins.opcode == 'lw':
                        self.registers.qi[parse_register(current_ins.rd)] = i
                    # store
                    else:
                        if self.registers.qi[parse_register(current_ins.rd)] == 0:
                            self.rs_lst[i].qj = 0
                            self.rs_lst[i].vj = self.registers.val[parse_register(current_ins.rd)]
                        else:
                            self.rs_lst[i].qj = self.registers.qi[parse_register(current_ins.rd)]

                    self.mem_queue.append(i)

                else:
                    # rs
                    if self.registers.qi[parse_register(current_ins.rs)] == 0:
                        self.rs_lst[i].qj = 0
                        self.rs_lst[i].vj = self.registers.val[parse_register(current_ins.rs)]
                    else:
                        self.rs_lst[i].qj = self.registers.qi[parse_register(current_ins.rs)]

                    # rt
                    if self.registers.qi[parse_register(current_ins.rt)] == 0:
                        self.rs_lst[i].qk = 0
                        self.rs_lst[i].vk = self.registers.val[parse_register(current_ins.rt)]
                    else:
                        self.rs_lst[i].qk = self.registers.qi[parse_register(current_ins.rt)]

                    self.registers.qi[parse_register(current_ins.rd)] = i

                self.rs_lst[i].ins = self.ins_list[self.ins_current_id]
                print(self.rs_lst[i].ins)
                self.ins_current_id += 1
                break


        # # Adder
        # for i in range(4):
        #     if not self.rs_lst[i].busy:
        #         current_ins.state = 1

        #         self.rs_lst[i].opcode = current_ins.opcode
        #         self.rs_lst[i].busy = True

        #         # rs
        #         if self.registers.qi[current_ins.rs] == 0:
        #             self.rs_lst[i].qj = 0
        #             self.rs_lst[i].vj = self.registers.val[current_ins.rs]
        #         else:
        #             self.rs_lst[i].qj = self.registers.qi[current_ins.rs]

        #         # rt
        #         if self.registers.qi[current_ins.rt] == 0:
        #             self.rs_lst[i].qk = 0
        #             self.rs_lst[i].vk = self.registers.val[current_ins.rt]
        #         else:
        #             self.rs_lst[i].qk = self.registers.qi[current_ins.rt]

        #         self.registers.qi[current_ins.rd] = i

        #         self.rs_lst[i].ins = self.ins_list[self.ins_current_id]
        #         self.ins_current_id += 1
        #         break

        # # Multiplier
        # for i in range(4, 12):
        #     if not self.rs_lst[i].busy:
        #         current_ins.state = 1

        #         self.rs_lst[i].opcode = current_ins.opcode
        #         self.rs_lst[i].busy = True

        #         # rs
        #         if self.registers.qi[current_ins.rs] == 0:
        #             self.rs_lst[i].qj = 0
        #             self.rs_lst[i].vj = self.registers.val[current_ins.rs]
        #         else:
        #             self.rs_lst[i].qj = self.registers.qi[current_ins.rs]

        #         # rt
        #         if self.registers.qi[current_ins.rt] == 0:
        #             self.rs_lst[i].qk = 0
        #             self.rs_lst[i].vk = self.registers.val[current_ins.rt]
        #         else:
        #             self.rs_lst[i].qk = self.registers.qi[current_ins.rt]

        #         self.registers.qi[current_ins.rd] = i

        #         self.rs_lst[i].ins = self.ins_list[self.ins_current_id]
        #         self.ins_current_id += 1
        #         break

        # # Memory
        # for i in range(12, 20):
        #     if not self.rs_lst[i].busy:
        #         current_ins.state = 1

        #         self.rs_lst[i].opcode = current_ins.opcode
        #         self.rs_lst[i].busy = True

        #         self.rs_lst[i].A = current_ins.rs

        #         # load
        #         if current_ins.opcode == 'lw':
        #             self.registers.qi[current_ins.rd] = i
        #         # store
        #         else:
        #             if self.registers.qi[current_ins.rd] == 0:
        #                 self.rs_lst[i].qj = 0
        #                 self.rs_lst[i].vj = self.registers.val[current_ins.rd]
        #             else:
        #                 self.rs_lst[i].qj = self.registers.qi[current_ins.rd]

        #         self.mem_queue.append(i)

        #         self.rs_lst[i].ins = self.ins_list[self.ins_current_id]
        #         self.ins_current_id += 1
        #         break

    def execute(self):
        pass

    def update(self):
        pass

