.ps2
.erroronwarning on

.open "ISO_EDITS\boku2.crc",0
; ################		   Load vwf table				####################
.definelabel crc_hash_offset, 0x16374
.org crc_hash_offset
.import "font_kerning.bin"

.close

.open "ISO_EDITS\scps_150.26", 0xFF000

.definelabel vwf_table, 0x0712b24 ;#0x002a1968 ;0xd0 bytes of free space
.definelabel func_vwf, 0x028eb34
.definelabel text_loop_space, 0x00290538 ;free debug text space

.definelabel 	get_fb_y, 0x0012D3C8
.definelabel 	get_fb_x, 0x0012D390
; ################         Removing the CRC Check            ####################
.org 0x1bff98
	nop
	ori v0, zero, 0x0

; ################         Edit the dialogue background            ####################
;;Disable BG
;.org 0x1ff530
;	nop
;	nop

bg_alpha equ 0x44
bg_tone  equ 0x10

bg_y_start equ 0xA40

;set bg alpha value
.org 0x0180248
	li v0, bg_alpha

.org 0x001801f8  
	li v1, bg_alpha

;bg_fade amount per frame and end point
.org 0x00180238 
	addiu  v0,v0, bg_alpha >> 4
	slti v1,v0, bg_alpha + 1

;bg fade amount per frame (end point is 0)
.org 0x0018025c
	addiu  v0,v0,-bg_alpha >> 4

;bg greyscale value
.org 0x00180290  
	li    s1, bg_tone

;bg_left (stay at framebuffer left) and top
.org 0x0018030c 
	jal get_fb_y
	sh v0, 0x8(s0)
	addiu v0, v0, bg_y_start

;disable gradient
.org 0x0018037c
	li   v0, 0x0
.org 0x001803a0
	li   v0, 0x0

; ################         Enable debug mode            ####################
;.org 0x020a970
;	lui 	a0,0x28
;.org 0x20a978
;	addiu	a0, a0, -0x11b0

; ################		   Native Horizontal text fixes

mfw equ 0xb ;Menu font width

; Hori text texel 23->22 fix
.org 0x018077c
	addiu v1, a2, 0x16
.org 0x0180794
	addiu v0, a0, 0x16
; Char H/W 23->22 fix
.org 0x01807d0 
	addiu  v1,s2, 0x16
.org 0x01807e4
	addiu  v1,s3, 0x16

; Hori text kerning updates

.org 0x0155e94 
	addiu s2,s2,mfw

.org 0x155ee8
	addiu s2,s2,mfw

.org 0x0156044  
	addiu s2,s2,-mfw

.org 0x0156098
	addiu s2,s2,-mfw

.org 0x0015a4bc
	li v1,mfw + 3

.org 0x015a4c4
	li v0,mfw
	li v1,mfw
	li v0,mfw + 3

;;.org 0x019d290  ;VERTICAL TEXT
;	addiu s2,s2,mfw

.org 0x001a7998  
	addiu s1,s1,mfw

.org 0x001a7a78  
	addiu  s1,s1,mfw

.org 0x001a7b30  
	addiu  s1,s1,mfw

.org 0x001a7d4c
	addiu  s1,s1,mfw


.org 0x001a81f8 
	addiu s1,s1,mfw

.org 0x001a7ef8  
	addiu s1,s1,mfw

.org 0x001a7fdc
	addiu  s1,s1,mfw

;.org 0x001a8380  
	;l;i t4,mfw ; this is an odd one

.org 0x001a868c  
	addiu  s1,s1,mfw

.org 0x001e7738  
	addiu  s1,s1,mfw

.org 0x001e7780 
	addiu s1,s1,mfw

.org 0x001fb15c  
	li    s4,mfw

.org 0x001fcb80  
	li     a3,mfw

.org 0x001fcc18  
	li     a3,mfw


.org 0x001b47c4  
	li     t1,mfw

.org 0x001b47cc  
	li     v0,mfw







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


.definelabel	char_pointer, 0x0027bbc0
.definelabel	char_offset, 0x0027bbd0

.definelabel	font_color, 0x2615c8
.definelabel	font_color_u, 0x26
.definelabel	font_color_l, 0x15c8


shadow_x equ 0x28
shadow_y equ 0x14
text_padding equ 2
base_x equ 0x330
base_y equ 0xAA ;AD
;font_width equ 0x160	 ; kerning
font_spacing equ 0xD ; newline spacing

white  equ 0x7FFFFFFF
black  equ 0x7F000000
yellow equ 0x7F00FFFF

curr_x equ  s4
newlines equ v1
gpu_call equ s0


.org draw_dialogue_char_start
.area draw_dialogue_char_end - draw_dialogue_char_start,0
	j font_loop
	nop

after_text_loop:
	addiu v1, v1, text_padding<<4	; add padding space to every character
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
	
	la a0, texel_width  ;-
	j func_vwf			; v1 = char width
	nop					;-

texel_width:
	addiu	a1,a2,0x16	; a1 = v_bottom
	sll		a3,a3,0x04	; a3 = u_gpu
	addu	a0,a3,v1	; a0 = u_gpu_right
	sll		a1,a1,0x04	; a1 = v_gpu_bottom
	;sll		a0,a0,0x04  ; a0 = u_gpu_right

	move v0, a3					; v0 = u_gpu
	sll	v1,a2,0x04				; a2 = v_gpu
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
	

	;addiu	v0,0x160			; v0 = x_right + frame_buffer_x aka x_gpu_right
	
	move a1, v0			;a1 = x_gpu
	
	la a0, x_right 		;-
	j func_vwf			; v1 = char width
	nop					;-
	
	
x_right:
	move v0, a1			;v0 = x_gpu
	move a2, v1			;a2 = char_width
	addu v0, v1			;v0 = x_gpu + char_width AKA x_gpu_right
	sh	v0,0x20(gpu_call)	; STORE x_gpu_right
	addiu 	v0, -shadow_x
	sh		v0, 0x48(gpu_call)	; STORE x_gpu_right SHADOW
	subu	v0, a2
	sh v0, 0x38(gpu_call)	; STORE x_gpu SHADOW

	addiu	gpu_call,0x50	; gpu_cursor += 0x50
	
	la a0, after_text_loop
	j	func_vwf
	nop

	

.org func_vwf
	;vwf, v1 gets width. assume a0 is return address 
	
	la v0, char_pointer		;v0 = &text_base
	lw v1, 0x10(v0)			;v1 = char_offset/2
	sll v1, v1, 0x1			;v1 = char_offset
	lw v0, 0x0(v0)			;v0 = text_base
	addu v0, v1, v0			;v0 = char offset + text_base aka &char
	lh 	v0, 0x0(v0)			;v0 = *&char = char
	
	la v1, vwf_table		;v1 = &vwf_table
	addu v1, v1, v0			;v1 = &vwf_table[char]
	lb	v1, 0x0(v1)			;v1 = *&vwf_table[char] = vwf_table[char]
	
	sll v1, v1, 0x4			;1 pixel = 0x10 value
	jr a0
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