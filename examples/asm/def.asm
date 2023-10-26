; Standard definitions for ENG1448 processor

; Memory-mapped I/O
      .equ btn, 0x00 ; Input register
      .equ enc, 0x01 ; Encoder counter register
      .equ kdr, 0x02 ; Keyboard data register
      .equ udr, 0x03 ; UART data register
      .equ usr, 0x04 ; UART status register
      .equ led, 0x05 ; LED register
      .equ ssd, 0x06 ; 7-segment display register
      .equ ldr, 0x07 ; LCD data register
      .equ lcr, 0x08 ; LCD command register
