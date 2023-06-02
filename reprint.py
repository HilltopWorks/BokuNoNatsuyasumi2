from PIL import Image,ImageDraw,ImageFont
import PIL
import os
import numpy
import copy
import shutil
from pathlib import Path
import math
import re
import cv2
from MSG import readFont, INSERTION, fixPO
import polib
from scipy import ndimage
import textCompaction

#Calendar
day_strings = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
day_colors = [(144,53,40,255), (53,53,53,255), (151,77,46,255), (33,41,122,255), (85,57,47,255) ,(40,74,61,255), (41,105,140,255)]
calendar_folder = "IMG_GFX_EDITS\\system\\submenu\\img"

#Bottle Caps
cap_folder = "IMG_GFX_EDITS\\system\\submenu\\img"
label_path = "GFX\\bottle_caps.txt"


#Bug Info
bug_folder = "IMG_GFX_EDITS\\system\\submenu\\img"
bug_label_path = "GFX\\bug_info.txt"

#Diary
diary_folder = "IMG_GFX_EDITS\\00diary\\nik"
diary_text_path = "GFX\\diaries.txt"
diary_base_folder = "GFX\\diary"
diary_base_path = "FONT/diary_base.png"

#Font
SPACING = 2
SPACE_WIDTH = 6

START_ROW = 15
END_ROW = 45
N_COLUMNS = 23
CELL_WIDTH = 22

KERNING_PATH = "font_kerning.bin"
FONT_IMAGE_PATH = "IMG_GFX_EDITS\\system\\bk_font.tms_0x80_0.png"

FONTS = {
        "base": {
                "typeface":"FONT\\IwataMaruGothicW55-D.ttf",
                "font_size":19,
                "font_map":"font-inject-print.txt",
                "row_offset":0,
                "kern":True,
                "monospace":-1,
                "baseline_adjust":0,
                "emphasis":1.0
                },
        "menu": {
                "typeface":"FONT\\Gen Jyuu Gothic Monospace Bold.ttf",
                "font_size":18,
                "font_map":"font-inject-menus-print.txt",
                "row_offset":5,
                "kern":False,
                "monospace":10,
                "baseline_adjust":0,
                "emphasis":1.0
                },
        "simon":{
                "typeface":"FONT\\OldStandardTT-Regular.ttf",
                "font_size":22,
                "font_map":"font-inject-simon-print.txt",
                "row_offset":10,
                "kern":True,
                "monospace":-1,
                "baseline_adjust":0,
                "emphasis":1.6

                }

        }

def printBottleCap(img_path, string):
    sourceImage = Image.open(img_path)#.convert("RGBA")

    #Clear away existing text
    clear_size = (256,22)
    clear_pos = (0,0)

    rect = Image.new("RGBA", clear_size, (0, 0, 0, 0))
    sourceImage.paste(rect)

    draw = ImageDraw.Draw(sourceImage)

    font = "FONT\\A-OTF-ShinGoPro-Regular.otf"
    fontSize = 18

    fontColor = (180, 180, 180, 255)
    shadowColor = (64,64,64,255)

    imFont = ImageFont.truetype(font, fontSize)
    

    draw.text( (7,4),string, shadowColor, imFont, "lt", 0, 'left')
    draw.text( (6,3),string, fontColor, imFont, "lt", 0, 'left')
    #sourceImage.show()
    sourceImage.save(img_path)

    return

def printAllBottleCaps():

    label_file = open(label_path, 'r')
    for x in range(25):
        print("Printing bottle cap " + str(x + 1))
        label = label_file.readline()

        if x < 10:
            digit = "0" + str(x)
        else:
            digit = str(x)
        cap_path = os.path.join(cap_folder, "okan_" + digit + ".tm2.arn_0x0_0.png")
        printBottleCap(cap_path, str(x + 1) + ". " + label.rstrip("\n"))
        
    return

def bugInfoTransform(image):
    transformed_image = Image.new("RGBA", (image.width, image.height), (0,0,0,0))
    original_dim = 256
    scale_factor = original_dim/image.width
    for y in range(image.height):
        for x in range(image.width):
            x_val = x/(0.96 + 0.05*x/image.width)#0.9*x + (x/image.width)*0.2
            x_val = round(x_val)
            #y_diff = round((-12 + 0.19*x - 0.00125*x*x + 0.00000146*x*x*x))
            y_diff = round((8.437695e-15 + 0.109375*x*scale_factor - 0.0004672461*(x*scale_factor)**2)/scale_factor)
            #y_diff = round((-8.114009 + 0.08162621*scale_factor*x - 0.0006351044*(scale_factor*x)**2 + 7.012523e-7*(scale_factor*x)**3)/scale_factor)
            if 0 <= x_val < image.width and 0<= y + y_diff < image.height:
                transformed_image.putpixel((x,y), image.getpixel((x_val, y + y_diff)))

    return transformed_image

def printBugInfo(img_path, string):
    sourceImage = Image.open(img_path)#.convert("RGBA")

    #Clear away existing text
    clear_size = (sourceImage.width,sourceImage.height)
    clear_pos = (0,0)

    rect = Image.new("RGBA", clear_size, (0, 0, 0, 0))
    sourceImage.paste(rect)

    draw = ImageDraw.Draw(sourceImage)

    font = "FONT\\FOT-Seurat Pro DB.otf"
    fontSize = 17
    fontColor = (0, 0, 0, 255)
    imFont = ImageFont.truetype(font, fontSize)

    draw.text( (16,9),string, fontColor, imFont, "la", 3, 'left')
    #sourceImage.show()
    
    #sourceImage.show()

    resample_scale_factor= 6
    bigImage = sourceImage.resize((sourceImage.width*resample_scale_factor, sourceImage.height*resample_scale_factor), resample=Image.LANCZOS)
    sourceImage = bugInfoTransform(bigImage)
    sourceImage = sourceImage.resize((sourceImage.width//resample_scale_factor, sourceImage.height//resample_scale_factor), resample=Image.LANCZOS)
    #sourceImage = sourceImage.filter(ImageFilter.SHARPEN)
    sourceImage = sourceImage.rotate(-2.5,Image.BICUBIC,expand=False, center=(0,0))
    #sourceImage.show()
    sourceImage.save(img_path)

    return

def printAllBugInfo():

    text_file = open(bug_label_path, "r", encoding="utf8")

    while True:
        headerLine = text_file.readline()
        if not headerLine:
            #EOF
            break
        if not headerLine.startswith("&"):
            #Filler line
            continue
        
        image_number = headerLine[1:].rstrip("\n").zfill(3)
        
        image_file_path = os.path.join(bug_folder, "book" + image_number + ".dat_0xc460_0.png")
        
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
        
        print("Printing Bug Info", image_number)
        printBugInfo(image_file_path, string_buffer) 
    
    text_file.close()
    return

def printCalendar(img_path, string, color):
    sourceImage = Image.open(img_path)

    #Clear away existing text
    sourceArray = numpy.array(sourceImage)
    maskArray = numpy.asarray(Image.open("FONT\\calendar_mask.png"))    
    mask = maskArray/255
    dst = sourceArray*mask
    cleanIm = Image.fromarray(dst.astype(numpy.uint8))
    
    rect = Image.new("RGBA", (112, 25), (0, 0, 0, 0))
    

    font = "FONT\\DFPOP1-C_0.ttc"
    fontSize = 22
    imFont = ImageFont.truetype(font, fontSize)
    augColor = (0, 0, 0, 255)

    draw = ImageDraw.Draw(rect)
    
    draw.text((45,4), "Aug.", augColor,imFont, "lt", 0, 'left' )
    draw.text((0,4), string, color,imFont, "lt", 0, 'left' )

    #Shear
    rect_array = numpy.array(rect)
    height, width, colors = rect_array.shape
    shX = -0.25
    shY = 0

    transform = [[1, shY, 0],
                 [shX, 1, 0],
                 [0, 0, 1]]
    
    rect_array =  ndimage.affine_transform(rect_array,
                                         transform,
                                         offset=(0, -height//2, 0),
                                         output_shape=(height, width+height//2, colors))
    rect = Image.fromarray(rect_array)

    #Rotate
    rect = rect.rotate(16,Image.BILINEAR,expand=True, fillcolor=(0,0,0,0))

    cleanIm.paste(rect, (-10,-11), rect )

    #cleanIm.show()
    cleanIm.save(img_path)

def printAllCalendars():

    for x in range(31):
        calendar_path = os.path.join(calendar_folder, "a_cal" + str(x+1) + ".tm2_0x0_0.png")
        print("Printing Calendar Day: " + str(x+1))
        printCalendar(calendar_path, day_strings[x%7], day_colors[x%7])

    return

def printDiary(img_path,stringL, stringR, alt_base_path=-1):

    if alt_base_path == -1:
        sourceImage = Image.open(img_path)
        baseImage = Image.open(diary_base_path)

        sourceImage = sourceImage.crop((0,0,512,195))

        baseImage.paste(sourceImage)
    else:
        linesImage = Image.open("GFX\\diary_base_lines.png")
        baseImage = Image.open(alt_base_path)
        baseImage.paste(linesImage, (0,0), linesImage)
    draw = ImageDraw.Draw(baseImage)

    font = "FONT\\KGMidnightMemories.ttf"
    #font = "FONT\\FOT-Seurat Pro DB.otf"
    fontSize = 26
    fontColor = (0, 0, 0, 255)
    imFont = ImageFont.truetype(font, fontSize)

    draw.text( (8,193), stringL, fontColor, imFont, "la", 2, 'left')
    draw.text( (253,193), stringR, fontColor, imFont, "la", 2, 'left')

    #baseImage.show()
    baseImage.save(img_path)
    return

def printAllDiary():
    text_file = open(diary_text_path, "r", encoding="utf8")

    while True:
        headerLine = text_file.readline()
        if not headerLine:
            #EOF
            break
        if not headerLine.startswith("&"):
            #Filler line
            continue
        
        image_number = headerLine[1:].rstrip("\n").zfill(3)
        image_name = "nik" + image_number + ".tm2_0x0_0.png"
        image_file_path = os.path.join(diary_folder, image_name)
        
        string_buffer = ["",""]
        LEFT = 0
        RIGHT = 1
        current_buffer = LEFT
        while True:
            cursor = text_file.tell()
            next_line = text_file.readline()
            if not next_line:
                #EOF
                break
            if next_line.startswith("///"):
                current_buffer = RIGHT
                continue

            if not next_line.startswith("&"):
                #Text line
                string_buffer[current_buffer] += next_line
                continue
            else:
                #Next entry reached
                text_file.seek(cursor)
                break
        
        print("Printing Diary", image_number)

        base_image_path = os.path.join("GFX","diary", "clean_diary_pages", image_name.replace(".png","_clean.png"))
        if os.path.exists(base_image_path):
            printDiary(image_file_path, string_buffer[0], string_buffer[1], alt_base_path=base_image_path) 
        else:
            printDiary(image_file_path, string_buffer[0], string_buffer[1]) 
    
    text_file.close()
    return

def getFontMap(font_path, start_row):
    font_file = open(font_path, "r")

    font = readFont(font_path, start_row*N_COLUMNS, INSERTION)

    for entry in font:
        index = font[entry]
        row = (index//N_COLUMNS)
        column = index % N_COLUMNS

        font[entry] = (column, row)

    return font

def updateKerning(file, index, val):
    file.seek(index)
    file.write(val.to_bytes(1, "little"))

    return

def getBoundedStringImage(string,im_font,baseline_adj, emphasis):
    test_field_width = 512
    test_field_size = (test_field_width,CELL_WIDTH)
    font_color = (255, 255, 255, 255)
    test_field_im = Image.new("RGBA", test_field_size, (0, 0, 0, 0))
    cursor = 0
    for char in string:
        
        if char == " ":
            cursor += SPACE_WIDTH + SPACING
            continue

        char_test_im = Image.new("RGBA", (30,22), (0, 0, 0, 0))
        draw = ImageDraw.Draw(char_test_im)

        draw.text( (4,17 +baseline_adj ),char, font_color, im_font, "ls", 0, 'left')

        if emphasis != 1.0:
            char_data = char_test_im.getdata()

            alpha_blended_char = []
            for item in char_data:
                alpha_blended_char.append((item[0], item[1], item[2], round(min(255, item[3]*emphasis))))
            char_test_im.putdata(alpha_blended_char)

        bounds = char_test_im.getbbox()
        if bounds == None:
            continue
        full_bounds = (bounds[0],0, bounds[2], CELL_WIDTH)
        char_im = char_test_im.crop(full_bounds)
        #char_im.show()

        test_field_im.paste(char_im, (cursor,0))
        cursor += char_im.width + SPACING
    
    cursor -= SPACING
    string_bounds = test_field_im.getbbox()
    if string_bounds == None:
        #handle no bounding box (only spaces)
        space_count = string.count(" ")
        string_bounds = (0,0,cursor, CELL_WIDTH)
    else:
        num_leading_spaces = len(os.path.commonprefix(["        ", string]))
        l_bound = string_bounds[0] - num_leading_spaces*(SPACE_WIDTH+SPACING)
        cursor -= num_leading_spaces*(SPACE_WIDTH+SPACING)
        assert l_bound >=0
        string_bounds = (l_bound,0, string_bounds[0] + cursor, CELL_WIDTH)
    test_field_im = test_field_im.crop(string_bounds)
    #test_field_im.show()
    return test_field_im

def printFont(font_im, font_map, im_font, kern=False, monospace=-1, baseline_adj=0, emphasis=1.0):
    '''Prints the given font text and compaction map into an image'''
    #src_img = Image.open(img_path)

    draw = ImageDraw.Draw(font_im)

    kerningFile = open(KERNING_PATH, 'r+b')

    for entry in font_map:
        row = font_map[entry][1]
        column = font_map[entry][0]
        x_coord = column * CELL_WIDTH
        y_coord = row * CELL_WIDTH


        entry_im = getBoundedStringImage(entry,im_font,baseline_adj, emphasis)
        if kern == True:
            kerningIndex = column + row*N_COLUMNS
            if monospace == -1:
                updateKerning(kerningFile,kerningIndex, entry_im.width)
            else:
                updateKerning(kerningFile,kerningIndex, monospace)
        font_im.paste(entry_im, (x_coord, y_coord))

    kerningFile.close()
    #font_im.show()
    return font_im


def printAllFonts():
    font_size = (512,1024)
    font_color = (255, 255, 255, 255)
    font_im = Image.new("RGBA", font_size, (0, 0, 0, 0))

    for entry in FONTS:
        entry = FONTS[entry]
        imFont = ImageFont.truetype(entry["typeface"], entry["font_size"], layout_engine=ImageFont.LAYOUT_RAQM)
        map = getFontMap(entry["font_map"], entry["row_offset"])
        printFont(font_im, map, imFont, kern=entry["kern"],
                             monospace=entry["monospace"], 
                             baseline_adj=entry["baseline_adjust"],
                             emphasis=entry["emphasis"])
        
        #font_im.paste(font_im, (0,0))
    #font_im.show()
    fixPO("boku-no-natsuyasumi-2\\m_a01000\\MAP\\en\\M_B25000.po")
    po = polib.pofile("boku-no-natsuyasumi-2\\m_a01000\\MAP\\en\\M_B25000.po")
    map = textCompaction.mapCompactions(po,2)

    cFont = FONTS["base"]
    imFont = ImageFont.truetype(cFont["typeface"], cFont["font_size"], layout_engine=ImageFont.LAYOUT_RAQM)
    printFont(font_im, map, imFont, kern=True, monospace=-1, baseline_adj=0)
    #font_im.show()
    font_im.save(FONT_IMAGE_PATH)
    return map

#printAllFonts()

desc = """Chinese Peacock
These large butterflies
suddenly pop out when
I step into the woods.
Their inky black wings
shine so pretty."""

desc1 = """I finally made it to my
uncle's beach house!
The big summery sun
shined down all the
way to the port.
"""

desc2 = """Listening close from
my bed, I can hear
the sound of the
waves."""

#printAllBugInfo()
printAllDiary()
#printAllBottleCaps()
#printDiary("nik001.tm2_0x0_0.png", desc1, desc2)
#printBugInfo("imgTestBUG.PNG", desc)
#printBottleCap("IMG_GFX_EDITS\\system\\submenu\\img\\okan_23.tm2.arn_0x0_0.png", "24. Relict Dragonfly")
#printCalendar("IMG_GFX_EDITS\\system\\submenu\\img\\a_cal7.tm2_0x0_0.png", "Sat", (41,105,140,255))
#printCalendar("IMG_GFX_EDITS\\system\\submenu\\img\\a_cal1.tm2_0x0_0.png", "Sun", (144,53,40,255))