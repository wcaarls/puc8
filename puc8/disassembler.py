"""Disassembler for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

from .instructions import defs

regs = [f'r{reg}' for reg in range(13)]
regs[13:16] = ['fp',  'sp', 'pc']

class Disassembler():
    """Disassemble machine code back to assembly."""
    def __init__(self, map=None):
        self.map = map

    def process(self, inst):
        """Disassemble a single instruction, replacing addresses with labels if a memory map is available."""
        for mnemonic in defs:
            for (opcode, minor, operands) in defs[mnemonic]:
                if opcode != '' and inst[:len(opcode)] == opcode and (minor == '' or inst[-len(minor):] == minor):
                    dis = f'{mnemonic:4} '
                    for i, o in enumerate(operands):
                        istart = len(opcode)+4*i
                        reg = int(inst[istart:istart+4], 2)

                        if o == 'R':
                            dis += f'{regs[reg]}, '
                        elif o == 'A':
                            dis += f'[{regs[reg]}], '
                        elif o == 'B':
                            addr = int(inst[istart:istart+8], 2)
                            if self.map is not None and addr in self.map['data']:
                                dis += f"[@{self.map['data'][addr]}], "
                            else:
                                dis += f'[{addr}], '
                        elif o == '4':
                            val = int(inst[istart:istart+4], 2)
                            if mnemonic == 'ldr' or mnemonic == 'str':
                                if val > 7:
                                    # signed
                                    val -= 16
                                # Convert [addr], offset into [addr, offset]
                                dis = dis[:-3] + f', {val}], '
                            else:
                                dis += f'{val}, '
                        elif o == '8':
                            val = int(inst[istart:istart+8], 2)
                            if self.map is not None and 4*val in self.map['code'] and (mnemonic == 'call' or mnemonic[0] == 'b'):
                                dis += f"@{self.map['code'][4*val]}, "
                            else:
                                dis += f'{val}, '
                    dis = dis[:-2]
                    return mnemonic, dis
        raise ValueError(f'Illegal instruction {inst}')
