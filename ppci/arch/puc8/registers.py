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
r13 = PUC8Register("r13", num=13)
r14 = PUC8Register("r14", num=14)
fp = PUC8Register("r15", num=15, aka=("fp",))

PUC8Register.registers = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, fp]
num_reg_map = {r.num: r for r in PUC8Register.registers}
alloc_registers = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]

register_classes = [
    RegisterClass(
        "reg",
        [ir.i8, ir.u8, ir.ptr],
        PUC8Register,
        alloc_registers,
    )
]

caller_save = alloc_registers
callee_save = []

#caller_save = []
#callee_save = alloc_registers
