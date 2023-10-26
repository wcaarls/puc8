         .include "def.asm"

main:    mov  r0, 0
         mov  r1, 0
         mov  r2, 255
         str  r0, [@ssd] ; Initialize display counter

loop:    mov  r0, r1     ; Save prevous input register status into r0
         ldr  r1, [@btn] ; Read current input register status into r1

         eor  r0, r0, r2 ; Invert r0
         and  r0, r0, r1 ; Detect positive edge (r1 & ~r0)
         and  r0, r0, 6  ; Test for BTN_EAST
         bz   @loop      ; If no edge, continue loop
         call @incr      ; Jump to subroutine
         b    @loop      ; Wait for next edge

         .org 0x80
incr:    push r0
         ldr  r0, [@ssd] ; Read display counter
         add  r0, r0, 1  ; Increment
         str  r0, [@ssd] ; Write back display counter
         pop  r0
         ret
