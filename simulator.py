"""Simulator for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import copy
from disassembler import Disassembler

"""Machine state for simulator."""
class State:
    def __init__(self):
        self.regs = [0 for i in range(16)]
        self.mem = [0 for i in range(256)]
        self.pc = 0
        self.sp = 255
        self.zero = False
        self.carry = False
    
    """Calculates difference between this state and another."""
    def diff(self, state):
        d = ""
    
        for i in range(16):
            if self.regs[i] != state.regs[i]:
                d += f", r{i} <- {state.regs[i]}"
        for i in range(256):
            if self.mem[i] != state.mem[i]:
                d += f", [{i}] <- {state.mem[i]}"
        if self.sp != state.sp:
            d += f", sp <- {state.sp}"
        if self.zero != state.zero:
            d += f", zf <- {state.zero}"
        if self.carry != state.carry:
            d += f", cf <- {state.carry}"
            
        if d != "":
            d = d[2:]
        return d

    def __str__(self):
        s = ""
        for i in range(16):
            s += f"r{i} = {self.regs[i]}, "
        s += f"pc = {self.pc}, sp = {self.sp}, zf = {self.zero}, cf = {self.carry}"

        return s
        
"""Simulates machine code."""
class Simulator:
    def __init__(self):
        self.disassembler = Disassembler()
        
    """Returns machine state after executing instruction."""
    def execute(self, bin, state):
        # Disassemble instruction
        m, dis = self.disassembler.process(bin)

        opcode = bin[0:4]
        r1 = int(bin[4:8], 2)
        r2 = int(bin[8:12], 2)
        r3 = int(bin[12:16], 2)
        cd = int(bin[8:16], 2)
        cb = int(bin[4:12], 2)
        next = copy.deepcopy(state)
        next.pc += 1

        # Simulate instructions
        if m == "ldr":
            if opcode == "0000":
                next.regs[r1] = state.mem[state.regs[r2]]
            elif opcode == "0001":
                next.regs[r1] = state.mem[cd]
            elif opcode == "0010":
                next.regs[r1] = cd
        elif m == "str":
            if opcode == "0011":
                next.mem[state.regs[r2]] = state.regs[r1]
            elif opcode == "0100":
                next.mem[cd] = state.regs[r1]
        elif m == "push":
            if state.sp == -1:
                raise RuntimeError("Stack overflow")
            next.mem[state.sp] =  state.regs[r1]
            next.sp -= 1
        elif m == "pop":
            if state.sp == 255:
                raise RuntimeError("Stack underflow")
            next.regs[r1] = state.mem[state.sp+1]
            next.sp += 1
        elif m == "ldsp":
            next.regs[r1] = state.sp
        elif m == "stsp":
            next.sp = state.regs[r1]
        elif m == "call":
            if state.sp == -1:
                raise RuntimeError("Stack overflow")
            next.mem[state.sp] = state.pc+1
            next.pc = cb
            next.sp -= 1
        elif m == "ret":
            if state.sp == 255:
                raise RuntimeError("Stack underflow")
            next.pc = state.mem[state.sp+1]
            next.sp += 1
        elif m == "bx":
            # Indirect jump
            next.pc = state.regs[r1]
        elif opcode == "1110":
            # Direct jumps
            if ( m == "b" or
                (m == "bz" and state.zero) or (m == "bnz" and not state.zero) or
                (m == "bcs" and state.carry) or (m == "bcc" and not state.carry)):
                next.pc = cb
        else:
            # ALU instructions (modify flags)
            if m == "mov":
                res = state.regs[r2]
            elif m == "mvn":
                res = ~state.regs[r2]
            elif m == "neg":
                res = 256-state.regs[r2]
            elif m == "inc":
                res = state.regs[r2] + 1
            elif m == "dec":
                res = state.regs[r2] + 255
            elif m == "lsl":
                res = state.regs[r2]<<1
            elif m == "lsr":
                res = state.regs[r2]>>1
            elif m == "rol":
                res = state.regs[r2]<<1 | state.carry
            elif m == "ror":
                res = state.regs[r2]>>1 | (128*state.carry)
            elif m == "add":
                res = state.regs[r2] + state.regs[r3]
            elif m == "adc":
                res = state.regs[r2] + state.regs[r3] + state.carry
            elif m == "sub":
                res = state.regs[r2] + (256-state.regs[r3])
            elif m == "sbc":
                res = state.regs[r2] + (256-state.regs[r3]) - (1 - state.carry)
            elif m == "and":
                res = state.regs[r2] & state.regs[r3]
            elif m == "orr":
                res = state.regs[r2] | state.regs[r3]
            elif m == "eor":
                res = state.regs[r2] ^ state.regs[r3]
            else:
                raise ValueError(f"Unknown opcode {opcode}")
            
            next.zero = ((res&255) == 0)
            next.carry = bool(res & 256)
            next.regs[r1] = res&255

        return next

    def help(self):
        print(
"""Available commands:
   h       This help.
   n       Advance to next instruction.
   p       Print current state.
   q       Exit simulator.
   rx      Print contents of register x.
   rx = y  Set register x to value y.
   [a]     Print contents of memory address a.
   [a] = y Set memory address a to value y.
""")

    """Simulate machine code."""
    def process(self, mem):
        state = State()
        for i, c in enumerate(mem["data"]):
            state.mem[i] = int(c[0], 2)
    
        while True:
            # Print current instruction
            bin = mem['code'][state.pc][0]
            _, dis = self.disassembler.process(bin)
            print(f"{state.pc:3}: {bin[0:8]} {bin[8:16]} ({dis})")

            next = copy.deepcopy(state)

            # Present interface
            cmd = input(">> ").strip()
            if cmd == "" or cmd == "n":
                # Advance to next instruction
                next = self.execute(bin, state)
            elif cmd == "p":
                # Print current state
                print(state)
            elif cmd == "q":
                # Exit simulator
                return
            elif cmd[0] == "r":
                # Set register
                tokens = [t.strip() for t in cmd.split('=')]
                if len(tokens[0]) < 2:
                    self.help()
                elif len(tokens) == 1:
                    try:
                        print(f"r{int(tokens[0][1:])} = {state.regs[int(tokens[0][1:])]}")
                    except Exception as e:
                        print(e)
                elif len(tokens) == 2:
                    try:
                        next.regs[int(tokens[0][1:])] = int(tokens[1], 0)&255
                    except Exception as e:
                        print(e)
                else:
                    self.help()
            elif cmd[0] == "[":
                # Set memory address
                tokens = [t.strip() for t in cmd.split('=')]
                if len(tokens[0]) < 2 or tokens[0][0] != '[' or tokens[0][-1] != ']':
                    self.help()
                elif len(tokens) == 1:
                    try:
                        print(f"[{int(tokens[0][1:-1])}] = {state.mem[int(tokens[0][1:-1])]}")
                    except Exception as e:
                        print(e)
                elif len(tokens) == 2:
                    try:
                        next.mem[int(tokens[0][1:-1])] = int(tokens[1], 0)&255
                    except Exception as e:
                        print(e)
                else:
                    self.help()
            else:
                self.help()

            # Print resulting difference
            diff = state.diff(next)
            if diff != "":
                print("     " + diff)
            state = copy.deepcopy(next)
