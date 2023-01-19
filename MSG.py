import os
import shutil
from pathlib import Path
import resource
import polib

MAP_DIR = "MAP_RIP"
MAP_SCRIPT_DIR = "SCRIPT/MAP"

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

INSERTION = 0
EXTRACTION = 1

#po insertion modes
MAP_MODE = 0 #Multi-table file
MSG_MODE = 1 #Single-table file

NULL_ENTRY = -1

class MAP:
    def __init__(self):
        self.this = "ok"

class MSG:
    def __init__(self, lines):
        self.lines = lines
        

def unpackMapMSG(path):
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
        msg = readMSG(path, tableOffset, tableSize)
        msgs.append(msg)
    f.close()

    return msgs

def readMSG(filepath, offset, tableSize):
    f = open(filepath, 'rb')
    f.seek(offset)
    msgs = []
    starts = []
    n_entries = resource.readInt(f)

    #Get line starts
    for x in range(n_entries):
        f.seek(offset + 4 + x*0x4)
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
    buffer = b""

    while True:
        if len(text) == 0:
            break

        if text.startswith("{STOP}"):
            return buffer
        #elif text.startswith("{END}"):
        #    return buffer + b'\x00\x80'
        elif text.startswith("\n"):
            buffer += b'\x01\x80'
            chars_read = 2
        elif text.startswith("{WAIT="):
            endpoint = text.find("}")
            wait_amount = int(text[6:endpoint],16).to_bytes(2, byteorder="little")
            buffer += b'\x02\x80' + wait_amount
            chars_read = endpoint + 3
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


def testConvert(hex):
    dict = readFont("font.txt",0, EXTRACTION)
    dict[0x8001] = "\n"
    dict[0x8000] = "{END}\n"
    dict[0xcdcd] = "" #Pads to align(4)

    text = convertRawToText(dict, bytes.fromhex(hex))
    print(text)
    return

def addComments(text):
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

def convertMapFilePO(path):

    dict = readFont("font.txt",0, EXTRACTION)
    dict[0x8001] = "\\n"
    dict[0x8000] = "{END}"
    dict[0xcdcd] = "" #Pads to align(4)
    tables = unpackMapMSG(path)
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
            text = convertMapFilePO(bin_path)
            
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

def fixPO(path):
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
            

def injectPO2(binary_path, po_path, mode, dict):
    #TODO
    
    fixPO(po_path)
    source = open(binary_path, "rb")
    po = polib.pofile(po_path)

    for entry in po:
        table_line = entry.comment
        split_table = table_line.split("-")
        table_number = int(split_table[0].split(":")[1])
        line_number = int(split_table[1].split(":")[1])

        if entry.msgstr == "":
            continue

        raw_line = convertTextToRaw(dict, entry.msgstr)
        
        if mode == MAP_MODE:
            source.seek(4 + table_number*0xC + 4)
            table_size = resource.readShort(source)
            source.seek(4 + table_number*0xC + 8)
            table_offset = resource.readInt(source)
            source.seek(table_offset)
            n_table_entries = resource.readInt(source)
            source.seek(table_offset + 4 + 4*line_number)
            line_offset = resource.readInt(source)

            #Get difference in size
            if line_number == n_table_entries - 1:
                line_difference = len(raw_line) - (table_size - line_offset)
            else:
                for x in range(n_table_entries - line_number - 1):
                    source.seek(table_offset + 4 + 4*line_number + 4*x)
                    next_offset = resource.readInt(source)
                    
                    if x == n_table_entries - line_number - 2 and next_offset == 0:
                        line_difference = len(raw_line) - (table_size - line_offset)
                    elif next_offset == 0:
                        continue
                    else:
                        line_difference = len(raw_line) - (next_offset - line_offset)
            
            source.seek(table_offset + 4 + 4*line_number + 4*x)

            source.seek()
        
    return

def repackMap(map):
    msgs = []
    n_entries = len(map)
    header_buffer = n_entries.to_bytes(4, "little")
    msg_buffer = b''

    msg_offset = 4 + n_entries * 0xC
    for x in range(len(map)):
        msg = repackMsg(map[x][1])

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

def repackMsg(msg):
    n_lines = len(msg)
    header = n_lines.to_bytes(4, "little")
    
    lines_offset = 4 + n_lines*4
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

def injectPO(binary_path, po_path, mode, dict):
    fixPO(po_path)
    source = open(binary_path, "rb")
    po = polib.pofile(po_path)

    if mode == MAP_MODE:
        map = splitMap(binary_path)
        for entry in po:
            table_line = entry.comment
            split_table = table_line.split("-")
            table_number = int(split_table[0].split(":")[1])
            line_number = int(split_table[1].split(":")[1])

            if entry.msgstr == "":
                continue
            
            raw_line = convertTextToRaw(dict, entry.msgstr)

            map[table_number][1][line_number] = raw_line
        
        raw_map = repackMap(map)
            

    elif mode == MSG_MODE:
        msg = splitMsg(binary_path)
        for entry in po:
            table_line = entry.comment
            line_number = int(table_line.split(":")[1])

            if entry.msgstr == "":
                continue
            
            raw_line = convertTextToRaw(dict, entry.msgstr)

            msg[line_number] = raw_line
        raw_msg = repackMsg(msg)

def testMAPs():
    for root, subdirectories, files in os.walk(MAP_DIR):
        for file in files:
            if file != "1.bin":
                continue

            bin_path = os.path.join(root, file)
            text = convertMapFilePO(bin_path)
            
            if len(text) == 0:
                continue
    return


m = splitMap("MAP_RIP/M_B09200/1.BIN")
n = repackMap(m)
#print(len(n))
#print(n.hex())
#injectPO("binary_path", "boku-no-natsuyasumi-2/m_a01000/MAP/en/M_A01000.po")
#convertTextToRaw(readFont("font.txt",0, INSERTION), "『天井近くまで高く{WAIT=0x1190}\\n積みあげられた\\n お布団の山がある\\n なんだかくずれてきそうだ』{STOP}")
#dict = readFont("font.txt",0)
#testMAPs()
#extractMAPs()
#testConvert("")
#print(convertMapFile("MAP_RIP/M_B09200/1.BIN"))