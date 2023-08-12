#!/usr/bin/env python3
import io

from ppci.api import asm, cc, link
from ppci.binutils.layout import LayoutLoader
from ppci.common import DiagnosticsManager
from ppci.binutils.outstream import BinaryOutputStream
from ppci.arch import get_arch
from ppci.binutils.objectfile import ObjectFile, Image, merge_memories

from disassembler import Disassembler

def assemble(src, section):
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
    stdobj = assemble(io.StringIO("global main\ncall main\nloop: b loop"), "reset")

    obj = cc(src, 'puc8', opt_level=opt_level)

    layout = LayoutLoader().load_layout(io.StringIO("""
    ENTRY(main)

    MEMORY rom LOCATION=0 SIZE=0x100 {
        SECTION(reset)
        SECTION(code)
    }
    MEMORY ram LOCATION=0x10 SIZE=0xf0 {
        SECTION(data)
    }
    """))

    obj = link([obj, stdobj], layout=layout)
    
    return obj

def mapaddr(obj):
    addrmap = {"code": {}, "data": {}}
    sz = 0
    for s in obj.symbols:
        addr = s.value + obj.get_section(s.section).address
        if s.section in addrmap and (s.binding == "global" or not addr in addrmap[s.section]):
            addrmap[s.section][addr] = s.name
            sz = max(sz, len(s.name))
            
    return addrmap

def disasm(obj):
    mem = {"code": [], "data": []}
    
    addrmap = mapaddr(obj)
    disasm = Disassembler(addrmap)
    
    sz = 0
    for s in addrmap:
        for a in addrmap[s]:
            sz = max(sz, len(addrmap[s][a]))

    rom = obj.get_image("rom").sections[0].data + obj.get_image("rom").sections[1].data
    ram = obj.get_image("ram").sections[0].data
    
    for i in range(len(rom)):
        if i%2==0:
            inst = f"{rom[i]:08b}{rom[i+1]:08b}"
            dis = disasm.process(inst)[1]
            
            if i in addrmap["code"]:
                dis = f"{addrmap['code'][i]}:{' '*(sz-len(addrmap['code'][i]))} {dis}"
            else:
                dis = f"{' ':{sz}}  {dis}"
            
            mem['code'].append((inst, dis))

    for i in range(obj.get_section("data").address):
        mem['data'].append(("00000000", ""))
        
    for i in range(len(ram)):
        dis = f".db  {ram[i]:d}"
            
        if i in addrmap["data"]:
            dis = f"{addrmap['data'][i]}:{' '*(sz-len(addrmap['data'][i]))} {dis}"
        else:
            dis = f"{' ':{sz}}  {dis}"
            
        mem['data'].append((f"{ram[i]:08b}", dis))

    return mem
