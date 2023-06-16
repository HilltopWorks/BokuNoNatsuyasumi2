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
    file.seek(offset)
    
    endpoint = MSG.findEndpoint(file, offset, n_entries, 2, size)
    
    
    file.seek(offset + 0xC)
    
    event_start = resource.readInt(file)
    event_end = event_start + size
    
    file.seek(offset + event_start)
    
    
    event_list = {"FILE":file_path, "OFFSET":offset, "EVENTS":[]}
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
        file.seek(4 + 0xC*x + 0x4)
        table_size = resource.readShort(file)
        file.seek(4 + 0xC*x + 0x8)
        table_offset = resource.readShort(file)
        event_list = readEventList(file_path, table_offset, table_size)
        event_list["TABLE_SIZE"] = table_size
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
        sub_map = [x for x in sub_map if x != '']
        #po = MSG.convertToPO(list["FILE"], MSG.MAP_MODE)
        voice_lines = [x.decode("ascii") for x in sub_map if isVoiceID(x)]
        text_lines = [x for x in sub_map if not isVoiceID(x)]
        MSG_COUNT = 0
        XAMSG_COUNT = 0
        XA_COUNT = 0
        for event in list["EVENTS"]:
            logFile.write(event["STRING"] + "\n")
            #print(event["STRING"])
            
            if EVENT_LABELS[event["ID"]] == "MSG":
                line_number = int(event["BODY"][8:10], 16)
                logFile.write( "MSG ID   = " +  str(line_number) +   "\n")
                line_text = MSG.testRaw(text_lines[MSG_COUNT + XAMSG_COUNT].hex().replace("cdcd", ""))
                logFile.write( "-MSG:" + "\n")
                line_text = line_text.rstrip("\n").replace("\\n", "\n")
                logFile.write(line_text + "\n--------------------------\n")
                MSG_COUNT += 1
            elif EVENT_LABELS[event["ID"]] == "XAMSG":
                line_number = int(event["BODY"][8:10], 16)
                
                logFile.write( "-MSG ID   = " +  str(line_number) +   "\n")
                line_text = MSG.testRaw(text_lines[MSG_COUNT + XAMSG_COUNT].hex().replace("cdcd", ""))
                voice_ID = voice_lines[XAMSG_COUNT + XA_COUNT]
                logFile.write( "-VOICE ID = " +voice_ID + "\n")
                logFile.write( "-XAMSG:" + "\n")
                line_text = line_text.rstrip("\n").replace("\\n", "\n")
                logFile.write(line_text + "\n--------------------------\n")
                
                XAMSG_COUNT += 1
            elif EVENT_LABELS[event["ID"]] == "XA":
                voice_ID = voice_lines[XAMSG_COUNT + XA_COUNT]
                logFile.write( "-VOICE ID = " +voice_ID + "\n--------------------------\n")
                XA_COUNT += 1
            elif EVENT_LABELS[event["ID"]] == "SELECT":
                line_number = int(event["BODY"][4:6], 16)
                logFile.write( "MSG ID   = " +  str(line_number) +   "\n")
                line_text = MSG.testRaw(text_lines[MSG_COUNT + XAMSG_COUNT].hex().replace("cdcd", ""))
                logFile.write( "-SELECT:" + "\n")
                line_text = line_text.rstrip("\n").replace("\\n", "\n")
                logFile.write(line_text + "\n--------------------------\n")
                MSG_COUNT += 1
        list_counter += 1
                
    return

def logAllMapEvents():
    dirs = os.walk("MAP_RIP")
    
    for dir in dirs.__next__()[1]:
        bin_path = os.path.join("MAP_RIP", dir, "1.bin")
        if os.path.exists(bin_path):
            logMAPEvent(readMAPEvents(bin_path))
        pass
    
    
    return

def eventScriptToBin(script_path):
    script_file = open(script_path, 'r', encoding="UTF8")
    
    
    return

logAllMapEvents()
#logMAPEvent(readMAPEvents("MAP_RIP\\M_A11200\\1.bin"))
#readMAPEvents("MAP_RIP\\M_A37118\\1.bin")
#createIDWavs()