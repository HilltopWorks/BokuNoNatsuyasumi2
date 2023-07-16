import os
import shutil
import resource
import MSG

def getVoiceList():
    XWH_PATH = "IMG_RIP\\SE\\VOICE.xwh"
    ID_START = 0x1FE20
    ID_ENTRIES = 0xFEF
    
    xwh_file = open(XWH_PATH, 'rb')
    xwh_file.seek(ID_START)
    voice_IDs = []
    
    for x in range(ID_ENTRIES):
        next_ID = resource.ReadString(xwh_file)
        voice_IDs.append(next_ID)
        
    return voice_IDs

def createIDWavs():
    WAV_PATH = "MISC\\voice"
    ID_ENTRIES = 0xFEF
    
    voice_ids = getVoiceList()
    
    for x in range(ID_ENTRIES):
        file_name = "voice_" + str(x).zfill(5) + ".wav"
        file_path = os.path.join(WAV_PATH, file_name)
        
        os.makedirs(os.path.join(WAV_PATH, "ID"), exist_ok=True)
        copy_path = os.path.join(WAV_PATH, "ID", str(x).zfill(4) + "_" + voice_ids[x] + ".wav")
        
        shutil.copyfile(file_path, copy_path)
        
    return


EVENT_LABELS = ["POS","INI","IPROG","JMP","JMPM","JMPE","PROG","GO","WALK","RUN","MAP","CMAP","CMAPP","CMWT",
                "BGM","SE","XAMSG","MSG","XA","FLAG","DISP","ANM","BGANM","LOOK","END","AWT","BWT",
                "XWT","DIXA","WIN","WAT","MWT","TIME","IF","DEBUG","FACE","SELECT","MOVIE","LFLAG","WARP",
                "MSGWT","YGO","XSEEK","CMPOS","SWIM","FOOT","SHADOW","CMINI"]

HAS_TEXT = ["XAMSG", "MSG", "SELECT"]
HAS_VOICE = ["XA", "XAMSG"]

inject_dict = MSG.readFont("font-inject.txt", 0, MSG.INSERTION)

def getEvent(id):
    return EVENT_LABELS[id]

def readEvent(file):
    event_ID = resource.readByte(file)
    event_size = resource.readByte(file) * 2
    
    if event_size == 0:
        return None
    event_body = file.read(event_size - 2).hex()
    label = EVENT_LABELS[event_ID] 
    label_id = hex(event_ID) + " "*(4 - len(hex(event_ID))) + " "
    line = label_id  + label + " "*(6 - len(label)) + ": " + event_body
    
    event = {"ID":event_ID, "SIZE":event_size, "BODY":event_body, "STRING": line}
    return event

def readEventList(file_path, offset, size):
    file = open(file_path, 'rb')
    file.seek(offset)
    
    n_entries = resource.readInt(file)
    
    init_blocks = []
    
    for x in range(2):
        file.seek(offset + 4 + x*4)
        block_offset = resource.readInt(file)
        
        block_endpoint = MSG.findEndpoint(file, offset, n_entries, x, size) - offset
        file.seek(offset + block_offset)
        block = file.read(block_endpoint - block_offset)
        init_blocks.append(block)
    
    file.seek(offset)
    endpoint = MSG.findEndpoint(file, offset, n_entries, 2, size)
    
    file.seek(offset + 0xC)
    
    event_start = resource.readInt(file)
    event_end = event_start + size
    
    
    
    n_msg_entries = (n_entries-3)
    event_list = {"FILE":file_path, "N_MSG_ENTRIES":n_msg_entries//2,
                  "OFFSET":offset,"INIT_BLOCKS":init_blocks, "EVENTS":[]}
    
    msg_block = []
    for x in range(n_msg_entries):
        file.seek(offset + 0x10 + 0x4*x)
        msg_offset = resource.readInt(file)
        if msg_offset == 0:
            msg_block.append(b'')
            continue
        
        msg_endpoint = MSG.findEndpoint(file, offset, n_entries, 3 + x, size) - offset
        file.seek(offset + msg_offset)
        block = file.read(msg_endpoint - msg_offset)
        msg_block.append(block)
        
    event_list["MSG_BLOCK"] = msg_block
    
    
    file.seek(offset + event_start)
    while file.tell() < endpoint:
        
        if len(event_list["EVENTS"]) >= 1 and event_list["EVENTS"][-1]["ID"] == 0x18:
            if file.tell() % 4 == 2:
                file.seek(file.tell() + 2)
            
            if file.tell() < endpoint:
                event_list["MSG"] = file.read(endpoint - file.tell())
            break
        event = readEvent(file)
        event_list["EVENTS"].append(event)
    
    
    return event_list

def readMAPEvents(file_path):
    file = open(file_path, 'rb')
    n_entries = resource.readInt(file)
    
    event_lists = []
    for x in range(n_entries):
        file.seek(4 + 0xC*x)
        magic_1 = file.read(4)
        table_size = resource.readShort(file)
        magic_2 = file.read(2)
        table_offset = resource.readInt(file)
        event_list = readEventList(file_path, table_offset, table_size)
        event_list["TABLE_SIZE"] = table_size
        event_list["MAGIC_1"] = magic_1
        event_list["MAGIC_2"] = magic_2
        event_lists.append(event_list)
    return event_lists

def isVoiceID(bytes):
    
    for x in bytes:
        if x >= 0x30 and x <= 0x39:
            continue
        else:
            return False
    
    return True

def logMAPEvent(event_lists):
    os.makedirs("MISC\\voice_logs", exist_ok=True)
    logFile = open("MISC\\voice_logs\\" + str(event_lists[0]["FILE"].split("\\")[1]) +".txt", 'w', encoding="UTF8")
    map = MSG.unpackMapMSG(event_lists[0]["FILE"])
    list_counter = 0
    for list in event_lists:
        logFile.write("\n--- " + list["FILE"] + ":" + hex(list["OFFSET"]) + ":" + str(list_counter)+  " ---\n")
        print("\n--- " + list["FILE"] + ":" + hex(list["OFFSET"]) + " ---\n")
        sub_map = map[list_counter][3:]

        for event in list["EVENTS"]:
            logFile.write(event["STRING"] + "\n")
            
            if EVENT_LABELS[event["ID"]] == "MSG":
                logFile.write( "-REPLACE  = FALSE\n")
                line_number = int(event["BODY"][8:10], 16)
                logFile.write( "-MSG ID   = " +  str(line_number) +   "\n")
                line_text = MSG.testRaw(sub_map[line_number*2 + 1].hex().replace("cdcd", ""))
                logFile.write( "-MSG:" + "\n")
                line_text = line_text.rstrip("\n").replace("\\n", "\n").replace("{END}","")
                logFile.write(line_text + "\n--------------------------\n")

            elif EVENT_LABELS[event["ID"]] == "XAMSG":
                logFile.write( "-REPLACE  = FALSE\n")
                line_number = int(event["BODY"][8:10], 16)
                
                logFile.write( "-MSG ID   = " +  str(line_number) +   "\n")
                line_text = MSG.testRaw(sub_map[line_number*2 + 1].hex().replace("cdcd", ""))
                voice_ID = sub_map[line_number*2].decode("ascii")
                logFile.write( "-VOICE ID = " +voice_ID + "\n")
                logFile.write( "-XAMSG:" + "\n")
                line_text = line_text.rstrip("\n").replace("\\n", "\n").replace("{END}","")
                logFile.write(line_text + "\n--------------------------\n")

            elif EVENT_LABELS[event["ID"]] == "XA":
                logFile.write( "-REPLACE  = FALSE\n")
                line_number = int(event["BODY"][8:10], 16)
                logFile.write( "-MSG ID   = " +  str(line_number) +   "\n")
                voice_ID = sub_map[line_number*2].decode("ascii")
                logFile.write( "-VOICE ID = " +voice_ID + "\n--------------------------\n")

            elif EVENT_LABELS[event["ID"]] == "SELECT":
                logFile.write( "-REPLACE  = FALSE\n")
                line_number = int(event["BODY"][4:6], 16)
                logFile.write( "-MSG ID   = " +  str(line_number) +   "\n")
                line_text = MSG.testRaw(sub_map[line_number*2 + 1].hex().replace("cdcd", ""))
                logFile.write( "-SELECT:" + "\n")
                line_text = line_text.rstrip("\n").replace("\\n", "\n")
                if not line_text.endswith("{END}"):
                    line_text += "{STOP}"
                logFile.write(line_text + "\n--------------------------\n")
        list_counter += 1
                
    return

def logAllMapEvents():
    dirs = os.walk("MAP_RIP")
    
    for dir in dirs.__next__()[1]:
        bin_path = os.path.join("MAP_RIP", dir, "1.bin")
        if os.path.exists(bin_path):
            logMAPEvent(readMAPEvents(bin_path))
    
    return

def peek_line(f):
    pos = f.tell()
    line = f.readline()
    f.seek(pos)
    return line

def getParam(line, type = "int"):
    if type == "int":
        return int(line.split("= ")[1].strip())
    elif type == "string":
        return line.split("= ")[1].strip()

def readTextBin(file, event_name):
    text_buffer = ""
    while True:
        next_line = file.readline()
        if next_line.startswith("--------------------------"):
            break
        text_buffer += next_line
    
    if event_name == "SELECT":
        alt = True
    else:
        alt = False
    
    text_buffer = text_buffer.rstrip("\n").replace("{END}","")
    #text = MSG.convertTextToRaw(inject_dict,text_buffer, alt_mode=alt)
    
    return text_buffer

def getNextMSG(file, src_event):
    event_block = []
    msg_block = {}
    while True:
        nextLine = file.readline()
        
        event_ID = int(nextLine.split(" ")[0][2:], 16)
        event_name = getEvent(event_ID)
        event_body_bin = bytes.fromhex(nextLine.split(": ")[-1].strip())
        
        
        if event_name in HAS_VOICE or event_name in HAS_TEXT:
            replace = getParam(file.readline(), "string")
            msg_id_line = file.readline()
            msg_id = getParam(msg_id_line)
        
            if replace == "FALSE":
                msg_block[msg_id*2] = "-SKIP-"
                msg_block[msg_id*2 + 1] = "-SKIP-"
                
        
        
        if event_name in HAS_VOICE:
            voice_id_line = file.readline()
            voice_id = getParam(voice_id_line, "string")
        
        if event_name == "XA":
            #Skip footer
            file.readline()
        
        if event_name in HAS_TEXT:
            msg_header = file.readline()
            msg_bin = readTextBin(file, event_name)
        
        if event_name == "XAMSG" and replace != "FALSE":
            msg_block[msg_id*2] = voice_id
            msg_block[msg_id*2 + 1] = msg_bin
        elif event_name == "XA" and replace != "FALSE":
            msg_block[msg_id*2] = voice_id
            msg_block[msg_id*2 + 1] = ''
            
        elif (event_name == "MSG" or event_name == "SELECT") and replace != "FALSE":
            msg_block[msg_id*2] = ''
            msg_block[msg_id*2 + 1] = msg_bin
            
        event_len = 1 + len(event_body_bin)//2
        
        event_block.append(event_ID.to_bytes(1, "little") + event_len.to_bytes(1, "little") + event_body_bin)
        
        
        if event_name == "END":
            break
        
    return {"EVENT_BLOCK":event_block, "MSG_BLOCK":msg_block}

def mergeMSG(src_convo, MSG_group):
    header_buffer = b''
    buffer = b''
    n_entries = 3 + len(MSG_group["MSG_BLOCK"])
    header_buffer += n_entries.to_bytes(4, "little")
    
    cursor = n_entries*4 + 4
    
    for x in range(2):
        header_buffer += cursor.to_bytes(4, "little")
        buffer += src_convo["INIT_BLOCKS"][x]
        cursor += len(src_convo["INIT_BLOCKS"][x])
        
    event_block_size = 0
    for event in MSG_group["EVENT_BLOCK"]:
        event_block_size += len(event)
        buffer += event
    
    header_buffer += cursor.to_bytes(4, "little")
    cursor += event_block_size
    
    for x in range(len(MSG_group["MSG_BLOCK"])):
        next_msg_txt = b''
        if MSG_group["MSG_BLOCK"][x] == "-SKIP-":
            #Get original MSG entry
            next_msg_txt = src_convo["MSG_BLOCK"][x]
        else:
            #Get new MSG entry
            if x%2 == 0:
                next_msg_txt = MSG_group["MSG_BLOCK"][x].encode("ascii")
            else:
                next_msg_txt = MSG.convertTextToRaw(inject_dict, MSG_group["MSG_BLOCK"][x])
        
        if len(next_msg_txt) == 0:
            header_buffer += 0x00000000.to_bytes(4, "little")
            continue
        header_buffer += cursor.to_bytes(4, "little")  
        buffer += next_msg_txt
        cursor += len(next_msg_txt)
            
        pass
    
    final_buffer = header_buffer + buffer
    
    if len(final_buffer) % 4 == 2:
        final_buffer += b'\xCD\xCD'
    return final_buffer

def mergeMAPBin(src_events, MSG_list):
    
    assert len(src_events) == len(MSG_list)
    
    header_buffer = b''
    buffer = b''
    header_buffer += len(src_events).to_bytes(4, "little")
    
    current_offset = 4 + len(src_events)*0xC
    for convo_entry_number in range(len(src_events)):
        src_convo = src_events[convo_entry_number]
        MSG_group = MSG_list[convo_entry_number]
        header_buffer += src_convo["MAGIC_1"]
        
        n_original_msg_entries = src_convo["N_MSG_ENTRIES"]
        n_new_msg_entries = len(MSG_group["MSG_BLOCK"])//2
        
        msg_bin = mergeMSG(src_convo, MSG_group)
        buffer += msg_bin
        
        header_buffer += len(msg_bin).to_bytes(2, "little")
        header_buffer += src_convo["MAGIC_2"]
        header_buffer += current_offset.to_bytes(4, "little")
        current_offset += len(msg_bin)
        pass
    
    return header_buffer + buffer

def eventScriptToBin(script_path, bin_path):
    script_file = open(script_path, 'r', encoding="UTF8")
    src_events = readMAPEvents(bin_path)
    MSG_bins = []
    while True:
        nextLine = script_file.readline()
        
        if not nextLine:
            #EOF
            break
        
        if nextLine.startswith("--- "):
            entry_number = int(nextLine.split(":")[-1].split(" ")[0])
            MSG_bins.append(getNextMSG(script_file, src_events[entry_number]))
    
    full_bin = mergeMAPBin(src_events, MSG_bins)
    
    open(bin_path, "wb").write(full_bin)
    return

def applyEventScripts():
    SCRIPT_DIR = "VOICE\\MAP_SCRIPTS"
    for filename in os.scandir(SCRIPT_DIR):
        if not filename.is_file():
            continue
        mapname = filename.name.replace(".txt","")
        MAP_EDITS_DIR = "MAP_RIP_EDITS"
        bin_path = os.path.join(MAP_EDITS_DIR, mapname, "1.bin")
        
        eventScriptToBin(filename.path, bin_path)
        
    return

def genSumoTextTXT(path):
    text_file = open(path, "r")
    text_buffer = text_file.read()
    text_file.seek(0)
    while True:
        nextLine = text_file.readline()
        
        if not nextLine:
            break
        
        if not nextLine.startswith("&"):
            continue
        
        number = nextLine[1:].strip()
        text_buffer = text_buffer.replace(number + "\n", number + "\n" + "Voice ID: " + number + " ")

    return text_buffer

LEFT = 0
CENTER = 1
RIGHT = 2

LINE_LENGTH = 25

def genSpaceSumoTXT(path, ALIGNMENT=LEFT):
    if ALIGNMENT == LEFT:
        return
    
    text_file = open(path, "r")
    text_buffer = ""
    text_file.seek(0)
    while True:
        nextLine = text_file.readline()
        nextLine = nextLine.lstrip(" ")
        if not nextLine:
            break
        
        if nextLine.startswith("&"):
            text_buffer += nextLine
            continue
        
        if nextLine == "\n":
            text_buffer += nextLine
            continue
        
        length = len(nextLine[:nextLine.find("{")])
        
        if ALIGNMENT == CENTER:
            spaces_to_add = (25 - length)//2
        elif ALIGNMENT == RIGHT:
            spaces_to_add = 25 - length
        
        spaced_line = " "*spaces_to_add + nextLine
        text_buffer += spaced_line

    return text_buffer

def genSumoVoiceBin():
    TEXT_PATH = "VOICE\\sumo_script.txt"
    BIN_PATH = "VOICE\\sumo_msg.bin"
    msg_mode = MSG.MSG_MODE
    
    text_file = open(TEXT_PATH, "r", encoding="utf8")

    voice_idx = 0
    msgs = {0:[],1:[],2:[],3:[],4:[],5:[]}
    
    MAX_ENTRIES = 17
    current_group = 0
    dict= MSG.readFont("font-inject-menus.txt",0, MSG.INSERTION)
    while True:
        headerLine = text_file.readline()
        if not headerLine:
            #EOF
            break
        if not headerLine.startswith("&"):
            #Filler line
            continue
        
        voice_id_nub = headerLine[1:].rstrip("\n")
        
        group_number = int(headerLine[1:2])
        entry_number = int(headerLine[2:4])
        
        string_buffer = ""

        while True:
            cursor = text_file.tell()
            next_line = text_file.readline()
            if not next_line:
                #EOF
                break
            if not next_line.startswith("&"):
                #Text line
                string_buffer += next_line
                continue
            else:
                #Next entry reached
                text_file.seek(cursor)
                break
        
        string_buffer = string_buffer.rstrip("\n")
        
        line = MSG.convertTextToRaw(dict, string_buffer, alt_mode=True)
        msgs[group_number].append(line)
        current_group = group_number
        #print("Adding sumo line ", voice_idx)
        
        
        
        voice_idx += 1
    msg = []
    for x in range(6):
        n_blanks = MAX_ENTRIES - len(msgs[x])
        for y in range(n_blanks):
            msgs[x].append(b'')
        msg += msgs[x]
    msg_bin = MSG.repackMsg(msg, msg_mode)
    out_file = open(BIN_PATH, "wb")
    out_file.write(msg_bin)
    out_file.close()
    text_file.close()
    return


#text = genSpaceSumoTXT("VOICE\\sumo_script.txt", RIGHT)
#text_path = open("VOICE\\sumo_script_test.txt", "w")
#text_path.write(text)
#genSumoVoiceBin()    
#applyEventScripts()
#eventScriptToBin("MISC\\voice_logs\\M_A11103.txt", "MAP_RIP\\M_A11103\\1.bin")
#logAllMapEvents()
#logMAPEvent(readMAPEvents("MAP_RIP\\M_A11200\\1.bin"))
#readMAPEvents("MAP_RIP\\M_A37118\\1.bin")
#createIDWavs()