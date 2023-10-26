""" Define PUC8 architecture """

from ... import ir
from ...binutils.assembler import BaseAssembler
from ..arch import Architecture
from ..arch_info import ArchInfo, TypeInfo
from ..generic_instructions import Label, Alignment, RegisterUseDef
from ..runtime import get_runtime_files
from . import instructions, registers
from ..data_instructions import data_isa

class PUC8Arch(Architecture):
    """ PUC8 architecture """

    name = "puc8"

    def __init__(self, options=None):
        super().__init__(options=options)
        self.info = ArchInfo(
            type_infos={
                ir.i8: TypeInfo(1, 1),
                ir.u8: TypeInfo(1, 1),
                ir.i16: TypeInfo(1, 1),
                ir.u16: TypeInfo(1, 1),
                ir.f32: TypeInfo(1, 1),
                ir.f64: TypeInfo(1, 1),
                "int": ir.i8,
                "long": ir.i8,
                "ptr": ir.u8,
                ir.ptr: ir.u8,
            },
            register_classes=registers.register_classes,
        )

        self.isa = instructions.isa + data_isa

        self.assembler = BaseAssembler()
        self.assembler.gen_asm_parser(self.isa)

    def get_runtime(self):
        """ Retrieve the runtime for this target """
        return asm(io.StringIO(""), self)

    def determine_arg_locations(self, arg_types):
        arg_locs = []
        int_regs = [registers.r12, registers.r11, registers.r10, registers.r9]
        for arg_type in arg_types:
            # Determine register:
            if arg_type in [
                ir.i8,
                ir.u8,
                ir.ptr,
            ]:
                reg = int_regs.pop(0)
            else:  # pragma: no cover
                raise NotImplementedError(str(arg_type))
            arg_locs.append(reg)
        return arg_locs

    def determine_rv_location(self, ret_type):
        """ return value in r0 """
        if ret_type in [ir.i8, ir.u8, ir.ptr]:
            rv = registers.r0
        else:  # pragma: no cover
            raise NotImplementedError(str(ret_type))
        return rv

    def gen_prologue(self, frame):
        """ Returns prologue instruction sequence """
        # Label indication function:
        yield Label(frame.name)

        # Callee save registers:
        for reg in self.get_callee_saved(frame):
            yield instructions.Push(reg)

        # Allocate stack and set frame pointer
        if frame.stacksize > 0:
            yield instructions.Push(registers.fp)
            yield self.move(registers.fp, registers.sp)

            ss = frame.stacksize
            while ss > 0:
                yield instructions.SubC(registers.sp, registers.sp, min(ss, 15))
                ss -= 15

    def gen_epilogue(self, frame):
        """ Return epilogue sequence """
        # Restore stack and frame pointers
        if frame.stacksize > 0:
            ss = frame.stacksize
            while ss > 0:
                yield instructions.AddC(registers.sp, registers.sp, min(ss, 15))
                ss -= 15

            yield instructions.Pop(registers.fp)

        # Pop save registers back:
        for reg in reversed(self.get_callee_saved(frame)):
            yield instructions.Pop(reg)

        # Return
        yield instructions.Pop(registers.pc)

    def get_callee_saved(self, frame):
        saved_registers = []
        for reg in registers.callee_save:
            if frame.is_used(reg, self.info.alias):
                saved_registers.append(reg)
        return saved_registers

    def gen_call(self, frame, label, args, rv):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)

        arg_regs = []
        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, registers.PUC8Register):
                arg_regs.append(arg_loc)
                yield self.move(arg_loc, arg)
            else:  # pragma: no cover
                raise NotImplementedError("Parameters in memory not impl")

        yield RegisterUseDef(uses=arg_regs)

        yield instructions.CallL(label, clobbers=registers.caller_save)

        if rv:
            retval_loc = self.determine_rv_location(rv[0])
            yield RegisterUseDef(defs=(retval_loc,))
            yield self.move(rv[1], retval_loc)

    def gen_function_enter(self, args):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)

        arg_regs = set(
            l for l in arg_locs if isinstance(l, registers.PUC8Register)
        )
        yield RegisterUseDef(defs=arg_regs)

        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, registers.PUC8Register):
                yield self.move(arg, arg_loc)
            else:  # pragma: no cover
                raise NotImplementedError("Parameters in memory not impl")

    def gen_function_exit(self, rv):
        live_out = set()
        if rv:
            retval_loc = self.determine_rv_location(rv[0])
            yield self.move(retval_loc, rv[1])
            live_out.add(retval_loc)
        yield RegisterUseDef(uses=live_out)

    def move(self, dst, src):
        return instructions.MovR(dst, src, ismove=True)
