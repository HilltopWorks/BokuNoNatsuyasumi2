import os
import shutil
from pathlib import Path
import resource
import polib

MAP_DIR = "MAP_RIP"
MAP_SCRIPT_DIR = "SCRIPT/MAP"

IMG_DIR = "IMG_RIP"
IMG_SCRIPT_DIR ="SCRIPT/IMG" 

false_positives = ['  {STOP}', '、 輪{STOP}', '、 ♂{STOP}', '゜ ;?{STOP}', '、 路{STOP}', '、 ユ{STOP}', '、 告{STOP}', '゜ マ告{STOP}', '、 航{STOP}', '、 ム{STOP}',
'゜ 路マ{STOP}', '゜ マユ{STOP}', ', マ値修{STOP}', '、 修{STOP}', '. マ値修゛{STOP}', '、 狭{STOP}', '゜ 狭ユ{STOP}', '、 ゛{STOP}', '、 蒸{STOP}', '、 ゜{STOP}', '゜ メ辞{STOP}', '、 辞{STOP}', '、 勘{STOP}', '゜ 勘詳{STOP}',
'・ 的狭ユ;?{STOP}', '、 マ{STOP}', '゜ ゜詳{STOP}', '、 ,{STOP}', '゜ 的商{STOP}', '゜ 商マ{STOP}', '、 商{STOP}', '゜ 商!{STOP}', '、 戻{STOP}', '、 働{STOP}', '゜ 的働{STOP}', '゜ 戻マ{STOP}', '゜ 戻的{STOP}', '、 然{STOP}',
'、 ワ{STOP}', '・ 蒸航ム名修{STOP}', '゜ ワ詳{STOP}', ',  詳ワ{STOP}', '゜ ワ゛{STOP}', ', 蒸航ム{STOP}', '・ 蒸航、ム?{STOP}', ', 蒸ム?{STOP}', '、 ÷{STOP}', '、 、{STOP}', '、 !{STOP}',
'゜ ムマ{STOP}', '゜ 詳航{STOP}', '、 的{STOP}', '情↓ 二{STOP}', '、 詳{STOP}', '゜ 、詳{STOP}', '、 ;{STOP}', ', 的狭ユ{STOP}', '、 ～{STOP}', ', 345{STOP}', '、 モ{STOP}', '、 ・{STOP}', '゜ ・詳{STOP}', ', ・!詳{STOP}',
'゜ ・!{STOP}', '、 ―{STOP}', '゜ ―…{STOP}', ',  詳―{STOP}', '゜ 詳―{STOP}', '! ミ゜;値?ユ_々―{STOP}', ', ワ輪詳{STOP}', ', 詳ワ輪{STOP}', '゜ 詳ワ{STOP}', '、 .{STOP}', '、 ±{STOP}', '゜  々{STOP}', '、 ル{STOP}', '、 >{STOP}',
'、 ={STOP}', '、 <{STOP}', '、 「{STOP}', ', 的々辞{STOP}', '. 々辞的詳{STOP}', '゜ 辞辞{STOP}', '゜ 辞詳{STOP}', '゜ 的辞{STOP}', '. ×【】+{STOP}', '、 有{STOP}', '゜ ゛詳{STOP}', '.  々±詳{STOP}', ', 々辞的{STOP}', 
'、 全{STOP}', '゜ ーマ{STOP}', '、 ー{STOP}', '、 —{STOP}', '゜ —マ{STOP}', '゜ —ヤ{STOP}', '、 ヤ{STOP}', '、 :{STOP}', '゜ :マ{STOP}', '゜ : {STOP}', '゜ 的ヤ{STOP}', '゜ ヤ的{STOP}', '゜ :輪{STOP}', '゜ 儲力{STOP}',
'゜ ヤマ{STOP}', '、  {STOP}', '、 力{STOP}', '、 郎{STOP}', '、 勝{STOP}', '゜ ～郎{STOP}', '゜ 怖勝{STOP}', '゜ 輪勝{STOP}', '゜ ラ～{STOP}', '゜  詳{STOP}', '、 』{STOP}', '、 儲{STOP}', '、 …{STOP}', '゜ _ラ{STOP}',
'、 々{STOP}', '゜ ?ユ{STOP}', '、 警{STOP}', '、 /{STOP}', '゜ /詳{STOP}', ', 々 ゛{STOP}', '゜ 詳±{STOP}', '゜  警{STOP}', '. ↓012{STOP}', '゜ !ョ{STOP}', '産伸儲;#労汽、二 {STOP}']

SJIS_FILES = ["system\\~saveload\\2.bin"]

OFFSET_ONLY_MSG_FILES = [
                        "data\\map\\evt\\~on_mem_event\\2.bin",
                        "data\\map\\evt\\~on_mem_event\\3.bin",
                        "data\\map\\evt\\~on_mem_event\\4.bin",
                        "data\\map\\evt\\~on_mem_event\\5.bin"
                        ]

RAW_MSG_FILES = [
                "~diary\\0.bin",
                "system\\~saveload\\0.bin",
                "system\\~saveload\\1.bin"

                ]

IMG_MSG_FILES = ["fish\\fishing.msg",
                "system\\system.msg",
                "system\\eat\\eat.msg",
                "system\\namemsg\\namemsg.msg",
                "system\\namemsg\\quiz.msg",
                "system\\submenu\\memories.msg",
                "system\\submenu\\fish\\fish_info.msg",
                "system\\submenu\\fish\\fish_menu.msg",
                "system\\submenu\\fish\\fish_name.msg",
                "system\\submenu\\fish\\turi_info.msg",
                "system\\submenu\\insect\\insect_cage.msg",
                "system\\submenu\\insect\\insect_menu.msg",
                "system\\submenu\\insect\\insect_name.msg",
                "system\\submenu\\insect\\memo_name.msg",
                "system\\submenu\\insect\\nick_name_a.msg",
                "system\\submenu\\insect\\nick_name_b.msg",
                "system\\submenu\\insect\\nick_name_menu.msg",
                "system\\submenu\\item\\item.msg",
                "system\\submenu\\item\\item_info.msg",
                "system\\submenu\\item\\item_name.msg",
                "system\\submenu\\item\\okan_info.msg",
                "system\\submenu\\item\\phot_info.msg",
                "system\\submenu\\msg\\config\\config.msg",
                "system\\wrestling\\msg\\technique.msg"
             ]

MENU_FONT_FILES = [ "fishing.msg","system.msg", "namemsg.msg", "quiz.msg", "memories.msg", "fish_menu.msg", "fish_name.msg",
                    "insect_cage.msg", "insect_menu.msg", "insect_name.msg", "memo_name.msg", "nick_name_a.msg", "nick_name_b.msg", 
                    "nick_name_menu.msg","item.msg","item_info.msg","item_name.msg","okan_info.msg","phot_info.msg",
                    "config.msg","technique.msg"]

#Dictionary modes
INSERTION = 0
EXTRACTION = 1

#po insertion modes
MAP_MODE = 0 #Multi-table file
MSG_MODE = 1 #Single-table file
RAW_MODE = 2
OFFSET_ONLY_MODE = 3 #

NULL_ENTRY = -1



def unpackMapMSG(path):
    '''Converts a binary MAP MSG file into a list of MSG list objects [[Table params],[MSG LIST]]'''
    f = open(path, 'rb')

    numTables = resource.readInt(f)
    msgs = []
    for x in range(numTables):
        f.seek(4 + x*0xC)
        magic1 = resource.readInt(f)
        tableSize = resource.readShort(f)
        magic2 = resource.readShort(f)
        tableOffset = resource.readShort(f)
        f.seek(tableOffset)
        msg = readMSG(path, tableOffset, tableSize, MAP_MODE)
        msgs.append(msg)
    f.close()

    return msgs

def unpackMSG(path, mode = MSG_MODE):
    '''Converts a binary IMG MSG file into a MSG list object '''
    tableSize = os.stat(path).st_size
    msg = readMSG(path, 0, tableSize, mode)
    return msg

def readMSG(filepath, offset, tableSize, mode):
    '''Turns a MSG at given offset into a file and returns list of lines'''
    f = open(filepath, 'rb')
    f.seek(offset)
    msgs = []
    starts = []
    n_entries = resource.readInt(f)

    #Get line starts
    for x in range(n_entries):
        if mode == MAP_MODE or mode == OFFSET_ONLY_MODE:
            f.seek(offset + 4 + x*0x4)
        elif mode == MSG_MODE:
            f.seek(offset + 4 + x*0x8)
        start_offset = resource.readInt(f)
        
        starts.append(start_offset)
    
    #Read each line
    for x in range(n_entries):
        #Skip null entries
        if starts[x] == 0:
            msgs.append('')
            continue

        f.seek(offset + starts[x])
        
        '''if x == n_entries - 1:
            msgs.append(f.read(tableSize - starts[x]))
            break'''

        endFound = False
        for y in range(n_entries - x - 1):
            if starts[x + y + 1] != 0:
                msgs.append(f.read(starts[x + y + 1] - starts[x]))
                endFound = True
                break
        #No more entries left
        if not endFound:
            msgs.append(f.read(tableSize - starts[x]))
    f.close()
    return msgs

def readFont(path, startval, mode):
    '''Converts a font into a TBL dictionary for injection or extraction'''
    font = open(path, "r", encoding="utf-8")
    dict = {}

    index = startval
    while True:
        char = font.read(1)
        #skip newlines
        if char == "\n":
            continue
        #EOF
        if not char:
            break

        if mode == EXTRACTION:
            dict[index] = char
        else:
            dict[char] = index
        index += 1

    return dict


def convertRawToText(dict, raw):
    '''binary -> string'''
    string = ""
    bytes_read = 0
    while True:
        if bytes_read >= len(raw):
            break
        val = int.from_bytes(raw[bytes_read:bytes_read + 2], byteorder="little")
        bytes_read += 2

        if val == 0x8002:
            param = int.from_bytes(raw[bytes_read:bytes_read + 2], byteorder="little")
            bytes_read += 2
            char = "{WAIT=" + hex(param) + "}\\n"
        else:    
            try:
                char = dict[val]
            except KeyError:
                char = "{KEY_ERROR:" + hex(val) + "}"
        
        string += char
    return string

def convertTextToRaw(dict, text):
    '''string -> binary'''
    buffer = b""

    while True:
        if len(text) == 0:
            break

        if text.startswith("{STOP}"):
            return buffer + b'\x00\x80'
        #elif text.startswith("{END}"):
        #    return buffer + b'\x00\x80'
        elif text.startswith("\n"):
            buffer += b'\x01\x80'
            chars_read = 1
        elif text.startswith("{WAIT="):
            endpoint = text.find("}")
            wait_amount = int(text[6:endpoint],16).to_bytes(2, byteorder="little")
            buffer += b'\x02\x80' + wait_amount
            chars_read = endpoint + 2
        else:
            try:
                val = dict[text[0]]
                buffer += val.to_bytes(2, byteorder="little")
                chars_read = 1
            except KeyError:
                error_code = b'\x2E\x00'
                print("INSERTION ERROR!!! CHAR: -" + text[0] + "- in " + text)
                chars_read = 1

        text = text[chars_read:]
    
    return buffer + b'\x00\x80'

#-------------OBSOLETE-----------------
def addComments(text):
    '''OBSOLETED'''
    split_text = text.split("\n")
    buffer = ""
    for x in range(len(split_text)):
        buffer += "///" + split_text[x] + "\\\\\\\n"
    buffer += "///--------------\n"
    for x in range(len(split_text)):
        buffer += split_text[x] + "\n"

    buffer = buffer.rstrip("\n")
    return buffer

def convertMapFile(path):
    '''OBSOLETED'''
    dict = readFont("font.txt",0, EXTRACTION)
    dict[0x8001] = "\n"
    dict[0x8000] = "{END}"
    dict[0xcdcd] = "" #Pads to align(4)
    tables = unpackMapMSG(path)
    buffer = ""
    #out = open("test.txt", 'w', encoding="utf-8" )

    table_number = 0
    for table in tables:
        msg_number = 0
        
        for msg in table:
            if len(msg) == 0:
                #Skip null entries
                msg_number += 1
                continue
            text = convertRawToText(dict, msg)
            
            
            if not text.endswith("{END}") and "KEY_ERROR" in text:
                #Skip malformed strings
                #print("---" + text + "---")
                msg_number += 1
                continue

            if not text.endswith("{END}"):
                #Add terminator to unterminated strings
                text += "{STOP}"

            if text in false_positives:
                #Skip entries that survive previous filters
                msg_number += 1
                continue

            commented = addComments(text)

            buffer += "///Table:" + str(table_number) + "-Line:" + str(msg_number) + "\n"
            buffer += commented + "\n\n"
            #print(text)
            msg_number += 1
        table_number += 1

    
    return buffer
#-----------OBSOLETE END---------------


def convertToPO(path, mode):
    '''Converts binary text file to .PO for Weblate'''
    dict = readFont("font.txt",0, EXTRACTION)
    dict[0x8001] = "\\n"
    dict[0x8000] = "{END}"
    dict[0xcdcd] = "" #Pads to align(4)
    if mode == MAP_MODE:
        tables = unpackMapMSG(path)
    elif mode == MSG_MODE:
        tables = [unpackMSG(path)]
    elif mode == RAW_MODE:
        tables = [[open(path, 'rb').read()]]
    elif mode == OFFSET_ONLY_MODE:
        tables = [unpackMSG(path, mode)]
    else:
        assert False, "UNIDENTIFIED FILE MODE!!!"
    buffer = "msgid \"\"\nmsgstr \"\"\n\"Project-Id-Version: PACKAGE VERSION\\n\"\n\"Language: en\\n\"\n\"MIME-Version: 1.0\\n\"\n\"Content-Type: text/plain; charset=UTF-8\\n\"\n\n"
    #buffer = "#. File " + path + "\n\n"

    line_total = 0

    table_number = 0
    for table in tables:
        msg_number = 0
        
        for msg in table:
            if len(msg) == 0:
                #Skip null entries
                msg_number += 1
                continue
            text = convertRawToText(dict, msg)
            
            
            if not text.endswith("{END}") and "KEY_ERROR" in text:
                #Skip malformed strings
                #print("---" + text + "---")
                msg_number += 1
                continue

            if not text.endswith("{END}"):
                #Add terminator to unterminated strings
                text += "{STOP}"

            if text in false_positives:
                #Skip entries that survive previous filters
                msg_number += 1
                continue

            #commented = addComments(text)
            commented = "msgid \"" + text + "\"\n" + "msgstr \"\""

            commented = commented.replace("{END}","")

            buffer += "#.Table:" + str(table_number) + "-Line:" + str(msg_number) + "\n"
            buffer += commented + "\n\n"
            #print(text)
            msg_number += 1
            line_total += 1
        table_number += 1

    if line_total == 0:
        return ""
    
    return buffer

def extractMAPs():
    '''Converts all text files (file 1's) in all maps to PO files'''
    for root, subdirectories, files in os.walk(MAP_DIR):
        for file in files:
            if file != "1.bin":
                continue

            bin_path = os.path.join(root, file)
            text = convertToPO(bin_path, MAP_MODE)
            
            if len(text) == 0:
                continue

            outpath = os.path.join(MAP_SCRIPT_DIR,"en",root.split("\\")[-1]) + ".po"
            os.makedirs(MAP_SCRIPT_DIR, exist_ok=True)
            outfile = open(outpath, 'w', encoding="utf-8")
            outfile.write(text)
            outfile.close()

            outpath = os.path.join(MAP_SCRIPT_DIR,"en",root.split("\\")[-1]) + ".pot"

            outfile = open(outpath, 'w', encoding="utf-8")
            outfile.write(text)
            outfile.close()
            
    return

def extractMSGs():
    '''Converts all specified .MSG files from IMG into PO's'''
    for msg_path in IMG_MSG_FILES + RAW_MSG_FILES + OFFSET_ONLY_MSG_FILES:
        file_path = os.path.join(IMG_DIR, msg_path)
        
        if msg_path in IMG_MSG_FILES:
            text = convertToPO(file_path, MSG_MODE)
        elif msg_path in RAW_MSG_FILES:
            text = convertToPO(file_path, RAW_MODE)
        elif msg_path in OFFSET_ONLY_MSG_FILES:
            text = convertToPO(file_path, OFFSET_ONLY_MODE)


        if len(text) == 0:
            continue
        outpath = os.path.join(IMG_SCRIPT_DIR,"en",file_path.split("\\", 1)[1]) + ".po"
        outdir = os.path.dirname(outpath)
        os.makedirs(outdir, exist_ok=True)
        outfile = open(outpath, 'w', encoding="utf-8")
        outfile.write(text)
        outfile.close()
        
        outpath = os.path.join(IMG_SCRIPT_DIR,"en",file_path.split("\\", 1)[1]) + ".pot"
        outdir = os.path.dirname(outpath)

        outfile = open(outpath, 'w', encoding="utf-8")
        outfile.write(text)
        outfile.close()

def fixPO(path):
    '''Fixes single space issue with PO files'''
    f = open(path, "r", encoding="utf-8")
    text = f.read()
    text = text.replace("#.Table", "#. Table")
    f.close()
    o = open(path, "w", encoding="utf-8")
    o.write(text)
    o.close()
    return


def findEndpoint(file, offset, n_entries, entry_number, table_size):
    
    return_point = file.tell()
    if entry_number == n_entries - 1:
        return offset + table_size

    for x in range(n_entries - entry_number - 1):
        file.seek(offset + 4 + 4*(entry_number +x + 1))
        next_offset = resource.readInt(file)
        
        if x == n_entries - entry_number - 2 and next_offset == 0:
            file.seek(return_point)
            return offset + table_size
        elif next_offset == 0:
            continue
        else:
            file.seek(return_point)
            return(offset + next_offset)
            

def repackMap(map):

    n_entries = len(map)
    header_buffer = n_entries.to_bytes(4, "little")
    msg_buffer = b''

    msg_offset = 4 + n_entries * 0xC
    for x in range(len(map)):
        msg = repackMsg(map[x][1], MAP_MODE)

        msg_buffer += msg

        map_header = map[x][0]
        #Magic 1
        header_buffer += map_header[0].to_bytes(4,"little")
        #Msg size
        header_buffer += len(msg).to_bytes(2, "little")
        #Magic 2
        header_buffer += map_header[2].to_bytes(2,"little")
        #Msg offset
        header_buffer += msg_offset.to_bytes(4, "little")
        
        msg_offset += len(msg)

    return header_buffer + msg_buffer


#MSG Mode: Offset + size, MAP Mode: Offset
def repackMsg(msg, mode):
    n_lines = len(msg)
    header = n_lines.to_bytes(4, "little")
    
    if mode == MAP_MODE or mode == OFFSET_ONLY_MODE:
        lines_offset = 4 + n_lines*4
    elif mode == MSG_MODE:
        lines_offset = 4 + n_lines*8
        
    lines_buffer = b''
    for x in range(len(msg)):
        if msg[x] == NULL_ENTRY:
            null = 0
            header += null.to_bytes(4, "little")
            continue

        header += lines_offset.to_bytes(4, "little")
        
        #print(lines_offset.to_bytes(4, "little").hex())
        lines_buffer += msg[x]
        line_length = len(msg[x])
        lines_offset += line_length
        if mode == MSG_MODE:
            header += line_length.to_bytes(4, "little")

    return header + lines_buffer

def splitMap(path):
    f = open(path, "rb")

    numTables = resource.readInt(f)
    msgs = []
    for x in range(numTables):
        msg = []
        f.seek(4 + x*0xC)
        magic1 = resource.readInt(f)
        tableSize = resource.readShort(f)
        magic2 = resource.readShort(f)
        tableOffset = resource.readInt(f)
        #Header parameters
        msg.append([magic1,tableSize,magic2, tableOffset])
        #Container for lines
        msg.append([])
        f.seek(tableOffset)
        num_entries = resource.readInt(f)
        for y in range(num_entries):
            f.seek(tableOffset + 4 + y*4)
            entry_offset = resource.readInt(f)
            if entry_offset == 0:
                msg[1].append(NULL_ENTRY)
                continue
            endpoint = findEndpoint(f,tableOffset, num_entries,y,tableSize)

            f.seek(tableOffset + entry_offset)
            rawBin = f.read(endpoint - (tableOffset + entry_offset))
            msg[1].append(rawBin)
        
        
        msgs.append(msg)

    return msgs

def splitMsg(path, mode):
    msg = []
    f = open(path, "rb")

    numLines = resource.readInt(f)

    if mode == MSG_MODE:
        for x in range(numLines):
            f.seek(4 + x*8)
            line_offset = resource.readInt(f)
            line_size = resource.readInt(f)
            f.seek(line_offset)
            line = f.read(line_size)
            msg.append(line)
    elif mode == OFFSET_ONLY_MODE:
        for y in range(numLines):
            f.seek(4 + y*4)
            entry_offset = resource.readInt(f)
            if entry_offset == 0:
                msg.append(NULL_ENTRY)
                continue
            endpoint = findEndpoint(f,0, numLines,y,os.stat(path).st_size)

            f.seek(entry_offset)
            rawBin = f.read(endpoint - entry_offset)
            msg.append(rawBin)

    return msg

simon_dict = readFont("font-inject-simon.txt", 0, INSERTION)
menu_dict = readFont("font-inject-menus.txt", 0, INSERTION)

def injectPO(binary_path, po_path, mode, dict):
    '''Convert a PO file into a game binary'''
    fixPO(po_path)
    source = open(binary_path, "rb")
    po = polib.pofile(po_path)

    all_lines = {}

    for entry in po:
        if entry.msgstr != "":
            all_lines[entry.msgid] = entry.msgstr


    if mode == MAP_MODE:
        map = splitMap(binary_path)
        for entry in po:
            table_line = entry.comment
            split_table = table_line.split("-")
            table_number = int(split_table[0].split(":")[1])
            line_number = int(split_table[1].split(":")[1])

            if entry.msgid in all_lines:
                entry.msgstr = all_lines[entry.msgid]

            if entry.msgstr == "":
                continue
            
            if entry.msgstr.startswith("Simon:"):
                raw_line = convertTextToRaw(simon_dict, entry.msgstr)
            else:
                raw_line = convertTextToRaw(dict, entry.msgstr)
            
            if len(raw_line) % 4 == 2:
                #PADDING
                raw_line += b"\xCD\xCD"
            map[table_number][1][line_number] = raw_line
        
        bin = repackMap(map)

    elif mode == MSG_MODE:
        msg = splitMsg(binary_path, mode)
        for entry in po:
            table_line = entry.comment
            split_table = table_line.split("-")
            table_number = int(split_table[0].split(":")[1])
            line_number = int(split_table[1].split(":")[1])

            if entry.msgstr == "":
                continue
            
            file_name = binary_path.split("\\")[-1]
            if file_name in MENU_FONT_FILES:
                raw_line = convertTextToRaw(menu_dict, entry.msgstr)
            else:
                raw_line = convertTextToRaw(dict, entry.msgstr)
            if len(raw_line) % 4 == 2:
                #PADDING
                raw_line += b"\xCD\xCD"
            msg[line_number] = raw_line

        bin = repackMsg(msg, MSG_MODE)
    elif mode == OFFSET_ONLY_MODE:
        msg = splitMsg(binary_path, mode)
        for entry in po:
            table_line = entry.comment
            split_table = table_line.split("-")
            table_number = int(split_table[0].split(":")[1])
            line_number = int(split_table[1].split(":")[1])

            if entry.msgstr == "":
                continue
            
            raw_line = convertTextToRaw(dict, entry.msgstr)
            if len(raw_line) % 4 == 2:
                #PADDING
                raw_line += b"\xCD\xCD"
            msg[line_number] = raw_line

        bin = repackMsg(msg, OFFSET_ONLY_MODE)
    
    elif mode == RAW_MODE:
        bin = convertTextToRaw(dict, po[0].msgstr)
        if len(bin) % 4 == 2:
            #PADDING
            bin += b"\xCD\xCD"
    source.close()
    out = open(binary_path, 'wb')
    out.write(bin)
    out.close()

def testMAPs():
    for root, subdirectories, files in os.walk(MAP_DIR):
        for file in files:
            if file != "1.bin":
                continue

            bin_path = os.path.join(root, file)
            text = convertToPO(bin_path, MAP_MODE)
            
            if len(text) == 0:
                continue
    return


def testRaw(hex_string):
    dict= readFont("font.txt",0, EXTRACTION)
    dict[0x8000] = "{END}\n"
    dict[0x8001] = "\n"
    print(convertRawToText(dict, bytes.fromhex(hex_string)))

    return





'''testRaw("""
48 01 E8 03 8D 02 9C 00 07 02 32 01 C1 00 DF 04
7E 00 AF 00 88 00 B8 00 77 00 00 80 B7 01 52 04
98 00 8A 00 7C 00 08 00 00 80 00 00 7B 00 07 02
32 01 A0 00 08 00 00 80 00 00 D1 00 0B 01 DB 00
99 00 07 02 32 01 01 80 84 00 BD 00 98 00 75 00
75 00 7C 00 9B 00 08 00 00 80 00 00 B3 00 9A 00
BC 00 00 80 A3 00 BA 00 7D 00 9B 00 00 80 00 00
CD 00 E1 00 CD 00 EC 00 00 80 00 00 35 00 36 00
37 00 38 00 39 00 3A 00 3B 00 3C 00 3D 00 01 80
3E 00 3F 00 40 00 41 00 42 00 43 00 44 00 45 00
46 00 00 80 73 00 75 00 77 00 79 00 7B 00 00 00
7C 00 7E 00 80 00 82 00 84 00 01 80 86 00 88 00
8A 00 8C 00 8E 00 00 00 90 00 92 00 95 00 97 00
99 00 01 80 9B 00 9C 00 9D 00 9E 00 9F 00 00 00
A0 00 A3 00 A6 00 A9 00 AC 00 01 80 AF 00 B0 00
B1 00 B2 00 B3 00 00 00 B5 00 00 00 B7 00 00 00
B9 00 01 80 BA 00 BB 00 BC 00 BD 00 BE 00 00 00
C0 00 00 00 C1 00 00 00 C2 00 01 80 72 00 74 00
76 00 78 00 7A 00 00 00 B4 00 B6 00 B8 00 94 00
00 00 01 80 7D 00 7F 00 81 00 83 00 85 00 00 00
87 00 89 00 8B 00 8D 00 8F 00 01 80 91 00 93 00
96 00 98 00 9A 00 00 00 A1 00 A4 00 A7 00 AA 00
AD 00 01 80 A2 00 A5 00 A8 00 AB 00 AE 00 00 00
08 00 09 00 3E 06 3F 06 40 06 00 80 C4 00 C6 00
C8 00 CA 00 CC 00 00 00 CD 00 CF 00 D1 00 D3 00
D5 00 01 80 D7 00 D9 00 DB 00 DD 00 DF 00 00 00
E1 00 E3 00 E6 00 E8 00 EA 00 01 80 EC 00 ED 00
EE 00 EF 00 F0 00 00 00 F1 00 F4 00 F7 00 FA 00
FD 00 01 80 00 01 01 01 02 01 03 01 04 01 00 00
06 01 00 00 08 01 00 00 0A 01 01 80 0B 01 0C 01
0D 01 0E 01 0F 01 00 00 11 01 00 00 12 01 00 00
13 01 01 80 C3 00 C5 00 C7 00 C9 00 CB 00 00 00
05 01 07 01 09 01 E5 00 00 00 01 80 CE 00 D0 00
D2 00 D4 00 D6 00 00 00 D8 00 DA 00 DC 00 DE 00
E0 00 01 80 E2 00 E4 00 E7 00 E9 00 EB 00 00 00
F2 00 F5 00 F8 00 FB 00 FE 00 01 80 F3 00 F6 00
F9 00 FC 00 FF 00 00 00 1D 00 1E 00 0F 00 2A 00
05 00 00 80 A0 00 75 00 00 00 75 00 75 00 79 00
00 80 00 00




""")'''

#extractMSGs()
#dict = readFont("font.txt",0, INSERTION)
#print(convertTextToRaw(dict, "verything" ).hex())
#injectPO("IMG_RIP_EDITS\\system\\namemsg\\namemsg.msg", "boku-no-natsuyasumi-2\\fishing-msg\\IMG\\en\\system\\namemsg\\namemsg.msg.po", MSG_MODE, dict)
#injectPO("1.bin", "M_A01000.po", MAP_MODE, dict)
#text = convertToPO("1.bin", MAP_MODE)
#print(text)
#extractMAPs()
#m = splitMap("MAP_RIP/M_B09200/1.BIN")
#n = repackMap(m)
#print(len(n))
#print(n.hex())
#injectPO("binary_path", "boku-no-natsuyasumi-2/m_a01000/MAP/en/M_A01000.po")
#convertTextToRaw(readFont("font.txt",0, INSERTION), "『天井近くまで高く{WAIT=0x1190}\\n積みあげられた\\n お布団の山がある\\n なんだかくずれてきそうだ』{STOP}")
#dict = readFont("font.txt",0)
#testMAPs()
#extractMAPs()
#testConvert("")
#print(convertMapFile("MAP_RIP/M_B09200/1.BIN"))