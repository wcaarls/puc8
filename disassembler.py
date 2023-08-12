from instructions import defs

class Disassembler():
    def __init__(self, map=None):
        self.map = map

    """Disassemble machine code back to assembly."""
    def process(self, inst):
        for mnemonic in defs:
            for (opcode, minor, operands) in defs[mnemonic]:
                if opcode != '' and inst[:len(opcode)] == opcode and (minor == '' or inst[-len(minor):] == minor):
                    dis = f"{mnemonic:4} "
                    for i, o in enumerate(operands):
                        istart = len(opcode)+4*i
                        reg = int(inst[istart:istart+4], 2)
                        if o == "R":
                            dis += f"r{reg}, "
                        elif o == "A":
                            dis += f"[r{reg}], "
                        elif o == "B":
                            addr = int(inst[istart:istart+8], 2)
                            dis += f"[{addr}], "
                        elif o == "C":
                            val = int(inst[istart:istart+8], 2)
                            if self.map is not None and 2*val in self.map["code"] and (mnemonic == "call" or mnemonic[0] == 'b'):
                                dis += f"@{self.map['code'][2*val]}, "
                            else:
                                dis += f"{val}, "
                    dis = dis[:-2]
                    return mnemonic, dis
        raise ValueError(f"Illegal instruction {inst}")
