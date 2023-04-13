.ps2
.erroronwarning on

.open "ISO_EDITS\boku2.crc",0
; ################		   Load vwf table				####################
.definelabel crc_hash_offset, 0x16374
.org crc_hash_offset
.import "font_kerning.bin"

.close

.open "ISO_EDITS\scps_150.26", 0xFF000

; ################         Enable debug mode            ####################
.org 0x020a970
	lui 	a0,0x28
.org 0x20a978
	addiu	a0, a0, -0x11b0


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


; ################		   Native Horizontal text fixes

mfw equ 0xa ;Menu font width

; Hori text texel 23->22 fix
.org 0x018077c					;Actual Menus texel width
	addiu v1, a2, 0x16
.org 0x0180794					;Actual Menus texel height
	addiu v0, a0, 0x16
; Char H/W 23->22 fix
.org 0x01807d0 					;Actual Menus glyph width
	addiu  v1,s2, 0x16
.org 0x01807e4					;Actual Menus glyph height
	addiu  v1,s3, 0x16

;Insect baselines

insect_baseline equ 0x18
vert_menu_y_dist equ 0xF

.org 0x001f6434	;digit 1	Y pos
	li a1, insect_baseline

.org 0x01f6450		;m/	Y pos
	li a2, insect_baseline - 2

.org 0x01f6484		;digit 2	Y pos
	li a1, insect_baseline

.org 0x01f649c		;d	Y pos
	li a2, insect_baseline

.org 0x01f64b0		;caught on	Y pos
	li a2, insect_baseline

.org 0x01F617c		
	li a2, -1		;King/Big tertiary
	li a0, 0x142	;King X pos
	li a1, 0x12		;King Y pos
	
.org 0x01F61A4		
	li a0, 0x136	;Big X pos
	li a1, 0x14		;Big Y pos

.org 0x01F6180		;Rare Star Y pos
	li a1, 0x12

;Shops

.org 0x155f80		;Shop price kerning
	addiu s3,s2, -mfw - 2

;Insects

;Keep/Release options vert->hori

.org 0x1f6688
	li a3,0

.org 0x1f669c
	li a3,0

;Release X pos
.org 0x001f6690
	li a1, 0x1a6

;Keep/Release text box bg
.org 0x0027af08
	.word 0x198		;x
	.word 0x110		;y
	.word 0xb0		;width
	.word 0x22		;height

;Keep/Release cursor pos
.org 0x27af48
	.word 0x1b2		;Release x
	.word 0xEC		;Release Y
	.word 0x210		;Keep x
	.word 0xEC		;Keep Y
	
;Insect Kit

.org 0x001E9EF8		;"Caught on" X
	li a1, 0x13b

.org 0x001e9e40		;Month digit X
	li a0, 0x1a0

.org 0x001e9e68		;/ X
	li a1, 0x1ac

.org 0x001e9e90		;Day digit tens X
	li v0, 0x1c3

.org 0x001e9eb4		;Day digit ones X
	li a0, 0x1d0	

.org 0x001e9f94		;Rare star Y
	li a1, 0x170

.org 0x001E9F60		;BIG Y
	li a1, 0x190

.org 0x001e9f28		;KING Y
	li a1, 0x190

;Insect cage full

.org 0x0027af28		;BG
	.word 0x60		;x
	.word 0x40		;y
	.word 0x1bc		;W
	.word 0xa0		;H

.org 0x001f67b0		;vert to hori
	li a3, 0
.org 0x001f67c4
	li a3, 0
.org 0x001f67d8
	li a3, 0

.org 0x001f67a4		;Cage is full header text
	li a1, 0xec		;Y
	li a2, 0x58		;X

.org 0x001f67cc		;Pocket it
	li a1, 0x7c		;X
	li a2, 0xb0		;Y

.org 0x001F67B8		;Let it go
	li a1, 0x1A0	;X
	li a2, 0xb0		;Y

.org 0x0027af58		;cursor
	.word 0xb0		;Pocket it X
	.word 0x80		;Pocket it Y
	.word 0x1b8		;Let it go X
	.word 0x80		;Let it go Y
	
;Insect tutorial

.org 0x001EBF94		;Inject tutorial vert->hori
	li t1, 0x0

.org 0x27a210		;Inject tutorial coords
	.word 0x40		;X
	.word 0x194		;Y

.org 0x27a198		;Inject tutorial BG width
	.word 0xf8

.org 0x27a208		;Inject tutorial 2 coords
	.word 0x40		;X
	.word 0x194		;Y

.org 0x27a188		;Inject tutorial 2 BG width
	.word 0xf8

;Insect delete confirmation
.org 0x027a1c0		
	.word 0x1e8		;BG coords x
	.word 0x1a0		;Y
	.word 0xe0		;W
	.word 0xB0		;H

.org 0x27a258		;cursor
	.word 0x20c		;No X
	.word 0x1e4		;No Y
	.word 0x26a		;Yes X
	.word 0x1e4		;Yes Y

.org 0x001EC0A0		;Yes verti->hori 
	li a3, 0x0

.org 0x001ec0c8		;No verti->hori
	li a3, 0x0

.org 0x001EC084		;Yes/No Y
	li s2, 0x212

.org 0x001ec08c		;Yes X
	li a1, 0x274

.org 0x0027a228		;Discard bug? X
	.word 0x200

;Insect blue notes screen

.org 0x001F8AEC		;Fix letter alpha mess
	li a3, 0x7f

.org 0x001F8Ad8		;Fix letter alpha mess
	li a3, 0x7f

.org 0x001F8C5C		;Nudge bug gfx up
	addiu a1,s0,0x3C

.org 0x001F8C90		;Nudge bug gfx up
	addiu a1,s0,0x3C

;Insect box screen

.org 0x001fc2e4		;Rarity star Y
	li a1, 0x12

.org 0x1fc330		;/ X
	li a1, 0x22E

.org 0x1fc314		;month digit X
	li a0, 0x224

.org 0x01fc36c		;day digit 2 X
	li a0, 0x249

.org 0x001fc394		;day digit 1 X
	li a0, 0x256

.org 0x001fc3cc		;caught on X
	li a1, 0x1c0

.org 0x001fc4e0		;Big Y
	li a1, 0x14

.org 0x001fc4bc		;King Y
	li a1, 0x14

.org 0x001E9D18		;mm text mess fix
	addiu a3, s2, -1

;Insect Cage


;Insect name count adjust
.org 0x01FADFC
	li 	v1, mfw

;Insect Caught text
.org 0x01f64ac
	addiu a1,zero,0x1C0

;Insect month digit
.org 0x01F6430
	li a0, 0x224
;Insect date digit
.org 0x01F6480
	li a0,0x256

;Insect date digit 2
.org 0x01f6464
	li a0, 0x249

;Insect month
.org 0x01f644c
	li a1,0x233

;Insect date
.org 0x01f6498
	li a1,0x264

; Hikari Yes/no text X coords
.org 0x2615e0	;No
	.word 0x114

.org 0x2615e8	;Yes
	.word 0x152

; Hikari Yes/No verti->hori
.org 0x180a04
	addu a0, a3

; Hikari Yes/No kerning
.org 0x1809c0
	li a3, mfw

; Hikari text box height
.org 0x27bbe4
	.word 0x60

; Hikari cursor point direction
.org 0x001f4828
	li a0, 0x2		;2 is down, 0 is right

; Hikari No cursor X
.org 0x27bc18
	.word 0x108

; Hikari No cursor Y
.org 0x27bc1C
	.word 0x60

; Hikari Yes cursor X
.org 0x27bc20
	.word 0x14C

; Hikari No cursor Y
.org 0x27bc24
	.word 0x60

;Continue Screen

.org 0x26ddd4		;colon X
	.halfword 0x10e



; Dinner quiz

.org 0x0027bc08		;bg x y w h 
	.word 0x20
	.word 0x20
	.word 0x240
	.word 0x78

.org 0x002616a0		;quiz options
	.word 0x30		;Left X
	.word 0x46		;Left Y
	.word 0xe0		;Mid X
	.word 0x5c		;Mid Y
	.word 0x180		;Right X
	.word 0x46		;Right Y

.org 0x0027bcd0		;Cursor
	.word 0x2D		;Left X
	.word 0x14		;Left Y
	.word 0xe0		;Mid X
	.word 0x28		;Mid Y
	.word 0x180		;Right X
	.word 0x14		;Right Y

; Discard bug

.org 0x001ec044		
	li a3, 0x0		;Yes verti to hori
.org 0x001ec064
	li a3, 0x0		;No verti to hori

.org 0x001EC038		;Yes X
	li a1, 0x160

.org 0x0027a220		;Label coords
	.word 0xe8		;X
	.word 0x44		;Y

.org 0x0027a1b0		;BG X Y W H
	.word 0xd0
	.word 0x30
	.word 0xe0
	.word 0x90

.org 0x0027a248		;Cursor
	.word 0xf4		;No X
	.word 0x64		;No Y
	.word 0x156		;Yes X
	.word 0x64		;Yes Y

;Done fishing

.org 0x29ab80
	.word 0x100		;Header text X
	.word 0x44		;Header Y

.org 0x1ada60		;Yes
	li a1, 0x160	;X
	li a2, 0x96		;Y

.org 0x001ada70		;verti to hori
	li t0, 0		;option 1
.org 0x001ada88
	li t0, 0		;option 2
.org 0x1ada54
	li t2, 0		;header

.org 0x001B35D4		;cursor no x
	addiu a0, 0xf4
.org 0x001B35B8		;cursor yes x
	li v1, 0x62

.org 0x29aaf0		;bg x y w h
	.word 0xd0
	.word 0x28
	.word 0xe0
	.word 0x98

;Fishing commence

.org 0x001ADAA4		;Verti to hori
	li t0, 0x0
.org 0x001adabc
	li t0, 0x0
.org 0x001ADA54
	li t2, 0x0

.org 0x001ada94		;Yes
	li a1, 0x176	;X
	li a2, 0xc8		;Y

.org 0x001adaac		;No
	li a1, 0xf4		;X
	li a2, 0xc8		;Y

.org 0x0029ab88		;Header
	.word 0xa0		;X
	.word 0x30		;Y

.org 0x0029ab00		;BG X Y W H
	.word 0x84
	.word 0x18
	.word 0x188
	.word 0xe0

.org 0x001B217C		;Cursor
	li v1, 0x88		;X dist
	li a1, 0x98		;X base
.org 0x001B2198
	addiu a0, 0xe4	;Y

; Underwater Text

.org 0x0019d290
	addiu s3, mfw	;Vert to hori

.org 0x0019d210		;Whiten text
	addiu a0, 0x255	
	addiu a1, 0x255
	addiu a2, 0x255


.org 0x0019D774
	li a0, 0x40		;Line 1 X
	li a1, 0x160	;Line 1 Y
.org 0x0019d848
	li a0, 0x40		;Line 1 X
.skip 4
	li a1, 0x160	;Line 1 Y
	

.org 0x0019d7fc
	li a0, 0x40			;Line 2 X
	li a1, 0x160 + 0x10	;Line 2 Y
.org 0x0019d7c8
	li a0, 0x40			;Line 2 X
	li a1, 0x160 + 0x10	;Line 2 Y
.org 0x0019d8a0
	li a0, 0x40			;Line 2 X
	li a1, 0x160 + 0x10	;Line 2 Y
.org 0x0019d8d4
	li a0, 0x40			;Line 2 X
	li a1, 0x160 + 0x10	;Line 2 Y

.org 0x0019d7e0
	li a0, 0x40			;Line 3 X
	li a1, 0x160 + 0x20	;Line 3 Y 
.org 0x0019d8b8
	li a0, 0x40			;Line 3 X
	li a1, 0x160 + 0x20	;Line 3 Y 

;Continue/Data load screen

.org 0x001A7B14
	li s1, 0x15c		;No X

.org 0x001A7A3C
	li s1, 0x100		;Yes X

;Diary/Bug kit

.org 0x00261620		;Picture diary coords
	.word 0x66		;x
	.word 0x7a		;y
	.word 0x14c		;Insect kit X
	.word 0x7a		;Y

.org 0x0027bc58		;Picture diary cursor
	.word 0x90		;X
	.word 0x48		;Y
					;Insect kit cursor
	.word 0x19c		;x
	.word 0x48		;Y

.org 0x0027bbe8			;BG
	.word 0x40			;X
	.word 0x64			;Y
	.word 0x1fe			;W
	.word 0x42			;H

;Diary save with label

.org 0x0027bd00			;Cursor
	.word 0xbc			;No X
	.word 0x7a			;No Y
	.word 0x1c4			;Yes X
	.word 0x7a			;Yes Y

.org 0x002616e0			;Labels
	.word 0xf4			;No X
	.word 0x74			;No Y
	.word 0x178			;Yes X
	.word 0x74			;Yes Y
	.word 0x9e			;Header X
	.word 0x2c			;Header Y


;Sumo Boku side

.org 0x001C6DD0			;Caught on
	li a1, 0x32d		;X

.org 0x001C6D30			;Month digit
	li a0, 0x390		;X

.org 0x001C6D54			;Month "/"
	li a1, 0x3a0		;X

.org 0x001C6D84			;Date tens
	li v0, 0x3aa		;X

.org 0x001C6DAC			;Date ones
	li a0, 0x3ba		;X

.org 0x001C6FB8			;Lv.
	li a0, 0x296		;Red X
.org 0x001c6fcc			
	addiu a1, 0xde		;Red Y
.org 0x001c7034
	li a0, 0x296		;White X
.org 0x001c7048
	addiu a1, 0xde		;White Y

.org 0x001c6fdc			;level digit
	li v0, 0x2b8		;Red X
.org 0x001c7058
	lu v0, 0x2b8		;White X

;Sumo opponent side

.org 0x001c7670			;Skill
	addiu a1, 0x42E		;X

.org 0x001c7740			;LV
	li a1, 0xde			;White Y
.org 0x001c76c0
	li a1, 0xde			;Red Y

.org 0x001C777C			;Level digit
	addiu a1, 0x48a		;White X
.org 0x001c76fc
	addiu a1, a1, 0x48a


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;Speculation follows
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Hori text kerning updates

.org 0x0155e94 
	addiu s2,s2,mfw

.org 0x155ee8
	addiu s2,s2,mfw

.org 0x0156044  
	addiu s2,s2,-mfw

.org 0x0156098
	addiu s2,s2,-mfw

.org 0x0015a4bc				;Vertical text newline distance
	li v1,mfw + 3

.org 0x015a4c4				
	li v0,vert_menu_y_dist	;Vertical text character Y distance
	li v1,mfw				;Horizontal Insect Text X distance
	li v0,0x14				;Horizontal Insect Text Y distance

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
	li     v0,0xb


; ################         Main Dialogue text hack             ####################
.definelabel 	draw_dialogue, 0x001fdcb0
.definelabel vwf_table, 0x0712b24 ;#0x002a1968 ;0xd0 bytes of free space
.definelabel func_vwf, 0x028eb34
.definelabel text_loop_space, 0x00290538 ;free debug text space

.definelabel 	get_fb_y, 0x0012D3C8
.definelabel 	get_fb_x, 0x0012D390
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


shadow_x equ 0x20
shadow_y equ 0x10
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
	lbu	v1, 0x0(v1)			;v1 = *&vwf_table[char] = vwf_table[char]
	
	sll v1, v1, 0x4			;1 pixel = 0x10 value
	jr a0					;return
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