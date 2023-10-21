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

There are 16 registers. `r14` is `sp`; `r15` is `pc`. The C compiler uses `r13` as `fp`.

## Instructions

All ALU instructions and MOV set flags.

| Group(2) | Op(2)  | Imm(1) | Nibble 1(4)  | Nibble 2(4)  | Nibble 3(4)  | Mnm | Effect | Example |
|---|---|---|---|---|---|---|---|---|
| 00 | 00 | 0 | rd   | rs        | c4i       | LDR  | rd <- [rs + c4i]                        | `ldr  r0, [r1, 4]`    |
| 00 | 00 | 1 | rd   | c8u(7..4) | c8u(3..0) | LDR  | rd <- [c8u]                             | `ldr  r0, [254]`      |
| 00 | 01 | 0 | rs1  | rs2       | c4i       | STR  | [rs2 + c4i] <- rs1                      | `str  r0, [r1, 4]`    |
| 00 | 01 | 1 | rs   | c8u(7..4) | c8u(3..0) | STR  | [c8u] <- rs                             | `str  r0, [254]`      |
| 00 | 10 | 0 | rd   | rs        | 0000      | MOV  | rd <- rs                                | `mov  r0, r1`         |
| 00 | 10 | 1 | rd   | c8u(7..4) | c8u(3..0) | MOV  | rd <- c8u                               | `mov  r0, 254`        |
| 00 | 11 | 0 | cond | rs        | c4i       | B    | if cond then pc <- rs + c4i             | `b    pc, -4`         |
| 00 | 11 | 1 | cond | c8u(7..4) | c8u(3..0) | B    | if cond then pc <- c8u                  | `b    254`            |
| 01 | 00 | 0 | rs   | 0000      | 0000      | PUSH | [sp] <- rs, sp <- sp - 1                | `push r0`             |
| 01 | 01 | 0 | 0000 | rs        | 0000      | CALL | [sp] <- pc + 1, sp <- sp - 1, pc <- rs  | `call r0`             |
| 01 | 01 | 1 | 0000 | c8u(7..4) | c8u(3..0) | CALL | [sp] <- pc + 1, sp <- sp - 1, pc <- c8u | `call 254`            |
| 01 | 10 | 0 | rd   | 0000      | 0000      | POP  | rd <- [sp + 1], sp <- sp + 1            | `pop  r0`             |
| 10 | 00 | 0 | rd   | rs1       | rs2       | ADD  | rd <- rs1 + rs2                         | `add  r0, r1, r2`     |
| 10 | 00 | 1 | rd   | rs        | c4u       | ADD  | rd <- rs + c4u                          | `add  r0, r1, 4`      |
| 10 | 01 | 0 | rd   | rs1       | rs2       | SUB  | rd <- rs1 - rs2                         | `sub  r0, r1, r2`     |
| 10 | 01 | 1 | rd   | rs        | c4u       | SUB  | rd <- rs - c4u                          | `sub  r0, r1, 4`      |
| 10 | 10 | 0 | rd   | rs1       | rs2       | SHL  | rd <- rs1 << rs2                        | `shl  r0, r1, r2`[^1] |
| 10 | 10 | 1 | rd   | rs        | c4u       | SHL  | rd <- rs << c4u                         | `shl  r0, r1, 1`[^1]  |
| 10 | 11 | 0 | rd   | rs1       | rs2       | SHR  | rd <- rs1 >> rs2                        | `shr  r0, r1, r2`[^1] |
| 10 | 11 | 1 | rd   | rs        | c4u       | SHR  | rd <- rs >> c4u                         | `shr  r0, r1, 1`[^1]  |
| 11 | 00 | 0 | rd   | rs1       | rs2       | AND  | rd <- rs1 & rs2                         | `and  r0, r1, r2`     |
| 11 | 00 | 1 | rd   | rs        | c4u       | AND  | rd <- rs & (1<<c4u)                     | `and  r0, r1, 4`      |
| 11 | 01 | 0 | rd   | rs1       | rs2       | ORR  | rd <- rs1 \| rs2                        | `orr  r0, r1, r2`     |
| 11 | 01 | 1 | rd   | rs        | c4u       | ORR  | rd <- rs \| (1<<c4u)                    | `orr  r0, r1, 4`      |
| 11 | 10 | 0 | rd   | rs1       | rs2       | EOR  | rd <- rs1 ^ rs2                         | `eor  r0, r1, r2`     |
| 11 | 10 | 1 | rd   | rs        | c4u       | EOR  | rd <- rs ^ (1<<c4u)                     | `eor  r0, r1, 4`      |

[^1]: May be implemented as a constant shift of 1.

`c4i` can be omitted from the assembly instruction, in which case it is set
to 0.

## Pseudo-instructions

| Pseudo-instruction | Actual instruction |
|---|---|
| `beq` | `bz` |
| `bne` | `bnz` |
| `bhs` | `bcs` |
| `blo` | `bcc` |
| `ret` | `pop pc` |

## Condition codes

| Condition | Meaning |
|---|---|
| 0000 | Unconditional |
| 0001 | Zero flag set |
| 0010 | Zero flag not set |
| 0011 | Carry flag set |
| 0100 | Carry flag not set |

# Assembly language

Assembly statements generally follow the following structure
```asm
[LABEL:] MNEMONIC [OPERAND[, OPERAND]...]
```
The available `MNEMONIC`s can be found in the table above. `OPERAND`s can be registers, constants, or labels. Labels used as operands must be prefixed with `@`:
```asm
loop: jmp @loop
```
When the operand is used as the contents of a memory address, it must be enclosed in square brackets:
```asm
ldr r0, [@inp]
.section data
inp: .db 0
```
Apart from these statements, the assembler recognizes the following directives:

- ```asm
  .include "FILE"
  ```

  Includes a given `FILE`. The path is relative to the file being processed.

- ```asm
  .section SECTION
  ```

  Define into which memory `SECTION` the subsequent code is assembled. Options are `code` and `data`. The default is `code`.

- ```asm
  .org ADDRESS
  ```

  Sets memory `ADDRESS` at which the subsequent code will be assembled.

- ```asm
  .equ LABEL VALUE
  ```

  Creates a `LABEL` for a specific constant `VALUE`. Values may be character constants, e.g. `"c"`

- ```asm
  .db VALUE
  ```

  Inserts a `VALUE` into the instruction stream. The value may be a string constant, e.g. `"Hello, world"`

- ```asm
  .macro NAME
  ; code
  .endmacro
  ```

  Defines a macro. The code inside the macro can use arguments of the form `$0`, `$1`, etc., which are replaced by the actual arguments when the macro is called using `NAME arg0, arg1`. Labels inside the macro that start with an underscore are localized such that the same macro can be called multiple times.

# Installation

```
pip install puc8
```

or

```
git clone https://github.com/wcaarls/puc8
cd puc8
pip install .
```

# Usage

```
usage: as-puc8 [-h] [-o OUTPUT] [-s] [-t N] [-E] file

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
usage: cc-puc8 [-h] [-o OUTPUT] [-s] [-t N] [-S] [-O {0,1,2}] file

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
./cc-puc8 examples/c/hello.c
```

Create assembly from C
```
./cc-puc8 examples/c/hello.c -S
```

Assemble to VHDL code
```
./as-puc8 examples/asm/ps2_lcd.asm
```

Assemble to VHDL package
```
./as-puc8 examples/asm/ps2_lcd.asm -o ps2_lcd.vhdl
```

Simulate resulting C or assembly program
```
./cc-puc8 -O0 examples/c/unittest.c -s
./as-puc8 examples/asm/simple.asm -s
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
