"""C compiler for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

from io import StringIO

from .ppci.lang.c import c_to_ir
from .ppci.api import ir_to_assembly, optimize

def compile(src, opt_level):
    asm = """
.section data
btn: .db 0
enc: .db 0
kdr: .db 0
udr: .db 0
usr: .db 0
led: .db 0
ssd: .db 0
ldr: .db 0
lcr: .db 0
.org 0x10

.section code
call @main
loop: b @loop
"""
    ir_module = c_to_ir(src, 'puc8')
    optimize(ir_module, level=opt_level)

    ppci_asm = StringIO(ir_to_assembly([ir_module], 'puc8'))

    lbl = ''
    for l in ppci_asm.readlines():
        l = l.lstrip().rstrip()
        if l.startswith('global') or l.startswith('type') or l.startswith('ALIGN'):
            pass
        elif l.endswith(':'):
            if lbl != '':
                lbl += '\n'
            lbl += l + ' '
        elif l.startswith('.byte'):
            asm += lbl + ' .db' + l[5:] + '\n'
            lbl = ''
        elif l.startswith('section'):
            asm += lbl + ' .' + l + '\n'
            lbl = ''
        else:
            asm += lbl + l + '\n'
            lbl = ''

    return asm
