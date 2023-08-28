        b @inst

; .org
        .org 0x5

; label, .equ
mylbl:  .equ equ1, 0x2a

; .db
.section data
        .org 0x20
        .db 123
        .db 0x2a
        .db @mylbl2
        .org 0x40
mylbl2: .db "Hello, world"
        .db 123, 0x2a, @mylbl2, "Hello, world"

.section code

; .macro
; local labels
        .macro macro1
_loop:  b @_loop
        .endmacro
        macro1
        macro1

; .macro
; arguments
        .macro macro2
_loop:  mov r1, $0
        mov r1, $1
        macro1
        b @_loop
        .endmacro
        macro2 0xAA, 0x55

; Instructions
inst:   ldr  r1, [r2]
        ldr  r1, [r2, 1]
        ldr  r1, [1]
        ldr  r1, [@mylbl]
        str  r1, [r2]
        str  r1, [r2, 1]
        str  r1, [1]
        mov  r1, 12
        mov  r1, 0x55
        mov  r1, "a"
        mov  r1, @equ1
        mov  r1, r2

        push r1
        pop  r1

        add r1, r2, r3
        add r1, r2, 1
        sub r1, r2, r3
        sub r1, r2, 1
        shft r1, r2, r3
        shft r1, r2, 1
        shft r1, r2, -1
        and r1, r2, r3
        clr r1, r2, 1
        orr r1, r2, r3
        set r1, r2, 1
        eor r1, r2, r3
        flip r1, r2, 1

        b 1
        b @mylbl

        bz 1
        bnz 1
        bcs 1
        bcc 1

        call 1
        ret
