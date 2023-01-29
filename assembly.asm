.psx
.erroronwarning on




.open "ISO_EDITS\scps_150.26", 0xFF000

; ################         Removing the CRC Check            ####################
.org 0x1bff98
	nop
	ori v0, zero, 0x0


.close