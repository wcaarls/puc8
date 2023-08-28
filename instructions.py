"""Instruction pattern definitions for ENG1448 8-bit processor
   (c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import copy

defs = {'ldr':   [('00000',         '0000', 'RA'),
                  ('00000',             '', 'RA4'),
                  ('00001',             '', 'RB')],
        'str':   [('00010',         '0000', 'RA'),
                  ('00010',             '', 'RA4'),
                  ('00011',             '', 'RB')],
        'mov':   [('00101',             '', 'R8'),
                  ('10001',         '0000', 'RR')], # add Rd, Rr, 0
        'b':     [('001110000',         '', '8')],
        'bz':    [('001110001',         '', '8')],
        'bnz':   [('001110010',         '', '8')],
        'bcs':   [('001110011',         '', '8')],
        'bcc':   [('001110100',         '', '8')],

        'push':  [('01000',     '00000000', 'R')],
        'call':  [('01010',     '00000000', 'R'),
                  ('010110000',         '', '8')],
        'pop':   [('01100',     '00000000', 'R')],
        'ret':   [('011001111', '00000000', '')],   # pop pc

        'add':   [('10000',             '', 'RRR'),
                  ('10001',             '', 'RR4')],
        'sub':   [('10010',             '', 'RRR'),
                  ('10011',             '', 'RR4')],
        'shft':  [('10100',             '', 'RRR'),
                  ('10101',             '', 'RR4')],

        'and':   [('11000',             '', 'RRR')],
        'clr':   [('11001',             '', 'RR4')],
        'orr':   [('11010',             '', 'RRR')],
        'set':   [('11011',             '', 'RR4')],
        'eor':   [('11100',             '', 'RRR')],
        'flip':  [('11101',             '', 'RR4')],

        '.org':  [('',                  '', '8')],
        '.db':   [('',                  '', '8')],
        '.section': [('',               '', 'X')],
        '.equ':  [('',                  '', 'X8')]
       }

defs_dis = copy.deepcopy(defs)
del defs_dis['ret']
