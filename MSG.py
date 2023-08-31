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
                #"~diary\\0.bin",
                #"system\\~saveload\\0.bin",
                #"system\\~saveload\\1.bin"

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

MENU_TEXT_EXCEPTIONS = ["いいえ\nはい\n{STOP}", "「\n買いもの\n買う\nやめる\nふつうの牛乳\n40円\nコ一ヒ一牛乳\n40円\nジェットサイダ一\n40円\n」",
                        "「\n買いもの\n買う\nやめる\nチュ一チュ一アイス\n10円\nオレンジガム\n10円\nベ一スボ一ルバ一\n10円\n串イカ\n10円\n串カステラ\n10円\nカツ\n10円\nボ一ルガム\n10円\nクリ一ム\n10円\n梅ジャム・せんべい\n20円\nベビ一スタ一ラ一メン\n20円\n北極バ一\n30円\nタマゴアイス\n30円\nしらゆめ\n50円\nメロンアイス\n50円\nバニラアイス\n50円\n戦艦大和のプラモデル\n350円\n」",
                        "「\n買いもの\n買う\nやめる\nふつうの牛乳\n40円\nコ一ヒ一牛乳\n40円\nジェットサイダ一\n40円\n」",
                        "絵日記\n昆虫採集セット\n{STOP}"]

BUGGED_LINES = {"グレ一ト\n {STOP}"     :"Great\n{STOP}",
                "黒い\n {STOP}"         :"Black\n {STOP}",
                "ハリケ一ン\n{STOP}"    :"Hurricane\n{STOP}"}

ALT_NEWLINE_FILES = ["turi_info.msg", "phot_info.msg", "okan_info.msg", "item_info.msg", "insect_menu.msg",
                     "fishing.msg", "fish_info.msg"]

#Have to copy over: item_info, fish_info

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

def unpackMapMSGVoice(path):
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


def convertRawToText(dict, raw, alt_mode = False):
    '''binary -> string'''
    string = ""
    bytes_read = 0
    
    while True:
        if bytes_read >= len(raw):
            break
        val = int.from_bytes(raw[bytes_read:bytes_read + 2], byteorder="little")
        bytes_read += 2

        if val == 0x8002 and not alt_mode:
            param = int.from_bytes(raw[bytes_read:bytes_read + 2], byteorder="little")
            bytes_read += 2
            char = "{WAIT=" + hex(param) + "}\\n"
        elif val == 0x8002 and alt_mode:
            char = "{BREAK}\\n"
        else:    
            try:
                char = dict[val]
            except KeyError:
                char = "{KEY_ERROR:" + hex(val) + "}"
        
        string += char
    return string

def convertTextToRaw(dict, text, map=-1, raw_insert=-1, alt_mode = False):
    '''string -> binary'''
    buffer = b""

    while True:
        if len(text) == 0:
            break

        if text.startswith("{STOP}") and not alt_mode:
            return buffer + b'\x00\x80'
        elif text.startswith("\n{STOP}") and alt_mode:
            return buffer + b'\x01\x80'
        elif text.startswith("{STOP}") and alt_mode:
            return buffer + b'\x01\x80'
        elif text.startswith("{BREAK}\n"):
            buffer += b'\x02\x80'
            chars_read = 8
        elif text.startswith("{BREAK}"):
            buffer += b'\x02\x80'
            chars_read = 7
        elif text.startswith("{END}\n") and raw_insert != -1:
            buffer += b'\x00\x80'
            chars_read = 6
        elif text.startswith("{END}") and raw_insert != -1:
            buffer += b'\x00\x80'
            chars_read = 5   
        #elif text.startswith("{END}"):
        #    return buffer + b'\x00\x80'
        elif text.startswith("\n") and not alt_mode:
            buffer += b'\x01\x80'
            chars_read = 1
        elif text.startswith("\n") and alt_mode:
            buffer += b'\x01\x80'
            chars_read = 1
        elif text.startswith("{WAIT="):
            endpoint = text.find("}")
            wait_amount = int(text[6:endpoint],16).to_bytes(2, byteorder="little")
            buffer += b'\x02\x80' + wait_amount
            chars_read = endpoint + 2
        else:
            try:

                if map != -1:
                    longest_match = ''
                    
                    for entry in map:
                        common = os.path.commonprefix([entry,text])
                        if common == entry and len(longest_match) < len(common):
                            longest_match = common

                    if longest_match != "":
                        column = map[longest_match][0]
                        row = map[longest_match][1]
                        val = column + row*23
                        buffer += val.to_bytes(2, byteorder="little")
                        chars_read = len(longest_match)
                    else:
                        val = dict[text[0]]
                        buffer += val.to_bytes(2, byteorder="little")
                        chars_read = 1
                else:
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


def convertToPO(path, mode, voice = False):
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

    filename = path.split("\\")[-1]

    table_number = 0
    for table in tables:
        msg_number = 0
        if mode == RAW_MODE:
            table = table[0].split(0x8000.to_bytes(2, byteorder="little"))
        for msg in table:
            
            if len(msg) == 0:
                #Skip null entries
                msg_number += 1
                continue
            
            if voice == True and isVoice(msg):
                text = msg.decode("ascii")
            elif filename in ALT_NEWLINE_FILES:
                text = convertRawToText(dict, msg, alt_mode=True)
            else:
                text = convertRawToText(dict, msg)
            if mode == RAW_MODE:
                text += "{END}"

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

def injectPO(binary_path, po_path, mode, dict, compaction_map = -1):
    '''Convert a PO file into a game binary'''
    fixPO(po_path)
    source = open(binary_path, "rb")
    po = polib.pofile(po_path)
    file_name = binary_path.split("\\")[-1]
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
            
            if entry.msgid in MENU_TEXT_EXCEPTIONS or "M_Z" in po_path:
                raw_line = convertTextToRaw(menu_dict, entry.msgstr)
            elif entry.msgstr.startswith("Simon:"):
                raw_line = convertTextToRaw(simon_dict, entry.msgstr)
            else:
                raw_line = convertTextToRaw(dict, entry.msgstr,compaction_map)
            
            if len(raw_line) % 4 == 2:
                #PADDING
                raw_line += b"\xCD\xCD"
                pass
            map[table_number][1][line_number] = raw_line
        
        bin = repackMap(map)

    elif mode == MSG_MODE:
        msg = splitMsg(binary_path, mode)
        for entry in po:
            if entry.msgid in BUGGED_LINES:
                entry.msgstr = BUGGED_LINES[entry.msgid]

            table_line = entry.comment
            split_table = table_line.split("-")
            table_number = int(split_table[0].split(":")[1])
            line_number = int(split_table[1].split(":")[1])

            if entry.msgstr == "":
                continue
              
            if file_name in ALT_NEWLINE_FILES:
                raw_line = convertTextToRaw(menu_dict, entry.msgstr, alt_mode=True)
            elif file_name in MENU_FONT_FILES or entry.msgid in MENU_TEXT_EXCEPTIONS:
                raw_line = convertTextToRaw(menu_dict, entry.msgstr)
            else:
                raw_line = convertTextToRaw(dict, entry.msgstr,compaction_map)
            if len(raw_line) % 4 == 2:
                #PADDING
                raw_line += b"\xCD\xCD"
                pass
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
            
            if  entry.msgid in MENU_TEXT_EXCEPTIONS:
                raw_line = convertTextToRaw(menu_dict, entry.msgstr)
            else:
                raw_line = convertTextToRaw(dict, entry.msgstr,compaction_map)
            if len(raw_line) % 4 == 2:
                #PADDING
                raw_line += b"\xCD\xCD"
                pass
            msg[line_number] = raw_line

        bin = repackMsg(msg, OFFSET_ONLY_MODE)
    
    elif mode == RAW_MODE:
        bin = convertTextToRaw(dict, po[0].msgstr)
        if len(bin) % 4 == 2:
            #PADDING
            bin += b"\xCD\xCD"
            pass
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



dict2= readFont("MISC\\font.txt",0, EXTRACTION)
dict2[0x8000] = "{END}\n"
dict2[0x8001] = "\n"
def testRaw(hex_string):
    
    text = convertRawToText(dict2, bytes.fromhex(hex_string), alt_mode=False)
    print(text)
    #print(text.count("END"))
    #print(hex_string.count("00 80"))
    return text

def testFind(string):
    dict= readFont("font.txt",0, INSERTION)
    hex = convertTextToRaw(dict, string).hex()
    print(hex)
    return hex


def testTextToHex(string):
    dict= readFont("font-inject.txt",0, INSERTION)
    hex = convertTextToRaw(dict, string).hex()
    print(hex)
    return hex



testRaw("""
""")
#testTextToHex("Testing")

#testFind("はっぴい")

#my_dict = readFont("font-inject.txt", 0, INSERTION)

#print(convertTextToRaw(my_dict, "No", map=-1).hex())



#extractMSGs()
#convertToPO("1.bin", RAW_MODE)
#extractMSGs()

saveload_1 = """Reading memory card...{END}
Formatting memory card...{END}
Loading save...{END}
Saving...{END}
Select a save file{END}
Which file will you save to?{END}
Complete{END}
Save complete{END}
File loaded{END}
No memory card detected.
Proceed anyways?{END}
The memory card is corrupted.
Proceed anyways?{END}
Not enough space to create
save. Proceed anyways?{END}
Proceed with this file?{END}
Do you want to save your
progress so far?{END}
Unformatted memory card detected.
Format now?{END}
Overwrite this file?{END}
Save failed. 92KB of free
space is required to save.{END}
Formatting error!{END}
Save error!{END}
No memory card detected!{END}
Memory card error{END}
No save files detected{END}
Load failed{END}
Memory card ejected{END}
No completed save file detected{END}
Data corrupted{END}
Yes{END}
No{END}
Do you want to continue playing?{END}"""


def genSaveText(txt):
    dict = readFont("font-inject-menus.txt",0, INSERTION)
    print(convertTextToRaw(dict, txt).hex())

def getAllMSGPaths():
    paths = []
    for x in os.walk(MAP_DIR):
        msg_path = os.path.join(x[0], "1.bin")
        if not os.path.exists(msg_path):
            continue
        
        paths.append(msg_path)
    
    return paths
  
def isVoice(msg):
    if len(msg) != 8:
        return False
    
    for x in msg:
        if x < 0x30 or x > 0x39:
            return False
    
    return True

#getAllMSGPaths()

def convertAllVoice():
    paths = getAllMSGPaths()
    
    for path in paths:
        text = convertToPO(path, MAP_MODE, voice = True)
        stem = path.split("\\")[1]
        file = open("VOICE\\MSG\\" + stem + ".txt", "w", encoding="utf8")
        file.write(text)
    return

#convertAllVoice()
#genSaveText("Menu\nWalk")

#genSaveText("Game")
#genSaveText("File")
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
#print(convertTextToRaw(readFont("font.txt",0, INSERTION), "この風景").hex())
#dict = readFont("font.txt",0)
#testMAPs()
#extractMAPs()
#testConvert("")
#print(convertMapFile("MAP_RIP/M_B09200/1.BIN"))