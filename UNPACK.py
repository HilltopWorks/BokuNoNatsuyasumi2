'''

Boku no Natsuyasumi 2 file unpacker

'''

import shutil
import subprocess
import os
import resource

from pathlib import Path
from datetime import datetime


LOG_DIR = 'log'
ISO_RIP_DIR = 'ISO_RIP'
ISO_EDIT_DIR = 'ISO_EDITS'
now = datetime.now()
date_time = now.strftime("%m-%d-%Y_%H-%M-%S")

#MAP Files
MAP_DIR = 'map'
MAP_RIP_DIR = "MAP_RIP"
DIR_START = 0x10
DIR_END = 0x8140
NUM_IDX_ENTRIES = (DIR_END - DIR_START)//0x10 
IDX_ENTRY_SIZE = 0x10

FILENAMES_START = 0x8140

#IMG File
INDEX_PATH = os.path.join(ISO_RIP_DIR, "boku2.idx")
IMG_PATH   = os.path.join(ISO_RIP_DIR, "boku2.img")
IMG_RIP_DIR = 'IMG_RIP'
IMG_EDITS_DIR = "IMG_RIP_EDITS"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = open(os.path.join(LOG_DIR, date_time + ".log"), 'w')

def log(msg):
    #print(msg)
    log_file.write(msg + '\n')
    return

def unpackMaps():
    '''Separates every individual file in the map dir'''
    for root, subdirectories, files in os.walk(os.path.join(ISO_RIP_DIR, MAP_DIR)):
        for file in files:
            log("Unpacking map " + file)
            stem = Path(file).stem
            map_path = os.path.join(ISO_RIP_DIR, MAP_DIR, file)

            map_file = open(map_path, 'rb')

            header_ID = resource.readInt(map_file) #Usually (always?) 0xE
            log("\tHeader ID: " + hex(header_ID))
            header_length = resource.readInt(map_file) #First offset entry. Usually (always?) 0x80
            log("\tHeader length: " + hex(header_length))
            map_file.seek(4) #Return to dir start

            cursor = 4

            while cursor + 4 < header_length:

                map_file.seek(cursor)
                log("\t\tUnpacking file from map #" + str((cursor - 4)//8))
                file_offset = resource.readInt(map_file)
                file_size = resource.readInt(map_file)

                log("\t\tOffset/Size: " + hex(file_offset) + "/" + hex(file_size))
                

                if file_offset == 0:
                    log("\t\t\tEntry skipped (null)")
                    cursor += 8
                    continue #Null directory entry
                
                map_file.seek(file_offset)

                if not os.path.exists(os.path.join(MAP_RIP_DIR, stem)):
                    os.makedirs(os.path.join(MAP_RIP_DIR, stem), exist_ok=True)

                fileNumber = (cursor - 4)//8
                output_file_name = str(fileNumber) + '.bin'
                output_file = open(os.path.join(MAP_RIP_DIR,stem, output_file_name ), 'wb')

                output_file.write(map_file.read(file_size))

                output_file.close()

                log("\t\t\tFile unpacked")

                cursor += 8
            
            map_file.close()


    return

def packMaps(maps_dir, outdir):
    map_list = []
    
    for root, subdirectories, files in os.walk(os.path.join(ISO_RIP_DIR, MAP_DIR)):
        for file in files:
            
            map_name = file.split(".")[0]
            map_dir = os.path.join(maps_dir, map_name)
            original_file_path = os.path.join(root, file)
            original_file = open(original_file_path, "rb")
            n_entries = resource.readInt(original_file)
            table_size = resource.readInt(original_file)

            header_buffer = n_entries.to_bytes(4, "little") #+ table_size.to_bytes(4, "little")
            data_buffer = b''

            file_cursor = table_size
            for x in range(n_entries):
                component_path = os.path.join(map_dir,  str(x) + ".bin")
                if not os.path.exists(component_path):
                    #Null entry
                    header_buffer += b'\x00\x00\x00\x00' + b'\x00\x00\x00\x00'
                    continue

                component_file = open(component_path, 'rb')
                component_data = component_file.read()

                component_size = len(component_data)

                while len(component_data) % 0x10 != 0:
                    component_data += b'\x00'

                header_buffer += file_cursor.to_bytes(4, "little")
                header_buffer += component_size.to_bytes(4,"little")

                data_buffer += component_data
                file_cursor += component_size + (0x10 - (component_size % 0x10) ) % 0x10
            
            #Pad header to original size
            while len(header_buffer) < table_size:
                header_buffer += b'\x00'

            os.makedirs(outdir, exist_ok=True)
            out_path = os.path.join(outdir, file)
            out_file = open(out_path, 'wb')
            out_file.write(header_buffer + data_buffer)
            out_file.close()
            
            


    for map in map_list:
        map_dir = os.path.join(maps_dir, map)
        buffer = b''

    return

def getFileNames():
    index_file = open(INDEX_PATH, 'rb')
    index_file.seek(FILENAMES_START)

    filenames = []

    while True:
        next_filename = resource.ReadString(index_file)
        if not next_filename:
            break

        filenames += [next_filename]
    
    return filenames

def getIDX():
    index_file = open(INDEX_PATH, 'rb')
    log("Unpacking IDX")

    filenames = getFileNames()

    IDX_ENTRIES = []

    for x in range(NUM_IDX_ENTRIES):
        index_file.seek(DIR_START + x*IDX_ENTRY_SIZE)
        is_dir = resource.readShort(index_file)
        dir_info = resource.readShort(index_file)
        filename_offset = resource.readInt(index_file)
        sector_offset =  resource.readInt(index_file)
        filesize = resource.readInt(index_file)
        
        
        IDX_ENTRY = {
                    'filename': filenames[x],
                    'offset': sector_offset*0x800,
                    'size': filesize,
                    'is_dir':is_dir,
                    'dir_info':dir_info
                     }
        IDX_ENTRIES += [IDX_ENTRY]
        log(str(IDX_ENTRY))
    
    return IDX_ENTRIES

#Create directory path with stack and root dir
def createDirPath(stack, dir):
    dir_path = dir
    
    for entry in stack:
        if entry == "/":
            continue
        dir_path = os.path.join(dir_path, entry)

    return dir_path

def unpackIMG():
    img_file = open(IMG_PATH, 'rb')

    IDX = getIDX()

    dir_stack = []

    is_escape_dir = False
    for x in range(len(IDX)):
        IDX_entry = IDX[x]
        if IDX_entry['is_dir'] != 0:
            dir_stack.append(IDX_entry['filename']) # Stack entries are [dirname, files remaining]
            if IDX_entry['dir_info'] == 0: #Immediately remove empty directories after creating empty dir
                os.makedirs(createDirPath(dir_stack, IMG_RIP_DIR), exist_ok=True)
                is_escape_dir = True
                #dir_stack.pop()
            continue

        file_path = os.path.join(createDirPath(dir_stack, IMG_RIP_DIR), IDX_entry['filename'])
        os.makedirs(createDirPath(dir_stack, IMG_RIP_DIR), exist_ok=True)

        output_file = open(file_path, 'wb')

        img_file.seek(IDX_entry['offset'])
        output_file.write(img_file.read(IDX_entry['size']))
        output_file.close()

        if IDX_entry['dir_info'] == 0:
            try:
                dir_stack.pop()
                if is_escape_dir == True:
                    dir_stack.pop()
                    is_escape_dir = False
            except IndexError:
                if x == len(IDX) - 1:
                    log("IDX unpack completed successfully")
                    break
                else:
                    assert False, "IDX INDEX ERROR"

    return

def packIMG(input_dir, output_dir):
    IDX = getIDX()

    dir_stack = []
    data_cursor = 0
    img_buffer = b''
    
    shutil.copyfile(INDEX_PATH, os.path.join(output_dir, "boku2.idx"))
    idx_file = open(os.path.join(output_dir, "boku2.idx"), 'r+b')
    #shutil.copyfile(IMG_PATH, os.path.join(output_dir, "boku2.img"))

    is_escape_dir = False
    for x in range(len(IDX)):
        IDX_entry = IDX[x]
        if IDX_entry['is_dir'] != 0:
            idx_file.seek(x*0x10 + 0x18)
            idx_file.write(data_cursor.to_bytes(4, "little"))
            dir_stack.append(IDX_entry['filename']) # Stack entries are [dirname, files remaining]
            if IDX_entry['dir_info'] == 0: #Immediately remove empty directories after creating empty dir
                is_escape_dir = True
            continue
        
        
        file_path = os.path.join(createDirPath(dir_stack, input_dir), IDX_entry['filename'])
        
        file_data = open(file_path, 'rb').read()

        idx_file.seek(x*0x10 + 0x18)
        idx_file.write(data_cursor.to_bytes(4, "little"))
        idx_file.write(len(file_data).to_bytes(4, "little"))
        if len(file_data) % 0x800 != 0:
            file_data += bytes((0x800 - (len(file_data)%0x800))%0x800)

        img_buffer += file_data
        
        
        data_cursor += len(file_data)//0x800
        
        if IDX_entry['dir_info'] == 0:
            print("Packing",file_path)
            try:
                dir_stack.pop()
                if is_escape_dir == True:
                    dir_stack.pop()
                    is_escape_dir = False
            except IndexError:
                if x == len(IDX) - 1:
                    log("IDX pack completed successfully")
                    break
                else:
                    assert False, "IDX INDEX ERROR"
    
    img_file = open(os.path.join(output_dir, "boku2.img"), 'wb')
    img_file.write(img_buffer)
    img_file.close()
    idx_file.close()

    return

def unzipPOs():
    os.system('cmd /c "tar -xf boku-no-natsuyasumi-2.zip"')
    return

def crc16(data : bytearray, offset , length):
    if data is None or offset < 0 or offset > len(data)- 1 and offset+length > len(data):
        return 0
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for j in range(0,8):
            if (crc & 0x8000) > 0:
                crc =(crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF

def crcFile(path):
    f = open(path, 'rb')
    data = f.read(0x80)
    
    if len(data) < 0x80:
        length = len(data)
    else:
        length = 0x80
    crc = crc16(data, 0, length)
    #print(hex(crc))
    return crc


def getCRCdict(path):
    crc_path = "ISO_RIP/boku2.crc"
    crc_file = open(crc_path, "rb")
    
    n_entries = resource.readInt(crc_file)
    dir_start = resource.readInt(crc_file)
    dir_size = resource.readInt(crc_file)
    crc_data_offset = resource.readInt(crc_file)
    crc_data_size = resource.readInt(crc_file)

    crcs = []
    file_names = []
    file_paths = []
    entry_numbers = []

    crc_matches = {}
    for x in range(n_entries):
        crc_file.seek(x * 0x20 + dir_start)
        resource.readShort(crc_file)
        entry_number = resource.readShort(crc_file)
        type = resource.readShort(crc_file)
        entry_number_2 = resource.readShort(crc_file)
        file_name = resource.ReadString(crc_file)
        
        file_names.append(file_name)
        entry_numbers.append(entry_number)

    for y in range(crc_data_size//2):
        crc_file.seek(crc_data_offset + y*2)
        file_crc = resource.readShort(crc_file)
        crcs.append(file_crc)


    for root, subdirectories, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root,file)
            base_path = os.path.join(root,file).split("\\",1)[1]
            file_name = os.path.basename(file)
            if file_names.count(file_name) > 1:
                matches = [i for i, z in enumerate(file_names) if z == file_name]

                match_found = False
                for index in matches:
                    base_crc = crcs[entry_numbers[index]]
                    calc_crc = crcFile(file_path)
                    if base_crc == calc_crc:
                        match_found = True
                        if not base_path in crc_matches:
                            crc_matches[base_path] = [index]
                        else:
                            crc_matches[base_path] = crc_matches[base_path] + [index]
                        print(file)
                        print("crc number " + hex(index) + " -> " + file_path)
                if not match_found:
                    print("CRC FAILURE: " +  file)
                    print("BASE: " + hex(base_crc), "CALC: " + hex(calc_crc))
            else:
                if not file_name in file_names:
                    print("MISSING FILE " + file)
                index = file_names.index(file_name)
                base_crc = crcs[entry_numbers[index]]
                calc_crc = crcFile(file_path)
                crc_matches[base_path] = [index]
                if base_crc != calc_crc:
                    print("CRC FAILURE: " +  file)
                    print("BASE: " + hex(base_crc), "CALC: " + hex(calc_crc))
    return crc_matches
            

def setCRC(crc_file, indices, crc):
    crc_file.seek(0)
    n_entries = resource.readInt(crc_file)
    dir_start = resource.readInt(crc_file)
    dir_size = resource.readInt(crc_file)
    crc_data_offset = resource.readInt(crc_file)
    crc_data_size = resource.readInt(crc_file)
    for index in indices:
        crc_file.seek(crc_data_offset + index*2)
        crc_file.write(crc.to_bytes(2, "little"))
    return

def updateCRCs(path):
    crc_dict = getCRCdict(IMG_RIP_DIR)
    map_crc_dict = getCRCdict("ISO_RIP\\map")
    
    crc_dict.update(map_crc_dict)

    crc_file = open(os.path.join(ISO_EDIT_DIR, "boku2.crc"), 'r+b')

    for root, subdirectories, files in os.walk(path):
        for file in files:
            file_path_base =  os.path.join(root,file).split("\\",1)[1]
            file_path = os.path.join(root,file)
            new_crc = crcFile(file_path)
            indices = crc_dict[file_path_base]

            setCRC(crc_file, indices, new_crc)
    crc_file.close()
    return

updateCRCs(IMG_EDITS_DIR)
#updateCRCs(MAP_DIR)

#getCRC("ISO_RIP\\map")
#c = getCRCdict(IMG_RIP_DIR)
#print(str(c["system\submenu\img_bak\msg.tm2"]))

#updateCRCs()
#crcFile("IMG_RIP\system\submenu\img\phot_20.tm2.arn")
#testCRC()
#packIMG("IMG_RIP_EDITS", "BUILD")
#unpackIMG()
#packIMG("IMG_RIP_EDITS","BUILD")
#packMaps("MAP_RIP","MAP_BUILD")
#unpackIMG()
#unpackMaps()