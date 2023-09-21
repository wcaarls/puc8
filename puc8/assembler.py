"""Assembler for ENG1448 8-bit processor
(c) 2020-2023 Wouter Caarls, PUC-Rio
"""

import sys, os, string, math, re
from .instructions import defs

def _split(s, delim=r'\s'):
    """https://stackoverflow.com/questions/16710076/python-split-a-string-respect-and-preserve-quotes"""
    return re.findall('(?:[^' + delim + r'"]|"(?:\\.|[^"])*")+', s)

def split(s):
    """Splits an instruction into the mnemonic and its operands, respecting string quotations"""
    tokens = _split(s)
    mnemonic = tokens[0]
    operands = _split(''.join(tokens[1:]), ',')

    # Translate MNM Rd, [rR, C] into MNM Rd, [rR], C
    if len(operands) == 3:
        if operands[1][0] == '[' and operands[1][-1] != ']' and operands[2][0] != '[' and operands[2][-1] == ']':
            operands[1] = operands[1] + ']'
            operands[2] = operands[2][0:-1]

    # Translate special-purpose register names
    for i, o in enumerate(operands):
        if o == 'pc':
            operands[i] = 'r15'
        if o == '[pc]':
            operands[i] = '[r15]'
        if o == 'sp':
            operands[i] = 'r14'
        if o == '[sp]':
            operands[i] = '[r14]'
        if o == 'fp':
            operands[i] = 'r13'
        if o == '[fp]':
            operands[i] = '[r13]'
    return mnemonic, operands

class Preprocessor:
    """Assembly preprocessor."""
    def process(self, file):
        """Preprocesses the source, resolving .include and .macro directives,
        and normalizing the instructions."""
        asm, _ = self._preprocess(file)
        return self._reindex(asm)

    def _normalize(self, line):
        """Strips comments and lowers uppercase characters."""
        c = line.find(';')
        if c >= 0:
            line = line[:c]
        line = line.strip()
        return line.lower()

    def _splitlabel(self, line):
        """Split a line into a label and an instruction."""
        c = line.find(':')
        if c >= 0:
            return (line[:c].strip(), line[c+1:].strip())
        else:
            return ('',line)

    def _preprocess(self, file, macros={}):
        """Resolves .include and .macro directives, and splits .db directives into single bytes."""
        asm = []
        macros = macros.copy()
        macro = ''
        nonce = 0
        dir = os.path.dirname(file)

        with open(file, 'r') as f:
            for idx, line in enumerate(f.readlines()):
                idx = idx + 1

                if macro == '':
                    # Emit into main instruction stream
                    code = asm
                else:
                    # Currently processing a macro; emit into that.
                    code = macros[macro]

                (label, inst) = self._splitlabel(self._normalize(line))

                if inst != '':
                    mnemonic, operands = split(inst)
                    if len(operands) > 0:
                        o = operands[0]

                    if mnemonic == '.include':
                        # Include other assembly file.
                        if len(operands) != 1:
                            raise SyntaxError(f'{file}:{idx:3}: Expected string constant')
                        if len(o) < 3 or (o[0] != '"' and o[0] != '\'') or (o[-1] != '"' and o[-1] != '\''):
                            raise SyntaxError(f'{file}:{idx:3}: Malformed string constant {o}')
                        if label != '':
                            code.append((file, idx, label, ''))
                        asm2, macros2 = self._preprocess(os.path.join(dir, o[1:-1]))
                        for line2 in asm2:
                            code.append(line2)
                        macros.update(macros2)
                    elif mnemonic == '.db':
                        # Split .db into single-byte constants
                        tmp = label
                        for o in operands:
                            if o[0] == r'"':
                                if len(o) < 3 or o[-1] != r'"':
                                    raise SyntaxError(f'{file}:{idx:3}: Malformed string constant')
                                for c in o[1:-1]:
                                    code.append((file, idx, tmp, r'.db "' + c + r'"'))
                                    tmp = ''
                            else:
                                code.append((file, idx, tmp, '.db ' + o))
                                tmp = ''
                    elif mnemonic == '.macro':
                        # Create a new macro.
                        if len(operands) != 1:
                            raise SyntaxError(f'{file}:{idx:3}: Missing macro name')
                        elif macro != '':
                            raise SyntaxError(f'{file}:{idx:3}: Cannot nest macro definitions')
                        elif o in defs:
                            raise SyntaxError(f'{file}:{idx:3}: Macro definition {o} shadows mnemonic')
                        elif o in macros:
                            raise SyntaxError(f'{file}:{idx:3}: Redefinition of macro {o}')
                        macro = o
                        macros[macro] = []
                    elif mnemonic == '.endmacro':
                        # Macro finished.
                        macro = ''
                    elif mnemonic in macros:
                        # Macro call. Emit macro contents into main instruction stream.
                        if label != '':
                            code.append((file, idx, label, ''))

                        for (file2, idx2, label2, inst2) in macros[mnemonic]:
                            newinst = ''
                            ii = 0
                            if label2 != '' and label2[0] == '_':
                                # Make label definition local
                                label2 = label2 + str(nonce) + '_'
                            while ii < len(inst2):
                                if inst2[ii] == '$' and ii < len(inst2)-1:
                                    # Resolve macro argument
                                    arg = ord(inst2[ii+1])-ord('0');
                                    if arg >= 0 and arg < len(operands):
                                        newinst = newinst + operands[arg]
                                        ii += 2
                                    else:
                                        raise SyntaxError(f'Invalid argument ${arg} in call to macro {mnemonic}')
                                elif inst2[ii] == '@' and ii < len(inst2)-1 and inst2[ii+1] == '_':
                                    # Make label use local
                                    while ii < len(inst2) and not inst2[ii].isspace() and inst2[ii] != ']':
                                        newinst = newinst + inst2[ii]
                                        ii += 1
                                    newinst = newinst + str(nonce) + '_'
                                else:
                                    newinst = newinst + inst2[ii]
                                    ii += 1

                            code.append((file2, idx2, label2, newinst))
                        nonce += 1
                    else:
                        code.append((file, idx, label, inst))
                elif label != '':
                    code.append((file, idx, label, inst))

        return asm, macros

    def _reindex(self, asm):
        """Combines file and line numbers into a single string."""
        midx = 0
        ml = 0
        for a in asm:
            midx = max(len(a[0]), midx)
            ml = max(ml, a[1])
        if ml > 0:
            ml = math.ceil(math.log10(ml))

        ret = []
        for a in asm:
            ret.append((f'{a[0]:>{midx}}:{a[1]:>{ml}}', a[2], a[3]))
        return ret

class Assembler:
    """Assembler for normalized assembly."""
    def process(self, asm):
        """Emits machine code for normalized assembly."""
        labels = self._pass1(asm)
        return self._pass2(asm, labels)

    def _pass1(self, lines):
        """Calculates label locations."""
        section = 'code'
        labels = {}
        loc = {'code': 0, 'data': 0}

        for (idx, label, inst) in lines:
            if label != '':
                if label in labels:
                    raise SyntaxError(f'{idx}: Redefinition of label {label}')

                labels[label] = loc[section]

            if inst == '':
                continue

            mnemonic, operands = split(inst)

            if mnemonic == '.org':
                if len(operands) < 1:
                    raise SyntaxError(f'{idx}: {mnemonic} directive requires an address argument')
                try:
                    newloc = int(operands[0], 0)
                except:
                    raise ValueError(f'{idx}: Cannot parse {mnemonic} address {operands[0]}')
                if newloc < loc[section]:
                    raise ValueError(f'{idx}: {mnemonic} argument cannot reduce current address {loc}')
                loc[section] = newloc

                # Label before .org points to next instruction
                if label != '':
                    labels[label] = newloc
            elif mnemonic == '.equ':
                # .equ just adds a new label and does not advance instruction
                if len(operands) < 2:
                    raise SyntaxError(f'{idx}: {mnemonic} directive requires 2 arguments')

                labels[operands[0]] = int(operands[1], 0)
            elif mnemonic == '.db' and section == 'code':
                raise ValueError(f'{idx}: Cannot use .db in code section')
            elif mnemonic == '.section':
                section = operands[0]
            else:
                loc[section] += 1

        return labels

    def _resolve(self, lidx, mnemonic, operands, labels):
        """Resolves instruction operands."""
        if not mnemonic in defs:
            raise SyntaxError(f"{lidx}: Unrecognized mnemonic '{mnemonic}'")

        for (opcode, minor, req) in defs[mnemonic]:
            try:
                if len(operands) != len(req):
                    raise SyntaxError(f'{lidx}: {mnemonic} requires {len(req)} operand(s), found {operands}')

                ret = []
                for r, o in zip(req, operands):
                    if r == 'R' or r == 'A':
                        if r == 'A':
                            # Register address
                            if len(o) < 4 or o[0] != '[' or o[-1] != ']':
                                raise SyntaxError(f"{lidx}: {mnemonic} operand '{o}' is not a valid indirect memory request")
                            o = o[1:-1]

                        # Register
                        if len(o) < 2 or o[0] != 'r' or int(o[1:]) < 0 or int(o[1:]) > 15:
                            raise SyntaxError(f"{lidx}: {mnemonic} operand '{o}' is not a valid register")
                        ret.append(f'{int(o[1:]):04b}')
                    elif r == '4' or r == '8' or r == 'B':
                        if r == 'B':
                            # Constant address
                            if len(o) < 2 or o[0] != '[' or o[-1] != ']':
                                raise SyntaxError(f"{lidx}: {mnemonic} operand '{o}' is not a valid direct memory request")
                            o = o[1:-1]

                        # Constant or label evaluated as constant
                        if len(o) > 1 and o[0] == '@':
                            if o[1:] in labels:
                                if r == '4':
                                    ret.append(f'{labels[o[1:]]:04b}')
                                else:
                                    ret.append(f'{labels[o[1:]]:08b}')
                            else:
                                raise ValueError(f"{lidx}: label '{o}' not defined")
                        elif r != '4' and len(o) == 3 and o[0] == r'"' and o[-1] == r'"':
                            ret.append(f'{ord(o[1]):08b}')
                        else:
                            try:
                                val = int(o, 0)
                            except:
                                raise SyntaxError(f"{lidx}: {mnemonic} operand '{o}' is not a valid constant")
                            if r == '4':
                                if val < -8 or val > 15:
                                    raise ValueError(f"{lidx}: {mnemonic} operand '{o}' is not a valid 4-bit signed or unsigned constant")
                                if val < 0:
                                     val = 16+val
                                ret.append(f'{val:04b}')
                            else:
                                if val < -128 or val > 255:
                                    raise ValueError(f"{lidx}: {mnemonic} operand '{o}' is not a valid 8-bit signed or unsigned constant")
                                if val < 0:
                                    val = 256+val
                                ret.append(f'{val:08b}')
                    else:
                        ret.append(o)
                return opcode, minor, ret
            except Exception as e:
                lastex = e
        raise lastex

    def _pass2(self, lines, labels):
        """Emits machine code."""
        mem = {'code': [], 'data': []}
        section = 'code'

        ls = 0
        for l in labels:
            ls = max(ls, len(l))

        ref = ' ' * (ls + 2)
        for (idx, label, inst) in lines:
            if label != '':
                ref = f'{label}: ' + ' ' * (ls-len(label))
            else:
                ref = ' ' * (ls + 2)

            if inst == '':
                continue

            mnemonic, operands = split(inst)
            opcode, minor, operands = self._resolve(idx, mnemonic, operands, labels)

            if mnemonic == '.section':
                section = operands[0]
            elif mnemonic == '.equ':
                # Ignore
                pass
            elif mnemonic == '.org':
                # Fill memory until requested address
                while len(mem[section]) < int('0b' + operands[0], 0):
                    if section == 'code':
                        mem[section].append(('00000000000000000', ''))
                    else:
                        mem[section].append(('00000000', ''))
            elif mnemonic == '.db':
                # Add byte into instruction stream
                mem[section].append((operands[0], f'{idx}: {ref}{inst}'))
            elif section != 'code':
                raise ValueError(f'{idx}: Cannot use instructions in data section')
            else:
                instcode = opcode
                for o in operands:
                    instcode += o
                instcode += minor

                mem[section].append((instcode, f'{idx}: {ref}{inst}'))

            ref = ' ' * (ls + 2)

        return mem
