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
_loop:  ldr r1, $0
        ldr r1, $1
        macro1
        b @_loop
        .endmacro
        macro2 0xAA, 0x55

; Instructions
inst:   ldr  r1, [r2]
        ldr  r1, [1]
        ldr  r1, [@mylbl]
        ldr  r1, 1
        ldr  r1, @equ1
        str  r1, [r2]
        str  r1, [1]

        push r1
        pop  r1
        ldsp r1
        stsp r1

        mov r1, r2
        mvn r1, r2
        neg r1, r2
        inc r1, r1
        dec r1, r1
        lsl r1, r2
        lsr r1, r2
        rol r1, r2
        ror r1, r2

        add r1, r2, r3
        adc r1, r2, r3
        sub r1, r2, r3
        sbc r1, r2, r3
        and r1, r2, r3
        orr r1, r2, r3
        eor r1, r2, r3

        b 1
        b @mylbl

        bz 1
        bnz 1
        bcs 1
        bcc 1

        call 1
        ret
