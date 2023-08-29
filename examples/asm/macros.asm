; Example Macros for ENG1448 processor

; Wait for keyboard character.
; INPUT : None
; OUTPUT: Keyboard character in $0
       .macro waitkb
_wait: ldr  $0, [@kdr] ; Read keyboard character
       mov  $0, $0     ; Set flags
       bz   @_wait     ; Wait until nonzero
       .endmacro

; Write LCD character.
; INPUT : LCD character in $0
; OUTPUT: None
; NOTE  : Clobbers r10
       .macro writelcd
_wait: ldr  r10, [@ldr]; Read LCD data
       mov  r10, r10   ; Set flags
       bnz  @_wait     ; Wait until zero
       str  $0, [@ldr] ; Write character to LCD
       .endmacro

; Clear LCD.
; INPUT : None
; OUTPUT: None
; NOTE  : Clobbers $0
       .macro clearlcd
_wait: ldr  $0, [@lcr] ; Read LCD command
       mov  $0, $0     ; Set flags
       bnz  @_wait     ; Wait until zero
       mov  $0, 0x01   ;
       str  $0, [@lcr] ; Clear LCD
       .endmacro
