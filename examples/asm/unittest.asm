; Unit tests for ENG1448 processor
; When successful, halts at instruction 226, showing 0b01010101
; When unsuccessful, halts at instruction 240, showing test number (1-32)

       .macro setled
       mov  r12, $0
       str  r12, [0x05]
       .endmacro

.section data

       .org 17

data:  .db  0x55
       .db  0xAA
tmp1:  .db  0
       .db  0
tmp2:  .db  0
       .db  0

.section code

main:  setled 1
       mov  r5, 0x55
       mov  r10, 0xAA

mov1:  setled 2
       mov  r0, 0x55
       sub  r11, r5, r0
       bnz  @err

ldr1:  setled 3
       ldr  r0, [@data]
       sub  r11, r5, r0
       bnz  @err

ldr2:  setled 4
       mov  r1, @data
       ldr  r0, [r1]
       sub  r11, r5, r0
       bnz  @err

ldr3:  setled 5
       mov  r1, @data
       ldr  r0, [r1, 1]
       sub  r11, r10, r0
       bnz  @err

str1:  setled 6
       str  r5, [@tmp1]
       ldr  r0, [@tmp1]
       sub  r11, r5, r0
       bnz  @err

str2:  setled 7
       mov  r1, @tmp2
       str  r5, [r1]
       ldr  r0, [@tmp2]
       sub  r11, r5, r0
       bnz  @err

str3:  setled 8
       mov  r1, @tmp2
       str  r10, [r1, 1]
       ldr  r0, [r1, 1]
       sub  r11, r10, r0
       bnz  @err

b1:    setled 9
       b    @b2
       b    @err
b2:

push1: setled 10
       mov  r1, 254
       push r5
       sub  r11, r1, r14
       bnz  @err
       ldr  r0, [r14, 1]
       sub  r11, r5, r0
       bnz  @err

pop1:  setled 11
       mov  r14, 255
       push r10
       pop  r0
       sub  r11, r10, r0
       bnz  @err

call1: setled 12
       call @call2
calln: b    @err
call2: mov  r1, @calln
       pop  r0
       sub  r11, r1, r0
       bnz  @err

ret1:  setled 13
       mov  r1, @ret2
       push r1
       ret
       b    @err
ret2:

add1:  setled 14
       mov  r1, 0xFF
       add  r0, r5, r10
       sub  r11, r1, r0
       bnz  @err

add2:  setled 15
       mov  r1, 0x5A
       add  r0, r5, 0x05
       sub  r11, r1, r0
       bnz  @err

sub1:  setled 16
       mov  r1, 0x55
       sub  r0, r10, r5
       sub  r11, r1, r0
       bnz  @err

sub2:  setled 17
       mov  r1, 0x50
       sub  r0, r5, 0x05
       sub  r11, r1, r0
       bnz  @err

shl1:  setled 18
       mov  r1, 1
       shl  r0, r5, r1
       sub  r11, r0, r10
       bnz  @err

shl2:  setled 19
       shl  r0, r5, 1
       sub  r11, r0, r10
       bnz  @err

shr1:  setled 20
       mov  r1, 1
       shr  r0, r10, r1
       sub  r11, r0, r5
       bnz  @err

shr2:  setled 21
       shr  r0, r10, 1
       sub  r11, r0, r5
       bnz  @err

and1:  setled 22
       and  r11, r5, r10
       bnz  @err
       and  r11, r5, r5
       sub  r11, r11, r5
       bnz  @err

and2:  setled 23
       and  r11, r5, 2
       bz   @err
       and  r11, r5, 3
       bnz  @err

orr1:  setled 24
       mov  r1, 255
       orr  r11, r5, r10
       sub  r11, r11, r1
       bnz  @err
       orr  r11, r5, r5
       sub  r11, r11, r5
       bnz  @err

orr2:  setled 25
       orr  r11, r5, 2
       sub  r11, r11, r5
       bnz  @err
       orr  r11, r5, 1
       add  r9, r5, 2
       sub  r11, r11, r9
       bnz  @err

eor1:  setled 26
       mov  r1, 255
       eor  r11, r5, r10
       sub  r11, r11, r1
       bnz  @err
       eor  r11, r5, r1
       sub  r11, r11, r10
       bnz  @err

eor2:  setled 27
       eor  r11, r5, 2
       sub  r9, r5, 4
       sub  r11, r11, r9
       bnz  @err
       eor  r11, r5, 1
       add  r9, r5, 2
       sub  r11, r11, r9
       bnz  @err

bz1:   setled 28
       sub  r11, r5, r5
       bz   @bz2
       b    @err
bz2:   sub  r11, r10, r5
       bz   @err

bnz1:  setled 29
       sub  r11, r10, r5
       bnz  @bnz2
       b    @err
bnz2:  sub  r11, r5, r5
       bnz  @err

bcs1:  setled 30
       shl  r11, r10, 1
       bcs  @bcs2
       b    @err
bcs2:  shl  r11, r5, 1
       bcs  @err
       add  r11, r10, r10
       bcs  @bcs3
       b    @err
bcs3:  setled 31
       sub  r11, r5, r10
       bcs  @err

bcc1:  setled 32
       shl  r11, r5, 1
       bcc  @bcc2
       b    @err
bcc2:  shl  r11, r10, 1
       bcc  @err
       sub  r11, r10, r5
       bcc  @err

       b    @succ

       .org 0xE0

succ:  setled 0x55
ends:  b    @ends

       .org 0xF0

err:   b    @err
