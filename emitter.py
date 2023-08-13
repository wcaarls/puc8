"""ASM and VHDL emitter for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import os

def emitasm(mem, f):
    print(".section code", file=f)
    for c in mem['code']:
        print(c[1], file=f)
    print(".section data", file=f)
    addr = 0
    skipped = False
    for c in mem['data']:
        if c[1] == "":
            skipped = True
        else:
            if skipped == True:
                print(f".org {addr}", file=f)
                skipped = False
            print(c[1], file=f)
        addr += 1

def emitarray(section, f):
    print("(", file=f)
    for l, c in enumerate(section):
        if (c[0] != "0000000000000000" and c[0] != "00000000") or c[1] != "":
            print(f"    {l:3} => \"{c[0]}\", -- {c[1]}", file=f)
    print("     others => \"00000000\");", file=f)

def emitvhdl(mem, f):
    if f.name != '<stdout>':
        pkg = os.path.splitext(os.path.basename(f.name))[0]
        print(
    f"""library ieee;
use ieee.std_logic_1164.all;

package {pkg} is
  type {pkg}ROMT is array(0 to 255) of std_logic_vector(15 downto 0);
  type {pkg}RAMT is array(0 to 255) of std_logic_vector(7 downto 0);

  constant {pkg}_rom: {pkg}ROMT := """, file=f, end='')
    else:
        pkg = ""
        print(f"""  signal rom: ROMT := """, file=f, end='')
    emitarray(mem['code'], f)

    if pkg != "":
        print(f"  constant {pkg}_ram: {pkg}RAMT := ", file=f, end='')
    else:
        print(f"  signal ram: RAMT := ", file=f, end='')
    emitarray(mem['data'], f)

    if pkg != "":
        print(f"end package {pkg};", file=f)
