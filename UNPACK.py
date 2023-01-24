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
ORIGINAL_RIP_PATH = 'ISO_RIP'
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
INDEX_PATH = os.path.join(ORIGINAL_RIP_PATH, "boku2.idx")
IMG_PATH   = os.path.join(ORIGINAL_RIP_PATH, "boku2.img")
IMG_RIP_DIR = 'IMG_RIP'
IMG_EDITS_DIR = "IMG_RIP_EDITS"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = open(os.path.join(LOG_DIR, date_time + ".log"), 'w')

def log(msg):
    print(msg)
    log_file.write(msg + '\n')
    return

def unpackMaps():
    '''Separates every individual file in the map dir'''
    for root, subdirectories, files in os.walk(os.path.join(ORIGINAL_RIP_PATH, MAP_DIR)):
        for file in files:
            log("Unpacking map " + file)
            stem = Path(file).stem
            map_path = os.path.join(ORIGINAL_RIP_PATH, MAP_DIR, file)

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
    
    for root, subdirectories, files in os.walk(os.path.join(ORIGINAL_RIP_PATH, MAP_DIR)):
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
            dir_stack.append(IDX_entry['filename']) # Stack entries are [dirname, files remaining]
            if IDX_entry['dir_info'] == 0: #Immediately remove empty directories after creating empty dir
                #os.makedirs(createDirPath(dir_stack, IMG_RIP_DIR), exist_ok=True)
                is_escape_dir = True
                #dir_stack.pop()
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

#unpackIMG()
packIMG("IMG_RIP_EDITS","BUILD")
#packMaps("MAP_RIP","MAP_BUILD")
#unpackIMG()
#unpackMaps()