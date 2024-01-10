#!/usr/bin/env python3

"""C compiler for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import sys, io, argparse

from .compiler import compile
from .assembler import Preprocessor, Assembler
from .simulator import Simulator
from .emitter import emitasm, emitvhdl

def main():
    parser = argparse.ArgumentParser(description='PUC8 C compiler (c) 2020-2023 Wouter Caarls, PUC-Rio')
    parser.add_argument('file', type=str,
                        help='C source file')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file', default='-')
    parser.add_argument('-s', '--simulate', action='store_true',
                        help='Simulate resulting program')
    parser.add_argument('-t', '--test', metavar='N', type=int,
                        help='Simulate for 1000 steps and check whether PC == N')
    parser.add_argument('-S', action='store_true',
                        help='Output assembly code')
    parser.add_argument('-O', type=int,
                        help='Optimization level', default='2', choices=[0, 1, 2])

    args = parser.parse_args()

    with open(args.file, 'r') as f:
        asm = io.StringIO(compile(f, args.O))

    pp  = Preprocessor()
    asm = pp.process(asm)

    ass = Assembler()
    mem = ass.process(asm)

    if args.simulate or args.test:
        sim = Simulator()
        if args.simulate:
            sim.process(mem)
        else:
            pc = sim.run(mem, 1000)
            if pc != args.test:
                raise RuntimeError('PC after 1000 steps is ' + str(pc) + ', expected ' + str(args.test))
    else:
        if args.output != '-':
            f = open(args.output, 'w')
        else:
            f = sys.stdout

        if args.S:
            # Don't emit machine code, just compiled assembly.
            for (idx, label, inst) in asm:
                print((label + ': ' if label != '' else '') + inst, file=f)
        else:
            emitvhdl(mem, f)

        if args.output != '-':
            f.close()

if __name__ == '__main__':
    main()
