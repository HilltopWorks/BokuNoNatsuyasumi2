import os
import shutil
import subprocess
from pathlib import Path
import resource
import polib
import MSG
import UNPACK
import TIM2


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

def injectMAPs():
    for root, subdirectories, files in os.walk(os.path.join(ORIGINAL_RIP_PATH, MAP_DIR)):
        for file in files:
            po_name = file.replace(".bin",".po")
            po_path = os.path.join(MAP_PO_PATH,po_name)

            map_stem = file.replace(".bin", "")
            bin_path = os.path.join(MAP_EDITS_DIR, map_stem, "1.bin")

            if not os.path.exists(po_path):
                print("Skipping MAP ",file)
                continue
            MSG.injectPO(bin_path,po_path, MSG.MAP_MODE, inject_dict)
    return

def injectIMGs():
    for img_msg in MSG.IMG_MSG_FILES:
        po_path = os.path.join(IMG_PO_PATH, img_msg + ".po")
        bin_path = os.path.join(IMG_EDITS_DIR, img_msg)
        MSG.injectPO(bin_path,po_path, MSG.MSG_MODE, inject_dict)
    
    for img_msg in MSG.RAW_MSG_FILES:
        po_path = os.path.join(RAW_PO_PATH, img_msg + ".po")
        bin_path = os.path.join(IMG_EDITS_DIR, img_msg)
        MSG.injectPO(bin_path,po_path, MSG.RAW_MODE, inject_dict)
    
    for img_msg in MSG.OFFSET_ONLY_MSG_FILES:
        po_path = os.path.join(OFFSET_ONLY_PO_PATH, img_msg + ".po")
        bin_path = os.path.join(IMG_EDITS_DIR, img_msg)
        MSG.injectPO(bin_path,po_path, MSG.OFFSET_ONLY_MODE, inject_dict)
    return

def build_ISO(input, output):
    #build_disc = 'cmd /c  ultraiso.exe -imax -l -d "' + input + '" -out "' + output + '"'
    build_disc = 'cmd /c  ultraiso.exe -in "' + output + '" -d "' + input + '"'
    os.system(build_disc)

    return


def build(mode):
    if mode > 0:
        #Pull text from weblate
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

        #Pack text
        print("____BUILD: Injecting MAPs")
        injectMAPs()
        print("____BUILD: Injecting IMGs")
        injectIMGs()

        #TODO pack graphics

        #Generate bin files
        print("____BUILD: Packing MAP files")
        UNPACK.packMaps("MAP_RIP_EDITS","ISO_EDITS\\map")
        print("____BUILD: Packing IMG")
        UNPACK.packIMG("IMG_RIP_EDITS", "ISO_EDITS")
        #UNPACK.updateCRCs(IMG_EDITS_DIR)

    #TODO apply all ASM patches
    print("____BUILD: Applying ASM patches")
    subprocess.call(['armips.exe', 'scps_150.26.asm'])

    #Build game disc
    print("____BUILD: Rebuilding ISO")
    build_ISO(ISO_EDITS_DIR, ISO_OUTPUT_PATH)
    return

FULL = 1
ASM_ONLY = 0

mode = ASM_ONLY

#injectIMGs()
build(mode)