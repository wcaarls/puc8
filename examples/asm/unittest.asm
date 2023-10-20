; Unit tests for ENG1448 processor
; When successful, halts at instruction 254, showing 0b01010101
; When unsuccessful, halts at instruction 255, showing test number (1-37)

       .macro setled
       mov  r12, $0
       str  r12, [0x05]
       .endmacro

.section data

       .org 17

data:  .db  0x55
data2: .db  0xAA
tmp1:  .db  0
       .db  0
tmp2:  .db  0
tmp3:  .db  0

.section code

; Preparation
main:  setled 1
       mov  r5, 0x55
       mov  r10, 0xAA

; Move immediate
mov1:  setled 2
       mov  r0, 0x55
       sub  r11, r5, r0
       bnz  @err

; Load from immediate address
ldr1:  setled 3
       ldr  r0, [@data]
       sub  r11, r5, r0
       bnz  @err

; Load from address contained in register
ldr2:  setled 4
       mov  r1, @data
       ldr  r0, [r1]
       sub  r11, r5, r0
       bnz  @err

; Load with positive immediate offset
ldr3:  setled 5
       mov  r1, @data
       ldr  r0, [r1, 1]
       sub  r11, r10, r0
       bnz  @err

; Load with negative immediate offset
ldr4:  setled 6
       mov  r1, @data2
       ldr  r0, [r1, -1]
       sub  r11, r5, r0
       bnz  @err

; Store to immediate address
str1:  setled 7
       str  r5, [@tmp1]
       ldr  r0, [@tmp1]
       sub  r11, r5, r0
       bnz  @err

; Store to address contained in register
str2:  setled 8
       mov  r1, @tmp2
       str  r5, [r1]
       ldr  r0, [@tmp2]
       sub  r11, r5, r0
       bnz  @err

; Store with positive immediate offset
str3:  setled 9
       mov  r1, @tmp2
       str  r10, [r1, 1]
       ldr  r0, [@tmp3]
       sub  r11, r10, r0
       bnz  @err

; Store with negative immediate offset
str4:  setled 10
       mov  r1, @tmp3
       str  r10, [r1, -1]
       ldr  r0, [@tmp2]
       sub  r11, r10, r0
       bnz  @err

; Unconditional branch to immediate address
b1:    setled 11
       b    @b2
       b    @err
b2:

; Push to stack
push1: setled 12
       mov  r1, 254
       push r5
       sub  r11, r1, r14
       bnz  @err
       ldr  r0, [r14, 1]
       sub  r11, r5, r0
       bnz  @err

; Pop from stack
pop1:  setled 13
       mov  r14, 255
       push r10
       pop  r0
       sub  r11, r10, r0
       bnz  @err

; Call subroutine contained in immediate address
call1: setled 14
       call @call2
calln: b    @err
call2: mov  r1, @calln
       pop  r0
       sub  r11, r1, r0
       bnz  @err

; Return from subroutine
ret1:  setled 15
       mov  r1, @ret2
       push r1
       ret
       b    @err
ret2:

; Add two registers
add1:  setled 16
       mov  r1, 0xFF
       add  r0, r5, r10
       sub  r11, r1, r0
       bnz  @err

; Add constant to register
add2:  setled 17
       mov  r1, 0x5A
       add  r0, r5, 0x05
       sub  r11, r1, r0
       bnz  @err

; Subtract two registers
sub1:  setled 18
       mov  r1, 0x55
       sub  r0, r10, r5
       sub  r11, r1, r0
       bnz  @err

; Subtract constant from register
sub2:  setled 19
       mov  r1, 0x50
       sub  r0, r5, 0x05
       sub  r11, r1, r0
       bnz  @err

; Shift left (always 1)
shl1:  setled 20
       mov  r1, 1
       shl  r0, r5, r1
       sub  r11, r0, r10
       bnz  @err

; Shift left (always 1)
shl2:  setled 21
       shl  r0, r5, 1
       sub  r11, r0, r10
       bnz  @err

; Shift right (always 1)
shr1:  setled 22
       mov  r1, 1
       shr  r0, r10, r1
       sub  r11, r0, r5
       bnz  @err

; Shift right (always 1)
shr2:  setled 23
       shr  r0, r10, 1
       sub  r11, r0, r5
       bnz  @err

; Bit-wise AND of two registers
and1:  setled 24
       and  r11, r5, r10
       bnz  @err
       and  r11, r5, r5
       sub  r11, r11, r5
       bnz  @err

; Bit-wise AND of register and constant bit (select)
and2:  setled 25
       and  r11, r5, 2
       bz   @err
       and  r11, r5, 3
       bnz  @err

; Bit-wise OR of two registers
orr1:  setled 26
       mov  r1, 255
       orr  r11, r5, r10
       sub  r11, r11, r1
       bnz  @err
       orr  r11, r5, r5
       sub  r11, r11, r5
       bnz  @err

; Bit-wise OR of register and constant bit (set)
orr2:  setled 27
       orr  r11, r5, 2
       sub  r11, r11, r5
       bnz  @err
       orr  r11, r5, 1
       add  r9, r5, 2
       sub  r11, r11, r9
       bnz  @err

; Bit-wise XOR of two registers
eor1:  setled 28
       mov  r1, 255
       eor  r11, r5, r10
       sub  r11, r11, r1
       bnz  @err
       eor  r11, r5, r1
       sub  r11, r11, r10
       bnz  @err

; Bit-wise XOR of register and constant bit (flip)
eor2:  setled 29
       eor  r11, r5, 2
       sub  r9, r5, 4
       sub  r11, r11, r9
       bnz  @err
       eor  r11, r5, 1
       add  r9, r5, 2
       sub  r11, r11, r9
       bnz  @err

; Branch when zero flag set
bz1:   setled 30
       sub  r11, r5, r5
       bz   @bz2
       b    @err
bz2:   sub  r11, r10, r5
       bz   @err

; Branch when zero flag not set
bnz1:  setled 31
       sub  r11, r10, r5
       bnz  @bnz2
       b    @err
bnz2:  sub  r11, r5, r5
       bnz  @err

; Branch when carry flag set, carry flag set by shift left
bcs1:  setled 32
       shl  r11, r10, 1
       bcs  @bcs2
       b    @err

; Branch when carry flag set, carry flag set by addition
bcs2:  setled 33
       shl  r11, r5, 1
       bcs  @err
       add  r11, r10, r10
       bcs  @bcs3
       b    @err

; Branch when carry flag set, carry flag set by subtraction
bcs3:  setled 34
       sub  r11, r5, r10
       bcs  @err

; Branch when carry flag not set, carry flag set by shift left
bcc1:  setled 35
       shl  r11, r5, 1
       bcc  @bcc2
       b    @err

; Branch when carry flag not set, carry flag set by subtraction
bcc2:  setled 36
       shl  r11, r10, 1
       bcc  @err
       sub  r11, r10, r5
       bcc  @err

; Unconditional branch to indirect address with offset
br1:   setled 37
       b    pc, 1
       b    @err

       b    @succ

       .org 0xFC

succ:  setled 0x55
ends:  b    @ends

       .org 0xFF

err:   b    @err
