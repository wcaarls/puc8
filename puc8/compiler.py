"""C compiler for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import io

from .ppci.api import asm, cc, link, optimize
from .ppci.lang.c import c_to_ir
from .ppci.irutils import to_json
from .ppci.binutils.layout import LayoutLoader
from .ppci.common import DiagnosticsManager
from .ppci.binutils.outstream import BinaryOutputStream
from .ppci.arch import get_arch
from .ppci.binutils.objectfile import ObjectFile, Image, merge_memories

from .disassembler import Disassembler

def assemble(src, section):
    """Assemble into a specific section."""
    diag = DiagnosticsManager()
    march = get_arch('puc8')
    assembler = march.assembler
    obj = ObjectFile(march)
    ostream = BinaryOutputStream(obj)
    ostream.select_section(section)
    assembler.prepare()
    assembler.assemble(src, ostream, diag)
    assembler.flush()
    return obj

def compile(src, opt_level):
    """Compile C source into an object with the correct memory layout."""
    stdobj = assemble(io.StringIO('global main\ncall main\nloop: b loop'), 'reset')

    ioobj = assemble(io.StringIO("""global btn
btn: .byte 0
global enc
enc: .byte 0
global kdr
kdr: .byte 0
global udr
udr: .byte 0
global usr
usr: .byte 0
global led
led: .byte 0
global ssd
ssd: .byte 0
global ldr
ldr: .byte 0
global lcr
lcr: .byte 0"""), 'io')
    obj = cc(src, 'puc8', opt_level=opt_level)

#    ir = c_to_ir(src, 'puc8')
#    optimize(ir, level=opt_level)
#    print(to_json(ir))

    layout = LayoutLoader().load_layout(io.StringIO("""
    ENTRY(main)

    MEMORY rom LOCATION=0 SIZE=0x400 {
        SECTION(reset)
        SECTION(code)
    }
    MEMORY io LOCATION=0x0 SIZE=0x10 {
        SECTION(io)
    }
    MEMORY ram LOCATION=0x10 SIZE=0xf0 {
        SECTION(data)
    }
    """))

    obj = link([obj, stdobj, ioobj], layout=layout)

    return obj

def mapaddr(obj):
    """Create reverse map of addresses to symbols."""
    addrmap = {'code': {}, 'data': {}}
    remap = {'code': 'code', 'reset':'code', 'data':'data', 'io':'data'}
    sz = 0
    for s in obj.symbols:
        section = remap[s.section]
        addr = s.value + obj.get_section(s.section).address
        if section in addrmap and (s.binding == 'global' or not addr in addrmap[section]):
            addrmap[section][addr] = s.name
            sz = max(sz, len(s.name))

    return addrmap

def disasm(obj):
    """Disassemble object into code and data memory contents."""
    mem = {'code': [], 'data': []}

    addrmap = mapaddr(obj)
    disasm = Disassembler(addrmap)

    sz = 0
    for s in addrmap:
        for a in addrmap[s]:
            sz = max(sz, len(addrmap[s][a]))

    rom = obj.get_image('rom').sections[0].data + obj.get_image('rom').sections[1].data
    ram = obj.get_image('ram').sections[0].data

    for i in range(len(rom)):
        if i%4==0:
            inst = f'{rom[i+1]:01b}{rom[i+2]:08b}{rom[i+3]:08b}'
            dis = disasm.process(inst)[1]

            if i in addrmap['code']:
                dis = f"{addrmap['code'][i]}:{' '*(sz-len(addrmap['code'][i]))} {dis}"
            else:
                dis = f"{' ':{sz}}  {dis}"

            mem['code'].append((inst, dis))

    data_addr = obj.get_section('data').address

    for addr in range(data_addr):
        if addr in addrmap['data']:
            mem['data'].append(('00000000', f"{addrmap['data'][addr]}:{' '*(sz-len(addrmap['data'][addr]))} .db  0"))
        else:
            mem['data'].append(('00000000', ''))

    for i in range(len(ram)):
        addr = i + data_addr
        v = ram[i]
        dis = f'.db  {v:d}'
        if v >= 32 and v <= 126:
            dis += ' '*(8-len(dis)) + f"; '{v:c}'"

        if addr in addrmap['data']:
            dis = f"{addrmap['data'][addr]}:{' '*(sz-len(addrmap['data'][addr]))} {dis}"
        else:
            dis = f"{' ':{sz}}  {dis}"

        mem['data'].append((f'{ram[i]:08b}', dis))

    return mem
