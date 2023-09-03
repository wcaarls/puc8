# PUC8

Assembler and C compiler for the PUC8 processor

Copyright 2020-2023 Wouter Caarls

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Introduction

PUC8 is a microcontroller with 8-bit registers. It is used in the
ENG1448 course of PUC-Rio. This is the assembler and C compiler
infrastructure for it.

# Instruction set architecture

This very simple processor is a Harvard design, with 17-bit instructions and 8-bit data values. Both instruction and data memories have 256 addresses.

## Registers

There are 16 registers. r14 is sp; r15 is pc. The C compiler uses r13 as fp.

## Instructions

T = target register, R = source register 1, S = source register 2, C = immediate value, F = Condition

All ALU instructions and MOV set flags.

| Group | Op  | Immediate | Nibble 1  | Nibble 2  | Nibble 3  | Mnemonic | Effect | Example |
|---|---|---|---|---|---|---|---|---|
| 00 | 00 | 0 | TTTT | RRRR | CCCC | LDR  | Rt <- [Rr + C[^1]] | ldr  r0, [r1, 4] |
| 00 | 00 | 1 | TTTT | CCCC | CCCC | LDR  | Rt <- [C]      | ldr  r0, [254]   |
| 00 | 01 | 0 | TTTT | RRRR | CCCC | STR  | [Rr + C[^1]] <- Rt | str  r0, [r1, 4] |
| 00 | 01 | 1 | TTTT | CCCC | CCCC | STR  | [C] <- Rt      | str  r0, [254]   |
| 00 | 10 | 1 | TTTT | CCCC | CCCC | MOV  | Rt <- C        | mov  r0, 254    |
| 00 | 11 | 1 | FFFF | CCCC | CCCC | B    | if F then pc <- C        | B    254     |
| 01 | 00 | 0 | TTTT | 0000 | 0000 | PUSH | [sp] <- Rt, sp <- sp - 1 | push r0 |
| 01 | 01 | 0 | TTTT | 0000 | 0000 | CALL | [sp] <- pc + 1, sp <- sp - 1, pc <- Rt | call r0 |
| 01 | 01 | 1 | 0000 | CCCC | CCCC | CALL | [sp] <- pc + 1, sp <- sp - 1, pc <- C | call 254 |
| 01 | 10 | 0 | TTTT | 0000 | 0000 | POP  | Rt <- [sp + 1], sp <- sp + 1 | pop r0 |
| 10 | 00 | 0 | TTTT | RRRR | SSSS | ADD  | Rt <- Rr + Rs | add r0, r1, r2 |
| 10 | 00 | 1 | TTTT | RRRR | CCCC | ADD  | Rt <- Rr + C | add r0, r1, 4 |
| 10 | 01 | 0 | TTTT | RRRR | SSSS | SUB  | Rt <- Rr - Rs | sub r0, r1, r2 |
| 10 | 01 | 1 | TTTT | RRRR | CCCC | SUB  | Rt <- Rr - C | sub r0, r1, 4 |
| 10 | 10 | 0 | TTTT | RRRR | SSSS | SHL  | Rt <- Rr << Rs | shl r0, r1, r2[^2] |
| 10 | 10 | 1 | TTTT | RRRR | CCCC | SHL  | Rt <- Rr << C | shl r0, r1, 1[^2] |
| 10 | 11 | 0 | TTTT | RRRR | SSSS | SHR  | Rt <- Rr >> Rs | shr r0, r1, r2[^2] |
| 10 | 11 | 1 | TTTT | RRRR | CCCC | SHR  | Rt <- Rr >> C | shr r0, r1, 1[^2] |
| 11 | 00 | 0 | TTTT | RRRR | SSSS | AND  | Rt <- Rr & Rs | and r0, r1, r2 |
| 11 | 00 | 1 | TTTT | RRRR | CCCC | AND  | Rt <- Rr & (1<<C) | and r0, r1, 4 |
| 11 | 01 | 0 | TTTT | RRRR | SSSS | ORR  | Rt <- Rr \| Rs | orr r0, r1, r2 |
| 11 | 01 | 1 | TTTT | RRRR | CCCC | ORR  | Rt <- Rr \| (1<<C) | orr r0, r1, 4 |
| 11 | 10 | 0 | TTTT | RRRR | SSSS | EOR  | Rt <- Rr ^ Rs | eor r0, r1, r2 |
| 11 | 10 | 1 | TTTT | RRRR | CCCC | EOR  | Rt <- Rr ^ (1<<C) | eor r0, r1, 4 |

[^1]: Signed constant.
[^2]: Only shifts of 0 and 1 are required to be supported.

## Pseudo-instructions

| Pseudo-instruction | Actual instruction | 
|---|---|
| mov r0, r1 | add r0, r1, 0 |
| ret | pop pc |

For an indirect branch, use mov pc, r0.

## Condition codes

| Condition | Meaning |
|---|---|
| 0000 | Unconditional |
| 0001 | Zero flag set |
| 0010 | Zero flag not set |
| 0011 | Carry flag set |
| 0100 | Carry flag not set |

# Usage

```
usage: as.py [-h] [-o OUTPUT] [-s] [-t N] [-E] file

PUC8 Assembler (c) 2020-2023 Wouter Caarls, PUC-Rio

positional arguments:
  file                  ASM source file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -s, --simulate        Simulate resulting program
  -t N, --test N        Simulate for 1000 steps and check whether PC == N
  -E                    Output preprocessed assembly code

```

```
usage: cc.py [-h] [-o OUTPUT] [-s] [-t N] [-S] [-O {0,1,2}] file

PUC8 C compiler (c) 2020-2023 Wouter Caarls, PUC-Rio

positional arguments:
  file                  C source file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -s, --simulate        Simulate resulting program
  -t N, --test N        Simulate for 1000 steps and check whether PC == N
  -S                    Output assembly code
  -O {0,1,2}            Optimization level

```

# Examples

Directly compile C to VHDL
```
./cc.py examples/c/hello.c
```

Create assembly from C
```
./cc.py examples/c/hello.c -S
```

Assemble to VHDL code
```
./as.py examples/asm/ps2_lcd.asm
```

Assemble to VHDL package
```
./as.py examples/asm/ps2_lcd.asm -o ps2_lcd.vhdl
```

Simulate resulting C or assembly program
```
./cc.py -O0 examples/c/testari.c -s
./as.py examples/asm/simple.asm -s
```

# Acknowledgments

The C compiler is based on [PPCI](https://github.com/windelbouwman/ppci).

Copyright (c) 2011-2019, Windel Bouwman

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
