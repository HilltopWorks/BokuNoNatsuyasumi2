.ps2
.erroronwarning on
;Blessing graphics

;Graphic positions
blessing_x equ 0x100
blessing_y equ 0x58

.open "MAP_RIP_EDITS\M_D09000\0.bin",0

.org 0x7f0
	.halfword  blessing_x
	.halfword  blessing_y
.org 0x800
	.halfword  blessing_x
	.halfword  blessing_y
.org 0x810
	.halfword  blessing_x
	.halfword  blessing_y
.org 0x820
	.halfword  blessing_x
	.halfword  blessing_y

.close

.open "MAP_RIP_EDITS\M_D09100\0.bin",0

.org 0x760
	.halfword  blessing_x
	.halfword  blessing_y
.org 0x770
	.halfword  blessing_x
	.halfword  blessing_y
.org 0x780
	.halfword  blessing_x
	.halfword  blessing_y
.org 0x790
	.halfword  blessing_x
	.halfword  blessing_y

.close

;Graphic dimension

.open "MAP_RIP_EDITS\M_D09000\6.bin",0

.org 0x8b9a8
	.halfword 0x80
	.halfword 0x80
.org 0x8da28
	.halfword 0x80
	.halfword 0x80
.org 0x8faa8
	.halfword 0x80
	.halfword 0x80
.org 0x91b28
	.halfword 0x80
	.halfword 0x80

.close

.open "MAP_RIP_EDITS\M_D09100\6.bin",0

.org 0x8b9a8
	.halfword 0x80
	.halfword 0x80
.org 0x8da28
	.halfword 0x80
	.halfword 0x80
.org 0x8faa8
	.halfword 0x80
	.halfword 0x80
.org 0x91b28
	.halfword 0x80
	.halfword 0x80

.close