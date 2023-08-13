""" PUC8 instruction definitions.
"""

from ..encoding import Instruction, Operand, Syntax
from ..isa import Relocation, Isa
from ..token import Token, bit_range, Endianness
from .registers import PUC8Register
from . import registers
from math import log2

isa = Isa()

class PUC8Token(Token):
    class Info:
        size = 16
        endianness=Endianness.BIG,

    opcode = bit_range(12, 16)
    minor = bit_range(0, 4)
    minor2 = bit_range(4, 8)
    minor3 = bit_range(8, 12)
    r1 = bit_range(8, 12)
    r2 = bit_range(4, 8)
    r3 = bit_range(0, 4)
    cd = bit_range(0, 8)
    cb = bit_range(4, 12)

class PUC8Instruction(Instruction):
    isa = isa

def make_rrr(mnemonic, opcode):
    r1 = Operand("r1", PUC8Register, write=True)
    r2 = Operand("r2", PUC8Register, read=True)
    r3 = Operand("r3", PUC8Register, read=True)
    syntax = Syntax([mnemonic, " ", r1, ",", " ", r2, ",", " ", r3])
    patterns = {
        "opcode": opcode,
        "r1": r1,
        "r2": r2,
        "r3": r3,
    }
    members = {
        "tokens": [PUC8Token],
        "r1": r1,
        "r2": r2,
        "r3": r3,
        "syntax": syntax,
        "patterns": patterns,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

def make_rr(mnemonic, opcode, minor, write=True, addr=False):
    if write:
        r1 = Operand("r1", PUC8Register, write=True)
    else:
        r1 = Operand("r1", PUC8Register, read=True)
    
    r2 = Operand("r2", PUC8Register, read=True)
    if addr:
        syntax = Syntax([mnemonic, " ", r1, ",", "[", r2, "]"])
    else:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", r2])
    
    patterns = {
        "opcode": opcode,
        "r1": r1,
        "r2": r2,
        "minor": minor,
    }
    members = {
        "tokens": [PUC8Token],
        "r1": r1,
        "r2": r2,
        "syntax": syntax,
        "patterns": patterns,
        "ismove": mnemonic == "mov",
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

def make_r(mnemonic, opcode, minor, minor2=0, write=True):
    if write:
        r1 = Operand("r1", PUC8Register, write=True)
    else:
        r1 = Operand("r1", PUC8Register, read=True)
    
    syntax = Syntax([mnemonic, " ", r1])
    
    patterns = {
        "opcode": opcode,
        "r1": r1,
        "minor": minor,
        "minor2": minor2,
    }
    members = {
        "tokens": [PUC8Token],
        "r1": r1,
        "syntax": syntax,
        "patterns": patterns,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

@isa.register_relocation
class Abs8DataRelocation(Relocation):
    """ Apply 8 bit data relocation """

    name = "abs8data"
    token = PUC8Token
    field = "cd"

    def calc(self, sym_value, reloc_value):
        return sym_value

def data_relocations(self):
     if self.label:
         yield Abs8DataRelocation(self.cd)

def make_rc(mnemonic, opcode, write=True, addr=False, label=False):
    if write:
        r1 = Operand("r1", PUC8Register, write=True)
    else:
        r1 = Operand("r1", PUC8Register, read=True)
    
    if label:
        cd = Operand("cd", str)
    else:
        cd = Operand("cd", int)
    
    if addr:
        syntax = Syntax([mnemonic, " ", r1, ",", "[", cd, "]"])
    else:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", cd])
    
    patterns = {
        "opcode": opcode,
        "r1": r1,
    }
    if not label:
        patterns["cd"] = cd;
    members = {
        "label": label,
        "tokens": [PUC8Token],
        "r1": r1,
        "cd": cd,
        "syntax": syntax,
        "patterns": patterns,
        "gen_relocations": data_relocations,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)


@isa.register_relocation
class Abs8BranchRelocation(Relocation):
    """ Apply 8 bit branch relocation """

    name = "abs8branch"
    token = PUC8Token
    field = "cb"

    def calc(self, sym_value, reloc_value):
        # Imem is 16-bit
        return sym_value // 2

def branch_relocations(self):
     if self.label:
         yield Abs8BranchRelocation(self.cb)

def make_c(mnemonic, opcode, minor, label=True):
    if label:
        cb = Operand("cb", str)
    else:
        cb = Operand("cb", int)
    
    syntax = Syntax([mnemonic, " ", cb])
    
    patterns = {
        "opcode": opcode,
        "minor": minor,
    }
    if not label:
        patterns["cb"] = cb;
    members = {
        "label": label,
        "tokens": [PUC8Token],
        "cb": cb,
        "syntax": syntax,
        "patterns": patterns,
        "gen_relocations": branch_relocations,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

def make_x(mnemonic, opcode, minor, minor2=0, minor3=0):
    syntax = Syntax([mnemonic])
    
    patterns = {
        "opcode": opcode,
        "minor": minor,
        "minor2": minor2,
        "minor3": minor3,
    }
    members = {
        "tokens": [PUC8Token],
        "syntax": syntax,
        "patterns": patterns,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

# Memory instructions:
LdrA = make_rr("ldr", 0, 0, addr=True)
LdrB = make_rc("ldr", 1, addr=True, label=True)
LdrBI = make_rc("ldr", 1, addr=True)
LdrC = make_rc("ldr", 2, label=True)
LdrCI = make_rc("ldr", 2)
StrA = make_rr("str", 3, 0, write=False, addr=True)
StrB = make_rc("str", 4, write=False, addr=True, label=True)
StrBI = make_rc("str", 4, write=False, addr=True)
Push = make_r("push", 5, 0, write=False)
Pop = make_r("pop", 5, 1)
LdSP = make_r("ldsp", 5, 2)
StSP = make_r("stsp", 5, 3, write=False)

# ALU2 instructions:
Mov = make_rr("mov", 6, 0)
Mvn = make_rr("mvn", 6, 1)
Neg = make_rr("neg", 6, 2)
Inc = make_rr("inc", 6, 3)
Dec = make_rr("dec", 6, 4)
LSL = make_rr("lsl", 6, 5)
LSR = make_rr("lsr", 6, 6)
ROL = make_rr("rol", 6, 7)
ROR = make_rr("ror", 6, 8)

# ALU3 instructions:
Add = make_rrr("add", 7)
Adc = make_rrr("adc", 8)
Sub = make_rrr("sub", 9)
Sbc = make_rrr("sbc", 10)
And = make_rrr("and", 11)
Orr = make_rrr("orr", 12)
EOr = make_rrr("eor", 13)

# Branch instructions
B = make_c("b", 14, 0)
BZ = make_c("bz", 14, 1)
BNZ = make_c("bnz", 14, 2)
BCS = make_c("bcs", 14, 3)
BCC = make_c("bcc", 14, 4)
#BC = make_r("bx", 15, 0, write=False)
Call = make_c("call", 15, 1)
Ret = make_x("ret", 15, 2)

@isa.pattern("reg", "ADDI8(reg, reg)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "ADDU8(reg, reg)", size=2, cycles=1, energy=1)
def pattern_add(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(Add(d, c0, c1))
    return d

@isa.pattern("reg", "SUBU8(reg, reg)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "SUBI8(reg, reg)", size=2, cycles=1, energy=1)
def pattern_sub(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(Sub(d, c0, c1))
    return d

@isa.pattern("reg", "NEGI8(reg, reg)", size=2, cycles=1, energy=1)
def pattern_neg(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(Neg(d, c0))
    return d

@isa.pattern("reg", "ANDI8(reg, reg)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "ANDU8(reg, reg)", size=2, cycles=1, energy=1)
def pattern_and(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(And(d, c0, c1))
    return d

@isa.pattern("reg", "ORI8(reg, reg)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "ORU8(reg, reg)", size=2, cycles=1, energy=1)
def pattern_or(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(Orr(d, c0, c1))
    return d

@isa.pattern("reg", "XORI8(reg, reg)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "XORU8(reg, reg)", size=2, cycles=1, energy=1)
def pattern_xor(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(EOr(d, c0, c1))
    return d

@isa.pattern("reg", "MULU8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU8(reg, CONSTU8)")
def pattern_mul(context, tree, c0):
    # Multiply with constant is needed for array handling; emulate
    if tree[1].value == 0:
        d = context.new_reg(PUC8Register)
        context.emit(LdrCI(d, 0))
        return d
    elif tree[1].value == 1:
        return c0
       
    assert(tree[1].value > 1)
    n = log2(tree[1].value) - 1
    assert(n.is_integer())
    d = context.new_reg(PUC8Register)
    context.emit(LSL(d, c0))
    for i in range(int(n)):
        context.emit(LSL(d, d))
    return d

@isa.pattern("reg", "SHLI8(reg, CONSTU8)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "SHLU8(reg, CONSTU8)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "SHLI8(reg, CONSTI8)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "SHLU8(reg, CONSTI8)", size=2, cycles=1, energy=1)
def pattern_shl(context, tree, c0):
    if tree.value == 0:
        return c0
        
    assert(tree[1].value > 0)
    d = context.new_reg(PUC8Register)
    context.emit(LSL(d, c0))
    for i in range(tree[1].value-1):
      context.emit(LSL(d, d))
    return d

@isa.pattern("reg", "SHRI8(reg, CONSTU8)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "SHRU8(reg, CONSTU8)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "SHRI8(reg, CONSTI8)", size=2, cycles=1, energy=1)
@isa.pattern("reg", "SHRU8(reg, CONSTI8)", size=2, cycles=1, energy=1)
def pattern_shr(context, tree, c0):
    if tree.value == 0:
        return c0
        
    assert(tree[1].value > 0)
    d = context.new_reg(PUC8Register)
    context.emit(LSR(d, c0))
    for i in range(tree[1].value-1):
      context.emit(LSR(d, d))
    return d

# Memory patterns:
@isa.pattern("mem", "reg", size=0, cycles=0, energy=0)
def pattern_reg_as_mem(context, tree, c0):
    return c0

@isa.pattern("reg", "FPRELU8", size=6, cycles=3, energy=5)
def pattern_fprelu8(context, tree):
    # First stack element is at fp. Previous fp is at fp+1
    if tree.value.offset != -1:
        d = context.new_reg(PUC8Register)
        context.emit(LdrCI(d, tree.value.offset+1))
        context.emit(Add(d, d, registers.fp))
        return d
    else:
        return registers.fp

@isa.pattern("stm", "STRI8(reg, reg)", size=2, cycles=1, energy=2)
@isa.pattern("stm", "STRU8(reg, reg)", size=2, cycles=1, energy=2)
def pattern_stra(context, tree, c0, c1):
    context.emit(StrA(c1, c0))
    
@isa.pattern("stm", "STRI8(CONSTU8, reg)", size=2, cycles=1, energy=2)
@isa.pattern("stm", "STRU8(CONSTU8, reg)", size=2, cycles=1, energy=2)
def pattern_strbi(context, tree, c0):
    context.emit(StrBI(c0, tree[0].value))
    
@isa.pattern("stm", "STRI8(LABEL, reg)", size=2, cycles=1, energy=2)
@isa.pattern("stm", "STRU8(LABEL, reg)", size=2, cycles=1, energy=2)
def pattern_strbi(context, tree, c0):
    context.emit(StrB(c0, tree[0].value))
    
@isa.pattern("reg", "LDRI8(reg)", size=2, cycles=1, energy=2)
@isa.pattern("reg", "LDRU8(reg)", size=2, cycles=1, energy=2)
def pattern_ldra(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(LdrA(d, c0))
    return d

@isa.pattern("reg", "LDRI8(mem)", size=2, cycles=1, energy=2)
@isa.pattern("reg", "LDRU8(mem)", size=2, cycles=1, energy=2)
def pattern_ldrb(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(LdrB(d, tree.value))
    return d

@isa.pattern("reg", "LDRI8(CONSTU8)", size=2, cycles=1, energy=2)
@isa.pattern("reg", "LDRU8(CONSTU8)", size=2, cycles=1, energy=2)
def pattern_ldrbi(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(LdrBI(d, tree[0].value))
    return d

@isa.pattern("reg", "LDRI8(LABEL)", size=2, cycles=1, energy=2)
@isa.pattern("reg", "LDRU8(LABEL)", size=2, cycles=1, energy=2)
def pattern_ldrbi(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(LdrB(d, tree[0].value))
    return d

@isa.pattern("reg", "CONSTI8", size=2, cycles=1, energy=1)
@isa.pattern("reg", "CONSTU8", size=2, cycles=1, energy=1)
def pattern_ldrc(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(LdrCI(d, tree.value))
    return d

# Misc patterns:
@isa.pattern("stm", "MOVI8(reg)", size=2, cycles=1, energy=1)
@isa.pattern("stm", "MOVU8(reg)", size=2, cycles=1, energy=1)
def pattern_mov(context, tree, c0):
    d = tree.value
    context.emit(Mov(d, c0))

@isa.pattern("reg", "REGI8", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU8", size=0, cycles=0, energy=0)
def pattern_reg(context, tree):
    return tree.value

@isa.pattern("reg", "I8TOU8(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "U8TOI8(reg)", size=0, cycles=0, energy=0)
def pattern_cast(context, tree, c0):
    return c0

@isa.pattern("reg", "LABEL", size=2, cycles=2, energy=1)
def pattern_label(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(LdrC(d, tree.value))
    return d

# Jumping around:
@isa.pattern("stm", "JMP")
def pattern_jmp(context, tree):
    tgt = tree.value
    context.emit(B(tgt.name, jumps=[tgt]))

@isa.pattern("stm", "CJMPI8(reg, reg)", condition=lambda t: t.value[0] == "==" or t.value[0] == "!=")
def pattern_cjmpi(context, tree, c0, c1):
    op, yes_label, no_label = tree.value
    opnames = {
        "==": BZ,
        "!=": BNZ,
    }
    Bop = opnames[op]
    d = context.new_reg(PUC8Register)
    context.emit(Sub(d, c0, c1));
    jmp_ins = B(no_label.name, jumps=[no_label])
    context.emit(Bop(yes_label.name, jumps=[yes_label, jmp_ins]))
    context.emit(jmp_ins)

@isa.pattern("stm", "CJMPU8(reg, reg)")
def pattern_cjmpu(context, tree, c0, c1):
    op, yes_label, no_label = tree.value
    opnames = {
        "==": (BZ, False),
        "!=": (BNZ, False),
        "<": (BCC, False),
        ">": (BCC, True),
        "<=": (BCS, True),
        ">=": (BCS, False),
    }
    Bop, swap = opnames[op]
    d = context.new_reg(PUC8Register)
    if swap:
        context.emit(Sub(d, c1, c0));
    else:
        context.emit(Sub(d, c0, c1));
    jmp_ins = B(no_label.name, jumps=[no_label])
    context.emit(Bop(yes_label.name, jumps=[yes_label, jmp_ins]))
    context.emit(jmp_ins)

@isa.pattern("stm", "CJMPI8(reg, CONSTI8)", condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTI8)", condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI8(reg, CONSTU8)", condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTU8)", condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
def pattern_cjmp0(context, tree, c0):
    # Special case for comparison to 0 (more efficient)
    op, yes_label, no_label = tree.value
    opnames = {
        "==": BZ,
        "!=": BNZ,
    }
    Bop = opnames[op]
    d = context.new_reg(PUC8Register)
    context.emit(Mov(c0, c0));
    jmp_ins = B(no_label.name, jumps=[no_label])
    context.emit(Bop(yes_label.name, jumps=[yes_label, jmp_ins]))
    context.emit(jmp_ins)
