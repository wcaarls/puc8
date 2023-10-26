""" PUC8 instruction definitions.
"""

from ..encoding import Instruction, Operand, Syntax
from ..isa import Relocation, Isa
from ..token import Token, bit_range, Endianness
from .registers import PUC8Register
from . import registers
from math import log2
from .. import effects

isa = Isa()

class PUC8Token(Token):
    class Info:
        size = 32
        endianness=Endianness.BIG,

    opcode = bit_range(13, 17)
    immediate = bit_range(12, 13)
    r1 = bit_range(8, 12)
    r2 = bit_range(4, 8)
    r3 = bit_range(0, 4)
    c4 = bit_range(0, 4)
    c8 = bit_range(0, 8)

class PUC8Instruction(Instruction):
    isa = isa

def make_rrr(mnemonic, opcode, immediate):
    r1 = Operand("r1", PUC8Register, write=True)
    r2 = Operand("r2", PUC8Register, read=True)
    r3 = Operand("r3", PUC8Register, read=True)
    syntax = Syntax([mnemonic, " ", r1, ",", " ", r2, ",", " ", r3])
    patterns = {
        "opcode": opcode,
        "immediate": immediate,
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

def make_rrc(mnemonic, opcode, immediate, addr=False, write=True):
    r1 = Operand("r1", PUC8Register, read = not write, write=write)
    r2 = Operand("r2", PUC8Register, read=True)
    c4 = Operand("c4", int)
    if addr:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", "[", r2, ",", " ", c4, "]"])
    else:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", r2, ",", " ", c4])

    patterns = {
        "opcode": opcode,
        "immediate": immediate,
        "r1": r1,
        "r2": r2,
        "c4": c4,
    }
    members = {
        "tokens": [PUC8Token],
        "r1": r1,
        "r2": r2,
        "c4": c4,
        "syntax": syntax,
        "patterns": patterns,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

def make_rr(mnemonic, opcode, immediate, minor4=0, addr=False, write=True):
    r1 = Operand("r1", PUC8Register, read = not write, write=write)
    r2 = Operand("r2", PUC8Register, read=True)
    if addr:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", "[", r2, "]"])
    else:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", r2])

    patterns = {
        "opcode": opcode,
        "immediate": immediate,
        "r1": r1,
        "r2": r2,
        "c4": minor4,
    }
    members = {
        "tokens": [PUC8Token],
        "r1": r1,
        "r2": r2,
        "syntax": syntax,
        "patterns": patterns,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

def make_r(mnemonic, opcode, immediate, minor8=0, write=True):
    if write:
        r1 = Operand("r1", PUC8Register, write=True)
    else:
        r1 = Operand("r1", PUC8Register, read=True)

    syntax = Syntax([mnemonic, " ", r1])

    patterns = {
        "opcode": opcode,
        "immediate": immediate,
        "r1": r1,
        "c8": minor8
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
    field = "c8"

    def calc(self, sym_value, reloc_value):
        return sym_value

def data_relocations(self):
     if self.label:
         yield Abs8DataRelocation(self.c8)

def make_rc(mnemonic, opcode, immediate, write=True, addr=False, label=False):
    if write:
        r1 = Operand("r1", PUC8Register, write=True)
    else:
        r1 = Operand("r1", PUC8Register, read=True)

    if label:
        c8 = Operand("c8", str)
    else:
        c8 = Operand("c8", int)

    if addr:
        syntax = Syntax([mnemonic, " ", r1, ",", "[", c8, "]"])
    else:
        syntax = Syntax([mnemonic, " ", r1, ",", " ", c8])

    patterns = {
        "opcode": opcode,
        "immediate": immediate,
        "r1": r1,
    }
    if not label:
        patterns["c8"] = c8;
    members = {
        "label": label,
        "tokens": [PUC8Token],
        "r1": r1,
        "c8": c8,
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
    field = "c8"

    def calc(self, sym_value, reloc_value):
        # Imem is fake 32-bit
        return sym_value // 4

def branch_relocations(self):
     if self.label:
         yield Abs8BranchRelocation(self.c8)

def make_c(mnemonic, opcode, immediate, minor4, label=True):
    if label:
        c8 = Operand("c8", str)
    else:
        c8 = Operand("c8", int)

    syntax = Syntax([mnemonic, " ", c8])

    patterns = {
        "opcode": opcode,
        "immediate": immediate,
        "r1": minor4,
    }
    if not label:
        patterns["c8"] = c8;
    members = {
        "label": label,
        "tokens": [PUC8Token],
        "c8": c8,
        "syntax": syntax,
        "patterns": patterns,
        "gen_relocations": branch_relocations,
    }
    return type(mnemonic.title(), (PUC8Instruction,), members)

# Memory instructions:
Ldr   = make_rrc("ldr",   0, 0, addr=True)
LdrC  = make_rc ("ldr",   0, 1, addr=True)
LdrL  = make_rc ("ldr",   0, 1, addr=True, label=True)
Str   = make_rrc("str",   1, 0, write=False, addr=True)
StrC  = make_rc ("str",   1, 1, write=False, addr=True)
StrL  = make_rc ("str",   1, 1, write=False, addr=True, label=True)
MovR  = make_rr ("mov",   2, 0)
Mov   = make_rc ("mov",   2, 1)
MovL  = make_rc ("mov",   2, 1, label=True)
B     = make_c  ("b",     3, 1, 0)
B.effect = lambda self: [effects.Assign(effects.PC, self.c8)]
BZ    = make_c  ("bz",    3, 1, 1)
BNZ   = make_c  ("bnz",   3, 1, 2)
BCS   = make_c  ("bcs",   3, 1, 3)
BCC   = make_c  ("bcc",   3, 1, 4)

# Stack instructions
Push  = make_r  ("push",  4, 0, write=False)
Call  = make_r  ("call",  5, 0, write=False)
CallL = make_c  ("call",  5, 1, 0)
Pop   = make_r  ("pop",   6, 0)

# ALU instructions:
Add   = make_rrr("add",   8, 0)
AddC  = make_rrc("add",   8, 1)
Sub   = make_rrr("sub",   9, 0)
SubC  = make_rrc("sub",   9, 1)
Shl   = make_rrr("shl",  10, 0)
ShlC  = make_rrc("shl",  10, 1)
Shr   = make_rrr("shr",  11, 0)
ShrC  = make_rrc("shr",  11, 1)
And   = make_rrr("and",  12, 0)
AndC  = make_rrc("and",  12, 1)
Orr   = make_rrr("orr",  13, 0)
OrrC  = make_rrc("orr",  13, 1)
EOr   = make_rrr("eor",  14, 0)
EOrC  = make_rrc("eor",  14, 1)

@isa.pattern("reg", "ADDI8(reg, reg)")
@isa.pattern("reg", "ADDU8(reg, reg)")
def pattern_add(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(Add(d, c0, c1))
    return d

@isa.pattern("reg", "ADDI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "ADDU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
def pattern_addc(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(AddC(d, c0, tree[1].value))
    return d

@isa.pattern("reg", "ADDI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "ADDU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
def pattern_addc2(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(AddC(d, c0, tree[0].value))
    return d

@isa.pattern("reg", "SUBI8(reg, reg)")
@isa.pattern("reg", "SUBU8(reg, reg)")
def pattern_sub(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(Sub(d, c0, c1))
    return d

@isa.pattern("reg", "SUBI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBI8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
@isa.pattern("reg", "SUBU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and t[1].value <= 15)
def pattern_subc(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(SubC(d, c0, tree[1].value))
    return d

@isa.pattern("reg", "SUBI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBI8(CONSTI8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
@isa.pattern("reg", "SUBU8(CONSTU8, reg)", condition=lambda t: t[0].value >= 0 and t[0].value <= 15)
def pattern_subc(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(SubC(d, c0, tree[0].value))
    return d

@isa.pattern("reg", "NEGI8(reg, reg)", size=2, cycles=2, energy=2)
def pattern_neg(context, tree, c0):
    d = context.new_reg(PUC8Register)
    zero = context.new_reg(PUC8Register)
    context.emit(Mov(zero, 0))
    context.emit(Sub(d, zero, c0))
    return d

@isa.pattern("reg", "ANDI8(reg, reg)")
@isa.pattern("reg", "ANDU8(reg, reg)")
def pattern_and(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(And(d, c0, c1))
    return d

@isa.pattern("reg", "ORI8(reg, reg)")
@isa.pattern("reg", "ORU8(reg, reg)")
def pattern_or(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(Orr(d, c0, c1))
    return d

@isa.pattern("reg", "XORI8(reg, reg)")
@isa.pattern("reg", "XORU8(reg, reg)")
def pattern_xor(context, tree, c0, c1):
    d = context.new_reg(PUC8Register)
    context.emit(EOr(d, c0, c1))
    return d

@isa.pattern("reg", "MULU8(reg, CONSTI8)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
@isa.pattern("reg", "MULU8(reg, CONSTU8)", condition=lambda t: t[1].value >= 0 and (t[1].value == 0 or log2(t[1].value).is_integer()))
def pattern_mul(context, tree, c0):
    # Multiply with constant is needed for array handling; emulate
    if tree[1].value == 0:
        d = context.new_reg(PUC8Register)
        context.emit(Mov(d, 0))
        return d
    elif tree[1].value == 1:
        return c0

    assert(tree[1].value > 1)
    n = log2(tree[1].value) - 1
    assert(n.is_integer())
    d = context.new_reg(PUC8Register)
    context.emit(ShlC(d, c0, 1))
    for i in range(int(n)):
        context.emit(ShlC(d, d, 1))
    return d

@isa.pattern("reg", "SHLI8(reg, CONSTU8)")
@isa.pattern("reg", "SHLU8(reg, CONSTU8)")
@isa.pattern("reg", "SHLI8(reg, CONSTI8)")
@isa.pattern("reg", "SHLU8(reg, CONSTI8)")
def pattern_shl(context, tree, c0):
    if tree.value == 0:
        return c0

    assert(tree[1].value > 0)
    d = context.new_reg(PUC8Register)
    context.emit(ShlC(d, c0, 1))
    for i in range(tree[1].value-1):
      context.emit(ShlC(d, d, 1))
    return d

@isa.pattern("reg", "SHRI8(reg, CONSTU8)")
@isa.pattern("reg", "SHRU8(reg, CONSTU8)")
@isa.pattern("reg", "SHRI8(reg, CONSTI8)")
@isa.pattern("reg", "SHRU8(reg, CONSTI8)")
def pattern_shr(context, tree, c0):
    if tree.value == 0:
        return c0

    assert(tree[1].value > 0)
    d = context.new_reg(PUC8Register)
    context.emit(ShrC(d, c0, 1))
    for i in range(tree[1].value-1):
      context.emit(ShrC(d, d, 1))
    return d

@isa.pattern("reg", "FPRELU8")
def pattern_fprelu8(context, tree):
    # First stack element is at fp. Previous fp is at fp+1
    if tree.value.offset != -1:
        d = context.new_reg(PUC8Register)
        if tree.value.offset < -16:
            context.emit(Mov(d, tree.value.offset+1))
            context.emit(Add(d, registers.fp, d))
            return d
        else:
            context.emit(SubC(d, registers.fp, -(tree.value.offset+1)))
            return d
    else:
        return registers.fp

@isa.pattern("stm", "STRI8(reg, reg)", energy=2)
@isa.pattern("stm", "STRU8(reg, reg)", energy=2)
def pattern_str(context, tree, c0, c1):
    context.emit(Str(c1, c0, 0))

@isa.pattern("stm", "STRI8(ADDU8(reg, CONSTI8), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("stm", "STRU8(ADDU8(reg, CONSTI8), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("stm", "STRI8(ADDU8(reg, CONSTU8), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("stm", "STRU8(ADDU8(reg, CONSTU8), reg)", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
def pattern_strrc(context, tree, c0, c1):
    context.emit(Str(c1, c0, tree[0][1].value))

@isa.pattern("stm", "STRI8(FPRELU8, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("stm", "STRU8(FPRELU8, reg)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
def pattern_strfp(context, tree, c0):
    context.emit(Str(c0, registers.fp, tree[0].value.offset+1))

@isa.pattern("stm", "STRI8(CONSTU8, reg)", energy=2)
@isa.pattern("stm", "STRU8(CONSTU8, reg)", energy=2)
def pattern_strc(context, tree, c0):
    context.emit(StrC(c0, tree[0].value))

@isa.pattern("stm", "STRI8(LABEL, reg)", energy=2)
@isa.pattern("stm", "STRU8(LABEL, reg)", energy=2)
def pattern_strl(context, tree, c0):
    context.emit(StrL(c0, tree[0].value))

@isa.pattern("reg", "LDRI8(reg)", energy=2)
@isa.pattern("reg", "LDRU8(reg)", energy=2)
def pattern_ldr(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(Ldr(d, c0, 0))
    return d

@isa.pattern("reg", "LDRI8(ADDU8(reg, CONSTI8))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("reg", "LDRU8(ADDU8(reg, CONSTI8))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("reg", "LDRI8(ADDU8(reg, CONSTU8))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
@isa.pattern("reg", "LDRU8(ADDU8(reg, CONSTU8))", energy=2, condition=lambda t: t[0][1].value >= -8 and t[0][1].value <= 7)
def pattern_ldrrc(context, tree, c0):
    d = context.new_reg(PUC8Register)
    context.emit(Ldr(d, c0, tree[0][1].value))
    return d

@isa.pattern("reg", "LDRI8(FPRELU8)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
@isa.pattern("reg", "LDRU8(FPRELU8)", energy=2, condition=lambda t: t[0].value.offset >= -9 and t[0].value.offset <= 6)
def pattern_ldrfp(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(Ldr(d, registers.fp, tree[0].value.offset+1))
    return d

@isa.pattern("reg", "LDRI8(CONSTU8)", energy=2)
@isa.pattern("reg", "LDRU8(CONSTU8)", energy=2)
def pattern_ldrc(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(LdrC(d, tree[0].value))
    return d

@isa.pattern("reg", "LDRI8(LABEL)", energy=2)
@isa.pattern("reg", "LDRU8(LABEL)", energy=2)
def pattern_ldrl(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(LdrL(d, tree[0].value))
    return d

# Misc patterns:
@isa.pattern("reg", "CONSTI8")
@isa.pattern("reg", "CONSTU8")
def pattern_mov(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(Mov(d, tree.value))
    return d

@isa.pattern("stm", "MOVI8(reg)")
@isa.pattern("stm", "MOVU8(reg)")
def pattern_movr(context, tree, c0):
    d = tree.value
    context.emit(MovR(d, c0, ismove=True))

@isa.pattern("reg", "REGI8", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU8", size=0, cycles=0, energy=0)
def pattern_reg(context, tree):
    return tree.value

@isa.pattern("reg", "I8TOU8(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "U8TOI8(reg)", size=0, cycles=0, energy=0)
def pattern_cast(context, tree, c0):
    return c0

@isa.pattern("reg", "LABEL")
def pattern_label(context, tree):
    d = context.new_reg(PUC8Register)
    context.emit(MovL(d, tree.value))
    return d

# Jumping around:
@isa.pattern("stm", "JMP")
def pattern_jmp(context, tree):
    tgt = tree.value
    context.emit(B(tgt.name, jumps=[tgt]))

@isa.pattern("stm", "CJMPI8(reg, reg)", size=3, cycles=2, energy=2, condition=lambda t: t.value[0] == "==" or t.value[0] == "!=")
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

@isa.pattern("stm", "CJMPU8(reg, reg)", size=3, cycles=2, energy=2)
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

@isa.pattern("stm", "CJMPI8(reg, CONSTI8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTI8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPI8(reg, CONSTU8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
@isa.pattern("stm", "CJMPU8(reg, CONSTU8)", size=3, cycles=2, energy=2, condition=lambda t: t[1].value == 0 and (t.value[0] == "==" or t.value[0] == "!="))
def pattern_cjmp0(context, tree, c0):
    # Special case for comparison to 0 (more efficient)
    op, yes_label, no_label = tree.value
    opnames = {
        "==": BZ,
        "!=": BNZ,
    }
    Bop = opnames[op]
    d = context.new_reg(PUC8Register)
    context.emit(MovR(c0, c0));
    jmp_ins = B(no_label.name, jumps=[no_label])
    context.emit(Bop(yes_label.name, jumps=[yes_label, jmp_ins]))
    context.emit(jmp_ins)
