.ps2
.erroronwarning on


.open "ISO_EDITS\scps_150.26", 0xFF000

.definelabel vwf_table, 0x002a1968 ;0xd0 bytes of free space
.definelabel func_vwf, 0x028eb34
.definelabel text_loop_space, 0x00290538 ;free debug text space


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

; ################		   Load vwf table				####################
.org vwf_table
.import "font_kerning.bin"

; ################         Main Dialogue text hack             ####################
.definelabel 	draw_dialogue, 0x001fdcb0
;.definelabel 	draw_char_7, 0x00180670
;.definelabel	draw_char, 0x00180680 ; int x, int y, uint char, B(7?)
;.definelabel	stash_char, 0x001fde94
.definelabel	draw_dialogue_char_start, 0x001fdeac ;start of char drawing routine in dialogue
.definelabel	draw_dialogue_char_end, 0x1fdf54
.definelabel	set_font_color, 0x180168	;Br Bg Bb Ba
.definelabel 	set_spacing, 0x1fde94
.definelabel	set_kerning, 0x1fdf58
.definelabel	set_x_top,   0x1fde34
.definelabel	set_x_top_2, 0x001fdd40
.definelabel	set_y_base, 0x1fde98
.definelabel 	get_fb_y, 0x0012D3C8
.definelabel 	get_fb_x, 0x0012D390

.definelabel	char_pointer, 0x0027bbc0
.definelabel	char_offset, 0x0027bbd0

.definelabel	font_color, 0x2615c8
.definelabel	font_color_u, 0x26
.definelabel	font_color_l, 0x15c8


shadow_x equ 0x20
shadow_y equ 0x10

curr_x equ  s4
newlines equ v1
gpu_call equ s0

text_padding equ 2
base_x equ 0x330
base_y equ 0xAD
;font_width equ 0x160	 ; kerning
font_spacing equ 0xC ; newline spacing
white  equ 0x7FFFFFFF
black  equ 0x7F000000
yellow equ 0x7F00FFFF

;TODO: make this loop another time with black text
;	   and slight x/y offset.

.org draw_dialogue_char_start
.area draw_dialogue_char_end - draw_dialogue_char_start,0
	j font_loop
	nop

after_text_loop:
	nop
.endarea

.org text_loop_space
font_loop:
	;Set main font color
	la a1, black
	sw a1, 0x0(gpu_call)
	la a1, white
	sw a1, 0x28(gpu_call)
	
	;autopilot    		; a2 = base_y, 
	mfhi	a3 			; a3 = char%17
	mflo	a1 			; a1 = char/17
	mult	v0,v1,v0 	; v0 = newlines*spacing ;.word 0x00621018	
	mult 	a1,a1,s7 	; a1 = (char/17)*0x16, aka glyph height x row aka v ;.word 0x00B72818	
	addu	s2,a2,v0 	; s2 = base_y + (newlines*spacing)
	mult	zero,a3,s7 	; lo = (char%0x17)*0x16, aka glyph width x column aka u ;.w 0x00F70018	
	andi	a2,a1,0xFFFF; a2 = font row
	mflo	a3			; a3 = u
	addiu	a1,a2,0x16	; a1 = v_bottom
	addiu	a0,a3,0x16	; a0 = u_bottom
	sll		a1,a1,0x04	; a1 = v_gpu_bottom
	sll		a0,a0,0x04  ; a0 = u_gpu_right

	sll	v0,a3,0x04		; a3 = u_gpu
	sll	v1,a2,0x04		; a2 = v_gpu
	sh	v0,0x8(gpu_call)		; STORE u_gpu
	sh	v0,0x30(gpu_call)
	sh	v1,0xA(gpu_call)		; STORE v_gpu
	sh	v1,0x32(gpu_call)
	sh	a0,0x18(gpu_call)		; STORE u_right_gpu
	sh	a0,0x40(gpu_call)
	jal	get_fb_y				; v0 = frame_buffer_y
	sh	a1,0x1A(gpu_call)		; STORE v_bottom_gpu	^
	sh	a1, 0x42(gpu_call)


	sll	v1,s2,0x04			; v1 = (base_y + (newlines*spacing)) *0x10 aka y_gpu unf
	addu	v0,v1			; v0 = y_gpu unf + frame_buffer_y aka y_gpu
	sh	v0,0x12(gpu_call)	; STORE y_gpu
	addiu	v0, v0, -shadow_y
	sh	v0, 0x3A(gpu_call)	; STORE y_gpu SHADOW
	addiu	v0,v0,0xB0		; v0 = y_gpu + 0xb8 aka y_gpu_bottom
	sh  v0, 0x4A(gpu_call)	; STORE y_gpu_bottom SHADOW
	addiu	v0, v0, shadow_y
	jal	get_fb_x			; v0 = frame_buffer_x
	sh	v0,0x22(gpu_call)	; STORE y_gpu_bottom		^
	addu	v0,curr_x		; v0 = frame_buffer_x + curr_x aka x_gpu
	sh	v0,0x10(gpu_call)	; STORE x_gpu
	
	;addiu	v1,curr_x,0x170	; v1 = curr_x + 0xb8 aka x_right
	addiu	v0,0x160			; v0 = x_right + frame_buffer_x aka x_gpu_right
	sh	v0,0x20(gpu_call)	; STORE x_gpu_right
	addiu 	v0, -shadow_x
	sh		v0, 0x48(gpu_call)	; STORE x_gpu_right SHADOW
	addiu	v0, -0x160
	sh v0, 0x38(gpu_call)	; STORE x_gpu SHADOW

	addiu	gpu_call,0x50	; gpu_cursor += 0x50
	
	j	func_vwf
	nop	

.org func_vwf
	;vwf
	la v1, vwf_table
	la s2, char_pointer
	lw v0, 0x10(s2)			;v0 = char_offset/2
	sll v0, v0, 0x1			;v0 = char_offset
	lw s2, 0x0(s2)			;s2 = text_base
	addu s2, v0, s2			;s2 = char offset + text_base aka &char
	lh 	s2, 0x0(s2)			;s2 = *&char
	
	addu v1, v1, s2			;v1 = &vwf_table[char]
	lb	v1, 0x0(v1)			;v1 = *&vwf_table[char]
	addiu v1, v1, text_padding	; add padding space to every character
	sll v1, v1, 0x4			;1 pixel = 0x10 value
	j after_text_loop
	nop


.org set_kerning
	addu s4, s4, v1 ;font_width

.org set_spacing
	li v0, font_spacing

.org set_y_base
	li a2, base_y

.org set_x_top
	;Set base x after newline
	li curr_x, base_x
.org set_x_top_2
	;Set base x after newline
	li curr_x, base_x

.close