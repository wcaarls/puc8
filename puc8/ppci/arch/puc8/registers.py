""" Description of mips registers """

from ..registers import Register, RegisterClass
from ... import ir


class PUC8Register(Register):
    bitsize = 8

    @classmethod
    def from_num(cls, num):
        return num_reg_map[num]

r0 = PUC8Register("r0", num=0)
r1 = PUC8Register("r1", num=1)
r2 = PUC8Register("r2", num=2)
r3 = PUC8Register("r3", num=3)
r4 = PUC8Register("r4", num=4)
r5 = PUC8Register("r5", num=5)
r6 = PUC8Register("r6", num=6)
r7 = PUC8Register("r7", num=7)
r8 = PUC8Register("r8", num=8)
r9 = PUC8Register("r9", num=9)
r10 = PUC8Register("r10", num=10)
r11 = PUC8Register("r11", num=11)
r12 = PUC8Register("r12", num=12)
fp = PUC8Register("r13", num=13, aka=("fp",))
sp = PUC8Register("r14", num=14, aka=("sp",))
pc = PUC8Register("r15", num=15, aka=("pc",))

PUC8Register.registers = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, fp, sp, pc]
num_reg_map = {r.num: r for r in PUC8Register.registers}
alloc_registers = [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12]

register_classes = [
    RegisterClass(
        "reg",
        [ir.i8, ir.u8, ir.ptr],
        PUC8Register,
        alloc_registers,
    )
]

caller_save = [r0, r1, r2, r3, r4, r9, r10, r11, r12]
callee_save = [r5, r6, r7, r8]
