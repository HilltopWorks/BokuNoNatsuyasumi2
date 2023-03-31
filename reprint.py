from PIL import Image,ImageDraw,ImageFont, ImageFilter
import os
import numpy
import copy
import shutil
from pathlib import Path
import math
import re
import cv2
from scipy import ndimage

#Calendar
day_strings = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
day_colors = [(144,53,40,255), (53,53,53,255), (151,77,46,255), (33,41,122,255), (85,57,47,255) ,(40,74,61,255), (41,105,140,255)]
diary_base_path = "FONT/diary_base.png"
diary_folder = "IMG_GFX_EDITS\\system\\submenu\\img"

#Bottle Caps
cap_folder = "IMG_GFX_EDITS\\system\\submenu\\img"
label_path = "GFX\\bottle_caps.txt"

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
    fontSize = 18
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
    sourceImage.show()
    sourceImage.save("imgTestBUG.PNG")

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
        calendar_path = os.path.join(diary_folder, "a_cal" + str(x+1) + ".tm2_0x0_0.png")
        print("Printing Calendar Day: " + str(x+1))
        printCalendar(calendar_path, day_strings[x%7], day_colors[x%7])

    return

def printDiary(img_path,stringL, stringR):
    sourceImage = Image.open(img_path)
    baseImage = Image.open(diary_base_path)

    sourceImage = sourceImage.crop((0,0,512,195))

    baseImage.paste(sourceImage)

    

    draw = ImageDraw.Draw(baseImage)

    font = "FONT\\VarelaRound-Regular.ttf"
    #font = "FONT\\FOT-Seurat Pro DB.otf"
    fontSize = 21
    fontColor = (0, 0, 0, 255)
    imFont = ImageFont.truetype(font, fontSize)

    draw.text( (8,196), stringL, fontColor, imFont, "la", 7, 'left')
    draw.text( (262,196), stringR, fontColor, imFont, "la", 7, 'left')

    baseImage.show()
    baseImage.save(img_path)
    return

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

#printAllCalendars()
#printAllBottleCaps()
#printDiary("nik001.tm2_0x0_0.png", desc1, desc2)
#printBugInfo("imgTestBUG.PNG", desc)
#printBottleCap("IMG_GFX_EDITS\\system\\submenu\\img\\okan_23.tm2.arn_0x0_0.png", "24. Relict Dragonfly")
#printCalendar("IMG_GFX_EDITS\\system\\submenu\\img\\a_cal7.tm2_0x0_0.png", "Sat", (41,105,140,255))
#printCalendar("IMG_GFX_EDITS\\system\\submenu\\img\\a_cal1.tm2_0x0_0.png", "Sun", (144,53,40,255))