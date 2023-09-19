#!/usr/bin/env python3

"""Assembler for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import sys, argparse

from .assembler import Preprocessor, Assembler
from .simulator import Simulator
from .emitter import emitvhdl

def main():
    parser = argparse.ArgumentParser(description='PUC8 Assembler (c) 2020-2023 Wouter Caarls, PUC-Rio')
    parser.add_argument('file', type=str,
                        help='ASM source file')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file', default='-')
    parser.add_argument('-s', '--simulate', action='store_true',
                        help='Simulate resulting program')
    parser.add_argument('-t', '--test', metavar='N', type=int,
                        help='Simulate for 1000 steps and check whether PC == N')
    parser.add_argument('-E', action='store_true',
                        help='Output preprocessed assembly code')

    args = parser.parse_args()

    pp  = Preprocessor()
    asm = pp.process(args.file)

    if args.output != '-':
        f = open(args.output, 'w')
    else:
        f = sys.stdout

    if args.E:
        # Don't emit machine code, just preprocessed assembly.
        for (idx, label, inst) in asm:
            print(idx + ' ' + (label + ': ' if label != '' else '') + inst, file=f)
    else:
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
            emitvhdl(mem, f)

    if args.output != '-':
        f.close()

if __name__ == '__main__':
    main()
