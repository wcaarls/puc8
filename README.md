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

# Usage

```
usage: as.py [-h] [-o OUTPUT] [-s] [-E] file

PUC8 Assembler (c) 2020-2023 Wouter Caarls, PUC-Rio

positional arguments:
  file                  ASM source file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -s, --simulate        Simulate resulting program
  -E                    Output preprocessed assembly code
```

```
usage: cc.py [-h] [-o OUTPUT] [-s] [-S] [-O {0,1,2}] file

PUC8 C compiler (c) 2020-2023 Wouter Caarls, PUC-Rio

positional arguments:
  file                  C source file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -s, --simulate        Simulate resulting program
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
./cc.py examples/c/hello.c -o hello.vhdl
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
