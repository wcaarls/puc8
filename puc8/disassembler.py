"""Disassembler for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

from .instructions import defs

class Disassembler():
    def __init__(self, map=None):
        self.map = map

    """Disassemble machine code back to assembly."""
    def process(self, inst):
        for mnemonic in defs:
            for (opcode, minor, operands) in defs[mnemonic]:
                if opcode != '' and inst[:len(opcode)] == opcode and (minor == '' or inst[-len(minor):] == minor):
                    dis = f'{mnemonic:4} '
                    for i, o in enumerate(operands):
                        istart = len(opcode)+4*i
                        reg = int(inst[istart:istart+4], 2)
                        if o == 'R':
                            dis += f'r{reg}, '
                        elif o == 'A':
                            dis += f'[r{reg}], '
                        elif o == 'B':
                            addr = int(inst[istart:istart+8], 2)
                            if self.map is not None and addr in self.map['data']:
                                dis += f"[@{self.map['data'][addr]}], "
                            else:
                                dis += f'[{addr}], '
                        elif o == '4':
                            val = int(inst[istart:istart+4], 2)
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
