; Standard definitions for ENG1448 processor

; Memory-mapped I/O
      .equ imr, 0x10 ; Interrupt mask register
      .equ isr, 0x11 ; Interrupt status register
      .equ udr, 0x12 ; UART data register
      .equ usr, 0x13 ; UART status register
      .equ kdr, 0x14 ; Keyboard data register
      .equ inp, 0x15 ; Input register
      .equ enc, 0x16 ; Encoder counter register
      .equ led, 0x17 ; LED register
      .equ ssd, 0x18 ; 7-segment display register
      .equ ldr, 0x19 ; LCD data register
      .equ lcr, 0x1A ; LCD command register
