         .include "def.asm"

main:    ldr  r0, 0
         ldr  r1, 0
         str  r0, [@ssd] ; Initialize display counter

loop:    mov  r0, r1     ; Save prevous input register status into r0
         ldr  r1, [@inp] ; Read current input register status into r1

         mvn  r0, r0     ; Invert r0
         and  r0, r0, r1 ; Detect positive edge (r1 & ~r0)
         rol  r0, r0
         rol  r0, r0     ; Move BTN_EAST into carry
         bcc  @loop      ; If no edge, continue loop
         call @incr      ; Jump to subroutine
         b    @loop      ; Wait for next edge

         .org 0x80
incr:    push r0
         ldr  r0, [@ssd] ; Read display counter
         inc  r0, r0     ; Increment
         str  r0, [@ssd] ; Write back display counter
         pop r0
         ret
