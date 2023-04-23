import os
import shutil
import subprocess
from pathlib import Path
import resource
import polib
import MSG
import UNPACK
import TIM2
import reprint


MAP_PO_PATH = "boku-no-natsuyasumi-2\\m_a01000\\MAP\\en"
IMG_PO_PATH = "boku-no-natsuyasumi-2\\fishing-msg\\IMG\\en"
RAW_PO_PATH = "boku-no-natsuyasumi-2\\diary\\en"
OFFSET_ONLY_PO_PATH = "boku-no-natsuyasumi-2\\diary\\en"

ORIGINAL_RIP_PATH = 'ISO_RIP'
MAP_DIR = 'map'

MAP_EDITS_DIR = "MAP_RIP_EDITS"
IMG_EDITS_DIR = "IMG_RIP_EDITS"

ISO_EDITS_DIR = "ISO_EDITS"
ISO_OUTPUT_PATH = "BUILD/boku2_patched.iso"

inject_dict = MSG.readFont("font-inject.txt", 0, MSG.INSERTION)

def injectMAPs(compaction_map):
    for root, subdirectories, files in os.walk(os.path.join(ORIGINAL_RIP_PATH, MAP_DIR)):
        for file in files:
            po_name = file.replace(".bin",".po")
            po_path = os.path.join(MAP_PO_PATH,po_name)

            map_stem = file.replace(".bin", "")
            bin_path = os.path.join(MAP_EDITS_DIR, map_stem, "1.bin")

            if not os.path.exists(po_path):
                print("Skipping MAP ",file)
                continue
            print("Injecting MAP script:", file)
            MSG.injectPO(bin_path,po_path, MSG.MAP_MODE, inject_dict, compaction_map)
    return

def injectIMGs(compaction_map):
    for img_msg in MSG.IMG_MSG_FILES:
        po_path = os.path.join(IMG_PO_PATH, img_msg + ".po")
        bin_path = os.path.join(IMG_EDITS_DIR, img_msg)
        print("Injecting IMG script:", img_msg)
        MSG.injectPO(bin_path,po_path, MSG.MSG_MODE, inject_dict, compaction_map)

    
    for img_msg in MSG.RAW_MSG_FILES:
        po_path = os.path.join(RAW_PO_PATH, img_msg + ".po")
        bin_path = os.path.join(IMG_EDITS_DIR, img_msg)
        print("Injecting RAW IMG script:", img_msg)
        MSG.injectPO(bin_path,po_path, MSG.RAW_MODE, inject_dict, compaction_map)
    
    for img_msg in MSG.OFFSET_ONLY_MSG_FILES:
        po_path = os.path.join(OFFSET_ONLY_PO_PATH, img_msg + ".po")
        bin_path = os.path.join(IMG_EDITS_DIR, img_msg)
        print("Injecting OFFSET ONLY IMG script:", img_msg)
        MSG.injectPO(bin_path,po_path, MSG.OFFSET_ONLY_MODE, inject_dict, compaction_map)
    return

def build_ISO(input, output):
    #build_disc = 'cmd /c  ultraiso.exe -imax -l -d "' + input + '" -out "' + output + '"'
    build_disc = 'cmd /c  ultraiso.exe -in "' + output + '" -d "' + input + '"'
    os.system(build_disc)

    return

def pullScript():
    print("____BUILD: Pulling text files")
    os.chdir("boku-no-natsuyasumi-2\\fishing-msg")
    os.system("git fetch")
    os.system("git reset --hard HEAD")
    os.system("git merge origin/main")
    os.chdir("..\\m_a01000")
    os.system("git fetch")
    os.system("git reset --hard HEAD")
    os.system("git merge origin/main")
    os.chdir("..\\..")
    return

def copy_POs():

    destinations = ["boku-no-natsuyasumi-2\\fishing-msg\\IMG\\en\\system\\submenu\\fish\\fish_info.msg.po",
                    "boku-no-natsuyasumi-2\\fishing-msg\\IMG\\en\\system\\submenu\\item\\item_info.msg.po"
                    ]

    sources =       ["boku-no-natsuyasumi-2\\fish_info-msg\\en.po",
                     "boku-no-natsuyasumi-2\\item_info-msg\\en.po"
                    ]
    
    for x in range(len(destinations)):
        if os.path.exists(sources[x]):
            print("Copying:",sources[x], destinations[x])
            shutil.copyfile(sources[x], destinations[x])

    return

ADDITIONS = {               #Addition file,                             parent file,        offset
            "diary":        ["ADDS\\diary-1.bin",               "IMG_RIP_EDITS\\diary.bin", 0x80 ],
            "saveload-0":   ["ADDS\\saveload-0.bin", "IMG_RIP_EDITS\\system\\saveload.bin", 0x100],
            "saveload-1":   ["ADDS\\saveload-1.bin", "IMG_RIP_EDITS\\system\\saveload.bin", 0x180]
            }

def insertAdditions(addition):
    parent = open(addition[1], 'r+b')
    parent.seek(addition[2])
    parent.write(open(addition[0], 'rb').read())

    return

def fixFishOnMem():
    payload_data = open(os.path.join(IMG_EDITS_DIR, "fish\\fishing.msg"), 'rb').read()
    
    while len(payload_data)%0x10 != 0:
        payload_data += b"\x00"
    
    target_file = open(os.path.join(IMG_EDITS_DIR, "fish\\img\\fish_on_mem.bin"), 'r+b')
    target_file.seek(0x438d0)
    target_file.write(payload_data)
    target_file.seek(0x90)
    target_file.write(len(payload_data).to_bytes(4, "little"))
    return

def insertAllAdditions():
    for addition in ADDITIONS:
        insertAdditions(ADDITIONS[addition])

    print("Applying fish_on_mem.bin manual patch...")
    fixFishOnMem()
    return

def build(mode):
    if mode > 0:
        #Pull text from weblate
        ###pullScript()
        copy_POs()

        #Print automated graphics
        print("____BUILD: Printing graphics")
        reprint.printAllCalendars()
        reprint.printAllBottleCaps()
        compaction_map = reprint.printAllFonts()

        #Pack graphics
        print("____BUILD: Injecting graphics")
        TIM2.injectAll()

        #Pack text
        print("____BUILD: Injecting MAP scripts")
        injectMAPs(compaction_map)
        print("____BUILD: Injecting IMG scripts")
        injectIMGs(compaction_map)

        #Insert addition files
        print("____BUILD: Applying addition patches")
        insertAllAdditions()

        #Generate bin files
        print("____BUILD: Packing MAP files")
        UNPACK.packMaps("MAP_RIP_EDITS","ISO_EDITS\\map")
        print("____BUILD: Packing IMG")
        UNPACK.packIMG("IMG_RIP_EDITS", "ISO_EDITS")
    

    #Apply ASM
    print("____BUILD: Applying ASM patches")
    os.remove("ISO_EDITS\\scps_150.26")
    shutil.copy("ISO_RIP\\scps_150.26", "ISO_EDITS\\scps_150.26")
    os.chmod("ISO_EDITS\\scps_150.26", 777)
    os.system('attrib -r '+"ISO_EDITS\\scps_150.26")
    subprocess.call(['armips.exe', 'scps_150.26.asm'])

    #Build game disc
    print("____BUILD: Rebuilding ISO")
    build_ISO(ISO_EDITS_DIR, ISO_OUTPUT_PATH)
    print("Ding!")
    return

FULL = 1
ASM_ONLY = 0

mode = ASM_ONLY
build(mode)

