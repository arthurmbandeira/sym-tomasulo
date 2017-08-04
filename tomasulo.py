import sys
from structs import *
from utils import *

class Tomasulo:
    """docstring for Tomasulo"""
    def __init__(self, ins_list):
        self.ins_list = ins_list
        self.program_counter = 0
        self.solve_branch = False

        self.reg_size = 8
        self.mem_size = 1024
        self.registers = Register(size=self.reg_size)
        self.memory = Memory(size=self.mem_size)

        self.rs_list = [ReservationStation() for i in range(20)]
        self.rs_map = {'add': (0, 4), 'addi': (0, 4), 'sub': (0, 4), 'subi': (0, 4),
                       'and': (0, 4), 'or': (0, 4), 'not': (0, 4),
                       'blt': (0, 4), 'bgt': (0, 4), 'beq': (0, 4), 'j': (0, 4),
                       'mul': (4, 12), 'div': (4, 12),
                       'lw': (12, 20), 'sw': (12, 20)
                       }

        self.mem_unit = MemUnit()
        self.add_unit1 = AddUnit()
        self.add_unit2 = AddUnit()
        self.mul_unit1 = MultUnit()
        self.mul_unit2 = MultUnit()

        self.mem_queue = []

        self.clock_now = 0

        self.run()

    def reset(self):
        for i in self.ins_list:
            i.reset()

        self.registers.reset()
        self.memory.reset()

        for r in self.rs_list:
            r.reset()

        self.mem_unit.reset()
        self.add_unit.reset()
        self.sub_unit.reset()
        self.mul_unit.reset()
        self.div_unit.reset()

        self.mem_queue = []

        self.program_counter = 0
        self.clock_now = 0

    def write_memory(self, index, data):
        self.memory.set_item(index/4, float(data))

    def read_memory(self, index):
        return self.memory.get_item(index/4)

    def print_state(self):
        print("(1) Emitted / (2) Executing / (3) Writed")
        print("Clock: {0} / PC: {1}".format(self.clock_now, self.program_counter))
        for ins in self.ins_list:
            if ins.get_name() == 'MemOp':
                print("{0} {1} {2}: {3}".format(ins.opcode, ins.rd, ins.rs, ins.state))
            elif ins.get_name() == 'BranchOp':
                if ins.opcode in ['j']:
                    print("{0} {1}: {3}".format(
                        ins.opcode, ins.imm, ins.state)
                    )
                else:
                    print("{0} {1} {2} {3}: {4}".format(
                        ins.opcode, ins.rs, ins.rt, ins.imm, ins.state)
                    )
            elif ins.opcode in ['addi', 'subi']:
                print("{0} {1} {2} {3}: {4}".format(
                    ins.opcode, ins.rd, ins.rs, ins.imm, ins.state)
                )
            elif ins.opcode in ['not']:
                print("{0} {1} {2}: {3}".format(
                    ins.opcode, ins.rd, ins.rs, ins.state)
                )
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
        for r_id in range(len(self.rs_list)):
            if r_id in [4, 12]: print()
            print("RS #{0}, Op: {1}, Qj: {2}, Qk: {3}, Vj: {4}, Vk: {5}, busy: {6}, A: {7}".format(
                r_id, 
                self.rs_list[r_id].op, 
                self.rs_list[r_id].qj, 
                self.rs_list[r_id].qk,
                self.rs_list[r_id].vj,
                self.rs_list[r_id].vk,
                self.rs_list[r_id].busy,
                self.rs_list[r_id].A
                )
            )

    def print_units(self):
        print("Add Unit 1: rs_id: {0}, result: {1}, busy: {2}, end_time: {3}".format(
            self.add_unit1.rs_id,
            self.add_unit1.result,
            self.add_unit1.busy,
            self.add_unit1.end_time
            )
        )
        print("Add Unit 2: rs_id: {0}, result: {1}, busy: {2}, end_time: {3}".format(
            self.add_unit2.rs_id,
            self.add_unit2.result,
            self.add_unit2.busy,
            self.add_unit2.end_time
            )
        )
        print("Mul Unit 1: rs_id: {0}, result: {1}, busy: {2}, end_time: {3}".format(
            self.mul_unit1.rs_id,
            self.mul_unit1.result,
            self.mul_unit1.busy,
            self.mul_unit1.end_time
            )
        )
        print("Mul Unit 2: rs_id: {0}, result: {1}, busy: {2}, end_time: {3}".format(
            self.mul_unit2.rs_id,
            self.mul_unit2.result,
            self.mul_unit2.busy,
            self.mul_unit2.end_time
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
                print('#'*10+' Execution Ended '+'#'*10)
                break

            self.step()
            self.print_rs()
            print()
            self.print_state()
            print()
            self.print_units()
            input('\nPress any key to continue...\n')

    def step(self):

        self.clock_now += 1

        self.update()
        self.execute()
        self.dispatch()

    def dispatch(self):
        if not self.solve_branch:
            if self.program_counter >= len(self.ins_list):
                return

            current_ins = self.ins_list[self.program_counter]

            for i in range(self.rs_map[current_ins.opcode][0], self.rs_map[current_ins.opcode][1]):
                if not self.rs_list[i].busy:
                    current_ins.state = 1

                    self.rs_list[i].op = current_ins.opcode
                    self.rs_list[i].busy = True

                    if current_ins.opcode == 'lw' or current_ins.opcode == 'sw':
                        self.rs_list[i].A = int(current_ins.imm) + int(self.registers.val[parse_register(current_ins.rs)])

                        # load
                        if current_ins.opcode == 'lw':
                            self.registers.qi[parse_register(current_ins.rd)] = i
                        # store
                        else:
                            if self.registers.qi[parse_register(current_ins.rd)] == 0:
                                self.rs_list[i].qj = 0
                                self.rs_list[i].vj = self.registers.val[parse_register(current_ins.rd)]
                            else:
                                self.rs_list[i].qj = self.registers.qi[parse_register(current_ins.rd)]

                        self.mem_queue.append(i)
                    elif current_ins.opcode == 'addi' or current_ins.opcode == 'subi':
                        # rs
                        if self.registers.qi[parse_register(current_ins.rs)] == 0:
                            self.rs_list[i].qj = 0
                            self.rs_list[i].vj = self.registers.val[parse_register(current_ins.rs)]
                        else:
                            self.rs_list[i].qj = self.registers.qi[parse_register(current_ins.rs)]

                        # imm
                        self.rs_list[i].qk = 0
                        self.rs_list[i].vk = int(current_ins.imm)
                        
                        self.registers.qi[parse_register(current_ins.rd)] = i
                    elif current_ins.opcode == 'not':
                        # rs
                        if self.registers.qi[parse_register(current_ins.rs)] == 0:
                            self.rs_list[i].qj = 0
                            self.rs_list[i].vj = self.registers.val[parse_register(current_ins.rs)]
                        else:
                            self.rs_list[i].qj = self.registers.qi[parse_register(current_ins.rs)]
                        self.registers.qi[parse_register(current_ins.rd)] = i
                    elif current_ins.opcode in ['blt', 'bgt', 'beq']:
                        solve_branch = True
                        # rs
                        if self.registers.qi[parse_register(current_ins.rs)] == 0:
                            self.rs_list[i].qj = 0
                            self.rs_list[i].vj = self.registers.val[parse_register(current_ins.rs)]
                        else:
                            self.rs_list[i].qj = self.registers.qi[parse_register(current_ins.rs)]

                        # rt
                        if self.registers.qi[parse_register(current_ins.rt)] == 0:
                            self.rs_list[i].qk = 0
                            self.rs_list[i].vk = self.registers.val[parse_register(current_ins.rt)]
                        else:
                            self.rs_list[i].qk = self.registers.qi[parse_register(current_ins.rt)]

                        # print(parse_register(current_ins.rd))
                        
                        # self.registers.qi[parse_register(current_ins.rd)] = i
                    elif current_ins.opcode in ['j']:
                        pass

                        

                    else:
                        # rs
                        if self.registers.qi[parse_register(current_ins.rs)] == 0:
                            self.rs_list[i].qj = 0
                            self.rs_list[i].vj = self.registers.val[parse_register(current_ins.rs)]
                        else:
                            self.rs_list[i].qj = self.registers.qi[parse_register(current_ins.rs)]

                        # rt
                        if self.registers.qi[parse_register(current_ins.rt)] == 0:
                            self.rs_list[i].qk = 0
                            self.rs_list[i].vk = self.registers.val[parse_register(current_ins.rt)]
                        else:
                            self.rs_list[i].qk = self.registers.qi[parse_register(current_ins.rt)]

                        # print(parse_register(current_ins.rd))
                        self.registers.qi[parse_register(current_ins.rd)] = i

                    self.rs_list[i].ins = self.ins_list[self.program_counter]
                    self.program_counter += 1
                    break

    def execute(self): 
        # load/store
        if len(self.mem_queue) > 0:
            rs_index = self.mem_queue[0]

            current_ins = self.rs_list[rs_index].ins

            if current_ins.state < 2:
                if self.rs_list[rs_index].op == 'lw':
                    self.mem_unit.result = self.memory.get_item(int(self.rs_list[rs_index].A/4))
                    current_ins.state = 2

                    self.mem_unit.rs_id = rs_index
                    self.mem_unit.end_time = self.clock_now + self.rs_list[rs_index].ins.cycle_cost
                elif self.rs_list[rs_index].op == 'sw':
                    if self.rs_list[rs_index].qj == 0:
                        self.mem_unit.result = self.rs_list[rs_index].vj
                        current_ins.state = 2

                        self.mem_unit.rs_id = rs_index
                        self.mem_unit.end_time = self.clock_now + self.rs_list[rs_index].ins.cycle_cost
            else:
                pass

        # adder
        if self.add_unit1.busy == False:
            for i in range(self.rs_map['add'][0], self.rs_map['add'][1]):
                if self.rs_list[i].qj == 0 and self.rs_list[i].qk == 0 and self.rs_list[i].busy == True and self.rs_list[i].ins.state == 1:
                    if self.rs_list[i].ins.opcode == 'add':
                        self.add_unit1.result = self.rs_list[i].vj + self.rs_list[i].vk
                        print('#'*10+' Generating a add result: {0} + {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit1.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'addi':
                        self.add_unit1.result = self.rs_list[i].vj + self.rs_list[i].vk
                        print('#'*10+' Generating a addi result: {0} + {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit1.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'sub':
                        self.add_unit1.result = self.rs_list[i].vj - self.rs_list[i].vk
                        print('#'*10+' Generating a sub result: {0} - {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit1.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'subi':
                        self.add_unit1.result = self.rs_list[i].vj - self.rs_list[i].vk
                        print('#'*10+' Generating a subi result: {0} - {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit1.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'and':
                        self.add_unit1.result = self.rs_list[i].vj and self.rs_list[i].vk
                        print('#'*10+' Generating an and result: {0} && {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit1.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'or':
                        self.add_unit1.result = self.rs_list[i].vj or self.rs_list[i].vk
                        print('#'*10+' Generating an or result: {0} || {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit1.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'not':
                        self.add_unit1.result = not self.rs_list[i].vj
                        print('#'*10+' Generating a not result: ~{0} = {1}'.format(self.rs_list[i].vj, self.add_unit1.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'blt':
                        if self.rs_list[i].vj < self.rs_list[i].vk:
                            self.solve_branch = True
                            self.program_counter = self.rs_list[i].ins.imm
                            print('Branch '+str(self.rs_list[i].ins.opcode))
                    elif self.rs_list[i].ins.opcode == 'bgt':
                        if self.rs_list[i].vj > self.rs_list[i].vk:
                            self.solve_branch = True
                            self.program_counter = self.rs_list[i].ins.imm
                            print('Branch '+str(self.rs_list[i].ins.opcode))
                    elif self.rs_list[i].ins.opcode == 'beq':
                        if self.rs_list[i].vj == self.rs_list[i].vk:
                            self.solve_branch = True
                            self.program_counter = self.rs_list[i].ins.imm
                            print('Branch '+str(self.rs_list[i].ins.opcode))
                    elif self.rs_list[i].ins.opcode == 'j':
                        self.solve_branch = True
                        self.program_counter = self.rs_list[i].ins.imm
                        print('Branch '+str(self.rs_list[i].ins.opcode))

                    self.rs_list[i].ins.state = 2

                    self.add_unit1.rs_id = i
                    self.add_unit1.end_time = self.clock_now + self.rs_list[i].ins.cycle_cost
                    self.add_unit1.busy = True
                    break

        elif self.add_unit2.busy == False:
            for i in range(self.rs_map['add'][0], self.rs_map['add'][1]):
                if self.rs_list[i].qj == 0 and self.rs_list[i].qk == 0 and self.rs_list[i].busy == True and self.rs_list[i].ins.state == 1:
                    if self.rs_list[i].ins.opcode == 'add':
                        self.add_unit2.result = self.rs_list[i].vj + self.rs_list[i].vk
                        print('#'*10+' Generating a add result: {0} + {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit2.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'addi':
                        self.add_unit2.result = self.rs_list[i].vj + self.rs_list[i].vk
                        print('#'*10+' Generating a addi result: {0} + {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit2.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'sub':
                        self.add_unit2.result = self.rs_list[i].vj - self.rs_list[i].vk
                        print('#'*10+' Generating a sub result: {0} - {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit2.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'subi':
                        self.add_unit2.result = self.rs_list[i].vj - self.rs_list[i].vk
                        print('#'*10+' Generating a subi result: {0} - {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit2.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'and':
                        self.add_unit2.result = self.rs_list[i].vj and self.rs_list[i].vk
                        print('#'*10+' Generating an and result: {0} && {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit2.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'or':
                        self.add_unit2.result = self.rs_list[i].vj or self.rs_list[i].vk
                        print('#'*10+' Generating an or result: {0} || {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.add_unit2.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'not':
                        self.add_unit2.result = not self.rs_list[i].vj
                        print('#'*10+' Generating a not result: ~{0} = {1}'.format(self.rs_list[i].vj, self.add_unit2.result))
                        print()
                    elif self.rs_list[i].ins.opcode == 'blt':
                        if self.rs_list[i].vj < self.rs_list[i].vk:
                            self.solve_branch = True
                            self.program_counter = self.rs_list[i].ins.imm
                            print('Branch '+str(self.rs_list[i].ins.opcode))
                    elif self.rs_list[i].ins.opcode == 'bgt':
                        if self.rs_list[i].vj > self.rs_list[i].vk:
                            self.solve_branch = True
                            self.program_counter = self.rs_list[i].ins.imm
                            print('Branch '+str(self.rs_list[i].ins.opcode))
                    elif self.rs_list[i].ins.opcode == 'beq':
                        if self.rs_list[i].vj == self.rs_list[i].vk:
                            self.solve_branch = True
                            self.program_counter = self.rs_list[i].ins.imm
                            print('Branch '+str(self.rs_list[i].ins.opcode))
                    elif self.rs_list[i].ins.opcode == 'j':
                        self.solve_branch = True
                        self.program_counter = self.rs_list[i].ins.imm
                        print('Branch '+str(self.rs_list[i].ins.opcode))

                    self.rs_list[i].ins.state = 2

                    self.add_unit2.rs_id = i
                    self.add_unit2.end_time = self.clock_now + self.rs_list[i].ins.cycle_cost
                    self.add_unit2.busy = True
                    break

        else:
            pass


        # multiplier
        if self.mul_unit1.busy == False:
            for i in range(self.rs_map['mul'][0], self.rs_map['mul'][1]):
                if self.rs_list[i].qj == 0 and self.rs_list[i].qk == 0 and self.rs_list[i].busy == True and self.rs_list[i].ins.state == 1:
                    if self.rs_list[i].ins.opcode == 'mul':
                        self.mul_unit1.result = self.rs_list[i].vj * self.rs_list[i].vk
                        print('Generating a mul result: {0} * {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.mul_unit1.result))
                    elif self.rs_list[i].ins.opcode == 'div':
                        if self.rs_list[i].vk != 0:
                            self.mul_unit1.result = self.rs_list[i].vj / self.rs_list[i].vk
                        else:
                            self.mul_unit1.result = 0
                        print('Generating a div result: {0} / {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.mul_unit1.result))

                    self.rs_list[i].ins.state = 2

                    self.mul_unit1.rs_id = i
                    self.mul_unit1.end_time = self.clock_now + self.rs_list[i].ins.cycle_cost
                    self.mul_unit1.busy = True
                    break

        elif self.mul_unit2.busy == False:
            for i in range(self.rs_map['mul'][0], self.rs_map['mul'][1]):
                if self.rs_list[i].qj == 0 and self.rs_list[i].qk == 0 and self.rs_list[i].busy == True and self.rs_list[i].ins.state == 1:
                    if self.rs_list[i].ins.opcode == 'mul':
                        self.mul_unit2.result = self.rs_list[i].vj * self.rs_list[i].vk
                        print('Generating a mul result: {0} * {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.mul_unit2.result))
                    elif self.rs_list[i].ins.opcode == 'div':
                        if self.rs_list[i].vk != 0:
                            self.mul_unit2.result = self.rs_list[i].vj / self.rs_list[i].vk
                        else:
                            self.mul_unit2.result = 0
                        print('Generating a div result: {0} / {1} = {2}'.format(self.rs_list[i].vj, self.rs_list[i].vk, self.mul_unit2.result))

                    self.rs_list[i].ins.state = 2

                    self.mul_unit2.rs_id = i
                    self.mul_unit2.end_time = self.clock_now + self.rs_list[i].ins.cycle_cost
                    self.mul_unit2.busy = True
                    break

        else:
            pass

    def update(self):
        # load/store
        if self.mem_unit.end_time == self.clock_now:
            rs_index = self.mem_queue[0]
            ins = self.rs_list[rs_index].ins

            if ins.opcode == 'lw':
                self.registers.val[parse_register(ins.rd)] = self.mem_unit.result
                self.registers.qi[parse_register(ins.rd)] = 0

                for i in range(self.rs_map['add'][0], self.rs_map['lw'][1]):
                    if self.rs_list[i].qj == self.mem_unit.rs_id:
                        self.rs_list[i].qj = 0
                        self.rs_list[i].vj = self.mem_unit.result
                    if self.rs_list[i].qk == self.mem_unit.rs_id:
                        self.rs_list[i].qk = 0
                        self.rs_list[i].vk = self.mem_unit.result

            elif ins.opcode == 'sw':
                self.memory.set_item(self.rs_list[rs_index].A/4, self.mem_unit.result)

            assert(rs_index == self.mem_unit.rs_id)
            self.rs_list[rs_index].ins.state = 3
            self.rs_list[rs_index].ins.busy = False

            self.mem_queue.remove(rs_index)

        self.update_unit(self.add_unit1)
        self.update_unit(self.add_unit2)
        self.update_unit(self.mul_unit1)
        self.update_unit(self.mul_unit2)

        # if self.add_unit1.end_time == self.clock_now:
        #     for reg_id in range(self.reg_size):
        #         if self.registers.qi[reg_id] == self.add_unit1.rs_id:
        #             self.registers.qi[reg_id] = 0
        #             self.registers.val[reg_id] = self.add_unit1.result

        #     for i in range(self.rs_map['add'][0], self.rs_map['lw'][1]):
        #         if self.rs_list[i].qj == self.add_unit1.rs_id:
        #             self.rs_list[i].qj = 0
        #             self.rs_list[i].vj = self.add_unit1.result
        #         if self.rs_list[i].qk == self.add_unit1.rs_id:
        #             self.rs_list[i].qk = 0
        #             self.rs_list[i].vk = self.add_unit1.result

        #     self.rs_list[self.add_unit1.rs_id].ins.state = 3
        #     self.rs_list[self.add_unit1.rs_id].ins.busy = False
        #     self.add_unit1.busy = False

        # if self.add_unit2.end_time == self.clock_now:
        #     for reg_id in range(self.reg_size):
        #         if self.registers.qi[reg_id] == self.add_unit2.rs_id:
        #             self.registers.qi[reg_id] = 0
        #             self.registers.val[reg_id] = self.add_unit2.result

        #     for i in range(self.rs_map['add'][0], self.rs_map['lw'][1]):
        #         if self.rs_list[i].qj == self.add_unit2.rs_id:
        #             self.rs_list[i].qj = 0
        #             self.rs_list[i].vj = self.add_unit2.result
        #         if self.rs_list[i].qk == self.add_unit2.rs_id:
        #             self.rs_list[i].qk = 0
        #             self.rs_list[i].vk = self.add_unit2.result

        #     self.rs_list[self.add_unit2.rs_id].ins.state = 3
        #     self.rs_list[self.add_unit2.rs_id].ins.busy = False
        #     self.add_unit2.busy = False

        # if self.mul_unit1.end_time == self.clock_now:
        #     for reg_id in range(self.reg_size):
        #         if self.registers.qi[reg_id] == self.mul_unit1.rs_id:
        #             self.registers.qi[reg_id] = 0
        #             self.registers.val[reg_id] = self.mul_unit1.result

        #     for i in range(self.rs_map['add'][0], self.rs_map['lw'][1]):
        #         if self.rs_list[i].qj == self.mul_unit1.rs_id:
        #             self.rs_list[i].qj = 0
        #             self.rs_list[i].vj = self.mul_unit1.result
        #         if self.rs_list[i].qk == self.mul_unit1.rs_id:
        #             self.rs_list[i].qk = 0
        #             self.rs_list[i].vk = self.mul_unit1.result

        #     self.rs_list[self.mul_unit1.rs_id].ins.state = 3
        #     self.rs_list[self.mul_unit1.rs_id].ins.busy = False
        #     self.mul_unit1.busy = False

        # if self.mul_unit2.end_time == self.clock_now:
        #     for reg_id in range(self.reg_size):
        #         if self.registers.qi[reg_id] == self.mul_unit2.rs_id:
        #             self.registers.qi[reg_id] = 0
        #             self.registers.val[reg_id] = self.mul_unit2.result

        #     for i in range(self.rs_map['add'][0], self.rs_map['lw'][1]):
        #         if self.rs_list[i].qj == self.mul_unit2.rs_id:
        #             self.rs_list[i].qj = 0
        #             self.rs_list[i].vj = self.mul_unit2.result
        #         if self.rs_list[i].qk == self.mul_unit2.rs_id:
        #             self.rs_list[i].qk = 0
        #             self.rs_list[i].vk = self.mul_unit2.result

        #     self.rs_list[self.mul_unit2.rs_id].ins.state = 3
        #     self.rs_list[self.mul_unit2.rs_id].ins.busy = False
        #     self.mul_unit2.busy = False

    def update_unit(self, unit):
        if unit.end_time == self.clock_now:
            for reg_id in range(self.reg_size):
                if self.registers.qi[reg_id] == unit.rs_id:
                    self.registers.qi[reg_id] = 0
                    self.registers.val[reg_id] = unit.result

            for i in range(self.rs_map['add'][0], self.rs_map['lw'][1]):
                if self.rs_list[i].qj == unit.rs_id:
                    self.rs_list[i].qj = 0
                    self.rs_list[i].vj = unit.result
                if self.rs_list[i].qk == unit.rs_id:
                    self.rs_list[i].qk = 0
                    self.rs_list[i].vk = unit.result

            self.rs_list[unit.rs_id].ins.state = 3
            self.rs_list[unit.rs_id].ins.busy = False
            unit.busy = False