       .include "def.asm"

; Write welcome message
main:  ldr  r0, 7
       ldr  r1, @msg1
       call @writemsg ; Write 7 characters from @msg1 to lcd

; Echo PS/2 characters to LCD
ret:   ldr  r2, [@ldr]; Read LCD data register into r2
       mov  r2, r2    ;
       bnz  @ret      ; Wait until it is 0
wkbd:  ldr  r2, [@kdr]; Get character from keyboard
       mov  r2, r2    ; 
       bz   @wkbd     ; Wait until nonzero
       ldr  r1, 0x0D  ;
       sub  r4, r2, r1; Compare to enter key
       bnz  @wchar    ; If no , write character to LCD
       ldr  r2, 0x01  ; If yes, clear LCD
       str  r2, [@lcr]; Clear LCD
       b    @ret
wchar: str  r2, [@ldr]  ; Write to LCD
       b    @ret

; Write message to LCD.
; r0 contains message length
; r1 contains message address
writemsg:
       add  r0, r0, r1; Set r0 to one past final character
wloop: ldr  r2, [@ldr]; Read LCD data register into r2
       mov  r2, r2    ;
       bnz  @wloop    ; Wait until it is 0
       ldr  r2, [r1]  ;
       str  r2, [@ldr]; Write next character to LCD
       inc  r1, r1    ; Advance
       sub  r4, r1, r0; 
       bnz  @wloop    ; Loop until last character was sent
       ret            ; ret

.section data
msg1:  .db "welcome"
