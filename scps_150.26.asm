.psx
.erroronwarning on


.open "ISO_EDITS\scps_150.26", 0xFF000

.definelabel freespace, 0x28e13C ;0x38 bytes of free space

; ################         Removing the CRC Check            ####################
.org 0x1bff98
	nop
	ori v0, zero, 0x0

; ################         Removing the dialogue background            ####################
.org 0x1ff530
	nop
	nop

; ################         Enable debug mode            ####################
.org 0x020a970
	lui 	a0,0x28
.org 0x20a978
	addiu	a0, a0, -0x11b0


; ################         Main Dialogue text hack             ####################
.definelabel 	draw_dialogue, 0x001fdcb0
.definelabel 	draw_char_7, 0x00180670
.definelabel	draw_char, 0x00180680 ; int x, int y, uint char, B(7?)
.definelabel	stash_char, 0x001fde94
.definelabel	draw_dialogue_char_start, 0x001fdeac ;start of char drawing routine in main dialogue
.definelabel	draw_dialogue_char_end, 0x1fdf54
.definelabel	set_font_color, 0x180168	;Br Bg Bb Ba
.definelabel	set_x_top, 0x1fde34
.definelabel	set_x_top_2, 0x001fdd40

.definelabel	font_color, 0x2615c8
.definelabel	font_color_u, 0x26
.definelabel	font_color_l, 0x15c8

current_x equ  s4
newlines equ v1
gpu_call equ s0

base_x equ 0x50
base_y equ 0x150
font_width equ 0x17
font_spacing equ 0x19
white equ 0x80FFFFFF
;Free: v0, a3, a2, a1, s2

;x left = current_x               ;x right = current_x + 0x17
;y top = base_y + (newlines*0x1A) ;y bot = base_y + (newlines*0x1A) + 0x17
;char = 

.org draw_dialogue_char_start
.area draw_dialogue_char_end - draw_dialogue_char_start,0

	;Set main font color
	la v0, white
	sw v0, 0x0(gpu_call)
	
	;autopilot    		; a2 = base_x, 
	mfhi	a3 			; a3 = char%17
	mflo	a1 			; a1 = char/17
	mult	v0,v1,v0 	; v0 = newlines*spacing
	mult	a1,a1,s7 	; a1 = (char/17)*0x16, aka glyph height x row aka v
	li		v1,0x80
	mult	zero,a3,s7 	; lo = (char%0x17)*0x16, aka glyph width x column aka u
	sb		v1,0x3(s0)
	subu	s2,a2,v0 	; s2 = base_x - (newlines*spacing)
	andi	a2,a1,0xFFFF; a2 = font row
	mflo	a3			; a3 = u
	addiu	a1,a2,0x17	; 
	addiu	a0,a3,0x17
	sll		a1,a1,0x04
	sll		a0,a0,0x04
	
	;Set params
	move a0, current_x ;x = current_x
	
	li v0, font_spacing;y = basey + (newlines*spacing)
	mult v0, newlines
	nop
	nop
	mflo v0
	addi a1, v0, base_y
	
	;Store squashed registers
	la v0, freespace
	
	sw t4, 0x0(v0)
	sw t7, 0x4(v0)
	sw v1, 0x8(v0)
	

	;Draw character
	jal draw_char_7 ;squashes v0,v1,a0,a1,a2,t4,t7
	nop
	
	;Restore squashed registers
	la v0, freespace
	lw t4, 0x0(v0)
	lw t7, 0x4(v0)
	lw v1, 0x8(v0)

	;Increment text x position
	addiu current_x, current_x, font_width

.endarea

.org set_x_top
	;Set base x after newline
	li current_x, base_x
.org set_x_top_2
	;Set base x after newline
	li current_x, base_x

.close