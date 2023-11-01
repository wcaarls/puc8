"""Simulator for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import copy
from .disassembler import Disassembler

class State:
    """Machine state for simulator."""
    def __init__(self):
        self.regs = [0 for i in range(16)]
        self.mem = [0 for i in range(256)]
        self.regs[14] = 255
        self.zero = False
        self.carry = False
        self.negative = False
        self.overflow = False

    def diff(self, state):
        """Calculates difference between this state and another."""
        d = ''

        for i in range(14):
            if self.regs[i] != state.regs[i]:
                d += f', r{i} <- {state.regs[i]}'
        for i in range(256):
            if self.mem[i] != state.mem[i]:
                d += f', [{i}] <- {state.mem[i]}'
        if self.regs[14] != state.regs[14]:
            d += f', sp <- {state.regs[14]}'
        if self.zero != state.zero:
            d += f', zf <- {state.zero}'
        if self.carry != state.carry:
            d += f', cf <- {state.carry}'
        if self.negative != state.negative:
            d += f', nf <- {state.negative}'
        if self.overflow != state.overflow:
            d += f', vf <- {state.overflow}'

        if d != '':
            d = d[2:]
        return d

    def __str__(self):
        s = ''
        for i in range(14):
            s += f'r{i} = {self.regs[i]}, '
        s += f'pc = {self.regs[15]}, sp = {self.regs[14]}, zf = {self.zero}, cf = {self.carry}, nf = {self.negative}, vf = {self.overflow}'

        return s

class Simulator:
    """Simulates machine code."""
    def __init__(self):
        self.disassembler = Disassembler()

    def execute(self, bin, state):
        """Returns machine state after executing instruction."""
        # Disassemble instruction
        m, dis = self.disassembler.process(bin)

        opcode = bin[0:5]
        imm = int(opcode[4], 2)
        r1 = int(bin[5:9], 2)
        r2 = int(bin[9:13], 2)
        r3 = int(bin[13:17], 2)
        c4i = int(bin[13]*4 + bin[13:17], 2)
        c4 = int(bin[13:17], 2)
        c8 = int(bin[9:17], 2)
        next = copy.deepcopy(state)
        next.regs[15] += 1

        if imm:
            addr = c8
            if opcode[1] == '0':
                val = c4
            else:
                val = (1<<c4)
        else:
            addr = (state.regs[r2] + c4i)&255
            val = state.regs[r3]

        # Simulate instructions
        if m == 'ldr':
            if addr == 2:
                inp = input('Enter keyboard character: ')
                if len(inp) > 0:
                    next.regs[r1] = ord(inp[0])
                else:
                    next.regs[r1] = 0
            else:
                next.regs[r1] = state.mem[addr]
        elif m == 'str':
            if addr == 7:
                print(chr(state.regs[r1]), end='')
            elif addr == 8 and state.regs[r1] == 1:
                print()
            else:
                next.mem[addr] = state.regs[r1]
        elif m == 'mov':
            if opcode == '00100':
                next.regs[r1] = state.regs[r2]
            elif opcode == '00101':
                next.regs[r1] = c8
            next.zero = (next.regs[r1] == 0)
            next.carry = False
            next.negative = bool(next.regs[r1] & 128)
            next.overflow = False
        elif opcode[:4] == '0011':
            # Direct jumps
            if ( m == 'b' or
                (m == 'bz' and state.zero) or (m == 'bnz' and not state.zero) or
                (m == 'bcs' and state.carry) or (m == 'bcc' and not state.carry) or
                (m == 'blt' and (state.overflow != state.negative)) or
                (m == 'bge' and (state.overflow == state.negative))):
                if opcode[-1] == '0':
                    # Uses incremented PC
                    next.regs[15] = (next.regs[r2] + c4i)&255
                else:
                    next.regs[15] = c8
        elif m == 'push':
            if state.regs[14] == -1:
                raise RuntimeError('Stack overflow')
            next.mem[state.regs[14]] =  state.regs[r1]
            next.regs[14] -= 1
        elif m == 'pop' or m == 'ret':
            if state.regs[14] == 255:
                raise RuntimeError('Stack underflow')
            next.regs[r1] = state.mem[state.regs[14]+1]
            next.regs[14] += 1
        elif m == 'call':
            if state.regs[14] == -1:
                raise RuntimeError('Stack overflow')
            next.mem[state.regs[14]] = state.regs[15]+1
            next.regs[15] = c8
            next.regs[14] -= 1
        else:
            # ALU instructions (modify flags)
            next.overflow = 0
            if m == 'add':
                res = state.regs[r2] + val
                next.overflow = bool((~(state.regs[r2] ^ val) & (state.regs[r2] ^ res)) & 128)
            elif m == 'sub':
                res = state.regs[r2] + (256-val)
                next.overflow = bool(( (state.regs[r2] ^ val) & (state.regs[r2] ^ res)) & 128)
            elif m == 'shl':
                res = state.regs[r2] << 1
            elif m == 'shr':
                res = state.regs[r2] >> 1
            elif m == 'and':
                res = state.regs[r2] & val
            elif m == 'orr':
                res = state.regs[r2] | val
            elif m == 'eor':
                res = state.regs[r2] ^ val
            else:
                raise ValueError(f'Unknown opcode {opcode}')

            next.zero = ((res&255) == 0)
            next.carry = bool(res & 256)
            next.negative = bool(res & 128)
            next.regs[r1] = res&255

        return next

    def help(self):
        print("""Available commands:
   h       This help.
   n       Advance to next instruction.
   c       Execute continuously until halted.
   p       Print current state.
   q       Exit simulator.
   rx      Print contents of register x.
   rx = y  Set register x to value y.
   [a]     Print contents of memory address a.
   [a] = y Set memory address a to value y.
""")

    def process(self, mem):
        """Simulate machine code."""
        state = State()
        for i, c in enumerate(mem['data']):
            state.mem[i] = int(c[0], 2)

        quiet = False

        while True:
            # Print current instruction
            bin = mem['code'][state.regs[15]][0]

            if quiet:
                next = copy.deepcopy(self.execute(bin, state))
                if next.regs[15] == state.regs[15]:
                    quiet = False
                state = next
                continue

            _, dis = self.disassembler.process(bin)
            print(f'{state.regs[15]:3}: {bin[0:4]} {bin[4]} {bin[5:9]} {bin[9:13]} {bin[13:17]} ({dis})')

            next = copy.deepcopy(state)

            # Present interface
            cmd = input('>> ').strip()
            if cmd == '' or cmd == 'n':
                # Advance to next instruction
                next = self.execute(bin, state)
            elif cmd == 'c':
                # Execute continuously
                quiet = True
            elif cmd == 'p':
                # Print current state
                print(state)
            elif cmd == 'q':
                # Exit simulator
                return
            elif cmd[0] == 'r':
                # Set register
                tokens = [t.strip() for t in cmd.split('=')]
                if len(tokens[0]) < 2:
                    self.help()
                elif len(tokens) == 1:
                    try:
                        print(f'r{int(tokens[0][1:])} = {state.regs[int(tokens[0][1:])]}')
                    except Exception as e:
                        print(e)
                elif len(tokens) == 2:
                    try:
                        next.regs[int(tokens[0][1:])] = int(tokens[1], 0)&255
                    except Exception as e:
                        print(e)
                else:
                    self.help()
            elif cmd[0] == '[':
                # Set memory address
                tokens = [t.strip() for t in cmd.split('=')]
                if len(tokens[0]) < 2 or tokens[0][0] != '[' or tokens[0][-1] != ']':
                    self.help()
                elif len(tokens) == 1:
                    try:
                        print(f'[{int(tokens[0][1:-1])}] = {state.mem[int(tokens[0][1:-1])]}')
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
            if diff != '':
                print('     ' + diff)
            state = copy.deepcopy(next)

    def run(self, mem, steps=1000):
        """Simulate machine code for a set number of steps and return PC."""
        state = State()
        for i, c in enumerate(mem['data']):
            state.mem[i] = int(c[0], 2)

        for s in range(steps):
            bin = mem['code'][state.regs[15]][0]
            state = copy.deepcopy(self.execute(bin, state))

        return state.regs[15]
