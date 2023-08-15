       .include "def.asm"
       .include "macros.asm"

; Write welcome message
main:  ldr  r0, 7
       ldr  r1, @msg1
       call @writemsg ; Write 7 characters from @msg1 to lcd

; Echo PS/2 characters to LCD
loop:  waitkb r0      ; Read character from keyboard
       ldr  r1, 0x0D  ; Compare to enter key
       sub  r1, r0, r1;
       bz   @clear    ; If enter, clear LCD
       writelcd r0    ; Otherwise, write to LCD
       b    @loop
clear: clearlcd r0    ; Clear LCD
       b    @loop

; Write message to LCD.
; r0 contains message length
; r1 contains message address
writemsg:
       add  r0, r0, r1; Set r0 to one past final character
wloop: ldr  r2, [r1]  ; Get character to write
       writelcd r2    ; Write character to LCD
       inc  r1, r1    ; Advance
       sub  r2, r1, r0; 
       bnz  @wloop    ; Loop until last character was sent
       ret            ; ret

.section data
       .org 0x10
msg1:  .db "welcome"
