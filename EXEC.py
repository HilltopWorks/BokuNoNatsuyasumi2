import os
import shutil
from pathlib import Path
import resource
import polib
import MSG
import UNPACK
import TIM2


MAP_PO_PATH = "boku-no-natsuyasumi-2\\m_a01000\\MAP\\en"
IMG_PO_PATH = "boku-no-natsuyasumi-2\\fishing-msg\\IMG\\en"

ORIGINAL_RIP_PATH = 'ISO_RIP'
MAP_DIR = 'map'

MAP_EDITS_DIR = "MAP_RIP_EDITS"
IMG_EDITS_DIR = "IMG_RIP_EDITS"

inject_dict = MSG.readFont("font.txt", MSG.INSERTION)

def injectMAPs():
    for root, subdirectories, files in os.walk(os.path.join(ORIGINAL_RIP_PATH, MAP_DIR)):
        for file in files:
            po_name = file.replace(".bin",".po")
            po_path = os.path.join(MAP_PO_PATH,po_name)

            map_stem = file.replace(".bin", "")
            bin_path = os.path.join(MAP_EDITS_DIR, map_stem, "1.bin")

            MSG.injectPO(bin_path,po_path, MSG.MAP_MODE, inject_dict)
    return

def injectIMGs():
    for img_msg in MSG.IMG_MSG_FILES:
        po_path = os.path.join(IMG_PO_PATH, img_msg + ".po")
        bin_path = os.path.join(IMG_EDITS_DIR, img_msg)
        MSG.injectPO(bin_path,po_path, MSG.MSG_MODE, inject_dict)
    return

def build():
    #Pack text
    UNPACK.unzipPOs()
    injectMAPs()
    injectIMGs()

    #TODO pack graphics

    #Generate bin files
    UNPACK.packMaps("MAP_RIP_EDITS","BUILD")
    UNPACK.packIMG("IMG_RIP_EDITS", "BUILD")
    
    #TODO apply ASM patches

    #TODO build game disc?
    return