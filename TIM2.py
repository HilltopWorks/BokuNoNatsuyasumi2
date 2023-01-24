from PIL import Image,ImageDraw
import os
import numpy
import copy
import shutil
import numpy as np
from pathlib import Path
import resource
import re

PALETTE_END_ADDR = 0x28
PALETTE_START = 0xa0
GRAPHIC_START = 0x500

#After PALETTE_END_ADDR value
GRAPHIC_WIDTH_ADDR  = 0x30
GRAPHIC_HEIGHT_ADDR = 0x34

GRAPHIC_WIDTH = 0x100
GRAPHIC_HEIGHT = 0x80

TEX_SIZE = 0x8800

#Font
FONT_END = 0x5c0c0
FONT_START = 0xc0

FONT_WIDTH_PX = 32
FONT_HEIGHT_PX = 32
FONT_WIDTH_BYTES = 0x10

FONT_PATH = "C:\dev\maid\BD_EXTRACT\MAP_0x17b6800_0x17f6840"
FONT_CLUT = [0,0x1D,0x27,0x30,0x39,0x3f,0x8c,0x9c,0xa8,0xb3,0xc1,0xd4,0xe4,0xee,0xf6,0xff]

GLYPH_SIZE = FONT_WIDTH_BYTES * FONT_HEIGHT_PX
NUM_GLYPHS = (FONT_END - FONT_START)//GLYPH_SIZE

EDIT_FOLDER = "IMAGE_EDITS"
REBUILD_FOLDER = "BD_EDITS"
INPUT_FOLDER = "BD_EXTRACT"
OUTPUT_FOLDER = "GFXrip" #TEST / GFXrip

IMG_PATH = "ISO_RIP/boku2.img"
IMG_FOLDER = "IMG_RIP"
IMG_GFX_FOLDER = "IMG_GFX_RIP"

MAP_FOLDER = "MAP_RIP"
MAP_GFX_FOLDER = "MAP_GFX_RIP"

MAP_TYPE = 1
IMG_TYPE = 2
FILE_ERROR = -1



def TIM2_to_PNG(tim2_file_path, offset):
    stem = Path(tim2_file_path).stem
    basename = os.path.basename(tim2_file_path)
    TIM2_file = open(tim2_file_path, 'rb')
    
    TIM2_file.seek(offset)
    fileType = TIM2_file.read(4).decode()

    if fileType != "TIM2":
        print("TIM2 FILE MISSING HEADER!!! Filename: " +  basename )
        return FILE_ERROR

    version = resource.readByte(TIM2_file)
    TIM2_format = resource.readByte(TIM2_file)

    

    num_images = resource.readShort(TIM2_file)

    whitespace1 = resource.readInt(TIM2_file)

    buffer = 0
    #literally why
    if whitespace1 == 0x4001a0 or TIM2_format == 1:
        buffer = 0x70

    if num_images != 1:
        print("!!!!!!!!! UH OH, NUM IMAGES IN TIM2 != 0! IT'S " + str(num_images))
    TIM2_file.seek(buffer + offset +0x10)


    total_image_size = resource.readInt(TIM2_file)
    palette_size = resource.readInt(TIM2_file)

    

    pxl_size = resource.readInt(TIM2_file)
    header_size = resource.readShort(TIM2_file)
    n_palette_entries = resource.readShort(TIM2_file)

    #(0=8bbp indexed)
    color_depth = resource.readByte(TIM2_file)
    n_mipmaps = resource.readByte(TIM2_file)
    #(1=16bbp, 2=24bpp, 3=32bbp, 4=4bbp, 5=8bpp)
    CLUT_format = resource.readByte(TIM2_file)
    #(1=16bbp, 2=24bpp, 3=32bbp, 4=4bbp, 5=8bpp)
    image_format = resource.readByte(TIM2_file)

    if CLUT_format == 1:
        bpp = 16
    elif CLUT_format == 2:
        bpp = 24
    elif CLUT_format == 3:
        bpp = 32
    elif CLUT_format == 4:
        bpp = 4
    elif CLUT_format == 5:
        bpp = 8
    elif CLUT_format == 0:
        bpp = 0
    

    CLUT_size = n_palette_entries*bpp/8
    if CLUT_size > 0:
       nPalettes = int(palette_size//CLUT_size)

    im_width = resource.readShort(TIM2_file)
    im_height = resource.readShort(TIM2_file)

    GsTEX0 = resource.readLong(TIM2_file)
    GsTEX1 = resource.readLong(TIM2_file)

    GsRegs = resource.readInt(TIM2_file)
    GsTexClut = resource.readInt(TIM2_file)
    

    if CLUT_format & 0x80 != 0:
        linear_CLUT = True
    else:
        linear_CLUT = False
    
    CLUT_format = CLUT_format & 0x7F
    TIM2_file.seek(buffer + offset + header_size + 0x10)

    graphics = []
    
    for x in range(im_width * im_height):
        #(1=16bbp, 2=24bpp, 3=32bbp, 4=4bbp, 5=8bpp)
        if image_format == 3:
            graphics += [int.from_bytes(TIM2_file.read(4), "little")]
        elif image_format == 2:
            graphics += [int.from_bytes(TIM2_file.read(3), "little")]
        elif image_format == 1:
            graphics += [int.from_bytes(TIM2_file.read(2), "little")]
        elif image_format == 5:
            graphics += [int.from_bytes(TIM2_file.read(1), "little")]
        elif image_format == 4:
            cursor = TIM2_file.tell()
            next_byte = int.from_bytes(TIM2_file.read(1), "little")
            if x % 2 == 0:
                graphics += [next_byte & 0x0F]
                TIM2_file.seek(cursor)
            else:
                graphics += [(next_byte & 0xF0) >> 4 ]


    if CLUT_format == 3 or CLUT_format == 0:
        pass
    else:
        assert False, "OH NO, CLUT FORMAT NOT 32 bit or DIRECT COLOR!!! File: " + tim2_file_path + " OFFSET:" + str(offset)

    if CLUT_format == 3:
        ims = []
        for x in range(nPalettes):
            CLUT_array = numpy.zeros((16, 16 , 4), dtype=numpy.uint8)
            palette = []


            for x in range(n_palette_entries):
                palette += [int.from_bytes(TIM2_file.read(4), "little")]

                red =    palette[x] &       0xFF
                green = (palette[x] &     0xFF00) >> 8
                blue =  (palette[x] &   0xFF0000) >> 16
                alpha = (palette[x] & 0xFF000000) >> 24
                if not linear_CLUT and (image_format == 3 or image_format == 5):
                    if x % 32 >= 8 and x % 32 < 24:
                        flipper = x % 16
                        if flipper >= 8:
                            CLUT_array[1 + (x//16)][x%8] = (red, green, blue, alpha)
                        else:
                            CLUT_array[(x//16) - 1][8 + (x%8)] = (red, green, blue, alpha)
                    else:
                        CLUT_array[x//16][x%16] = (red, green, blue, alpha)
                else:
                    CLUT_array[x//16][x%16] = (red, green, blue, alpha)

            clut_im = Image.fromarray(CLUT_array, "RGBA")

            os.makedirs(os.path.join(OUTPUT_FOLDER, "CLUT/"), exist_ok=True)

            clut_im.save(os.path.join(OUTPUT_FOLDER, "CLUT/", stem + "_" + hex(offset) + "_" + str(x) + "CLUT.png"))

            image_array = numpy.zeros((im_height, im_width , 4), dtype=numpy.uint8)
            for pixel_number in range(im_width * im_height):

                x = graphics[pixel_number]
                red =   CLUT_array[x//16][x%16][0]
                green = CLUT_array[x//16][x%16][1]
                blue =  CLUT_array[x//16][x%16][2]
                alpha = min(CLUT_array[x//16][x%16][3] * 2, 255)
                

                pixel_color = (red, green, blue,  alpha)
                
                image_array[pixel_number//im_width][pixel_number%im_width] = pixel_color
            
            
            im = Image.fromarray(image_array, "RGBA")
            #im.show()
            ims.append(im)
        return ims
    
    elif CLUT_format == 0:
        image_array = numpy.zeros((im_height, im_width , 4), dtype=numpy.uint8)
        for pixel_number in range(im_width * im_height):

            pixel = graphics[pixel_number]
            red =   pixel & 0xFF
            green = (pixel & 0xFF00) >> 8
            blue =  (pixel & 0xFF0000) >> 16
            alpha = min(2*((pixel & 0xFF000000) >> 24), 255)
            

            pixel_color = (red, green, blue,  alpha)
            
            image_array[pixel_number//im_width][pixel_number%im_width] = pixel_color


        im = Image.fromarray(image_array, "RGBA")
        #im.save(os.path.join(OUTPUT_FOLDER, stem + "_offset_" + hex(offset) + ".png"))
        #im.show()
        return [im]


def ripTIMpack(file_path, type):
    pack_file = open(file_path, 'rb')
    stem = Path(file_path).stem
    basename = os.path.basename(file_path)
    extension = Path(file_path).suffix

    n_entries = resource.readInt(pack_file)

    for x in range(n_entries):
        pack_file.seek(4 + x*8)
        offset = resource.readInt(pack_file)
        size = resource.readInt(pack_file)


        

        if type == MAP_TYPE:
            
            dir_name = os.path.split(os.path.dirname(file_path))[1]
            out_path = os.path.join(MAP_GFX_FOLDER, dir_name, stem + "_" + str(x) + ".PNG")
            if not os.path.exists(out_path):
                os.makedirs(os.path.join(MAP_GFX_FOLDER, dir_name), exist_ok=True)
                ims = TIM2_to_PNG(file_path, offset)
                ims[0].save(out_path)
                if len(ims) > 1:
                    print("___NOTE!!: MAP IMAGE HAS MORE THAN 1 CLUT!!!")
        else:
            #TODO handle IMG
            pass

    return

def unpackMap():
    
    for dir in os.listdir(MAP_FOLDER):


        #File 6

        path_6 = os.path.join(MAP_FOLDER, dir, "6.bin")
        try:
            ripTIMpack(path_6, MAP_TYPE)
        except FileNotFoundError:
            print("Image 6 not found in map " + dir + ", Skipping...")

        #File 3 = map image

        path_3 = os.path.join(MAP_FOLDER, dir, "3.bin")
        try:
            ims = TIM2_to_PNG(path_3, 0)
            if len(ims) > 1:
                print("___NOTE!!: MAP IMAGE 3 HAS MORE THAN 1 CLUT!!!")
            image_3 = ims[0]
            os.makedirs(os.path.join(MAP_GFX_FOLDER, dir), exist_ok=True)
            image_3.save(os.path.join(MAP_GFX_FOLDER, dir, "3.PNG"))
        except FileNotFoundError:
            print("Image 3 not found in map " + dir + ", Skipping...")
        
        #File 10

        path_10 = os.path.join(MAP_FOLDER, dir, "10.bin")
        try:
            ripTIMpack(path_10, MAP_TYPE)
        except FileNotFoundError:
            print("Image 10 not found in map " + dir + ", Skipping...")

    return

def findTIM2s(file_path):

    TIM2_header = ('\x54\x49\x4d\x32').encode()

    #print(mm.find(TIM2_header))
    
    infile = file_path
    with open(infile, "rb") as f:
        data = f.read()

    matches = []                # initializes the list for the matches
    curpos = 0                  # current search position (starts at beginning)
    pattern = re.compile(TIM2_header)   # the pattern to search
    while True:
        m = pattern.search(data[curpos:])     # search next occurence
        if m is None: break                   # no more could be found: exit loop
        print("Found TIM2 at " + hex(curpos + m.start()) + " in " + file_path)
        matches.append(curpos + m.start()) # append a pair (pos, string) to matches
        curpos += m.end()          # next search will start after the end of found string

    print("Searching for matches complete")


    return matches

def unpackIMGTIM2s():

    for subdir, dirs, files in os.walk(IMG_FOLDER):
        for file in files:
            # checking if it is a file
            path = os.path.join(subdir, file)
            f=open(path,'rb')
            if os.path.isfile(path):
                print("Checking " + path)
                TIM2_offsets = findTIM2s(path)

                for offset in TIM2_offsets:
                    ims = TIM2_to_PNG(path, offset)
                    for x in range(len(ims)):
                        im = ims[x]
                        img_file_path = path.replace(IMG_FOLDER, IMG_GFX_FOLDER)
                        img_file_path = img_file_path + "_" + hex(offset) + "_" + str(x) + '.png'
                        directory = str(Path(img_file_path).parent)
                        os.makedirs(directory, exist_ok=True)
                        im.save(img_file_path)



def unpackFont(filepath):
    font_file = open(filepath, 'rb')
    font_file.seek(FONT_START)

    columns = 32
    rows = NUM_GLYPHS //columns

    font_array = numpy.zeros((rows * FONT_HEIGHT_PX, columns * FONT_WIDTH_PX , 3), dtype=numpy.uint8)
    
    for glyph_number in range(NUM_GLYPHS):
        base_x = (glyph_number % columns) * FONT_WIDTH_PX
        base_y =  (glyph_number // columns) * FONT_HEIGHT_PX
        for v in range(FONT_HEIGHT_PX):
            for u in range(FONT_WIDTH_BYTES):
                next_byte = int.from_bytes(font_file.read(1), 'little')
                pixel1 = (next_byte & 0xF0) >> 4
                pixel2 = (next_byte & 0x0F)

                if pixel1 == 0:
                    font_array[base_y + v][base_x + u*2] = (255,0,255)
                else:
                    greyscale_color = FONT_CLUT[pixel1]
                    font_array[base_y + v][base_x + u*2] = (greyscale_color,greyscale_color,greyscale_color)

                if pixel2 == 0:
                    font_array[base_y + v][base_x + u*2 + 1] = (255,0,255)
                else:
                    greyscale_color = FONT_CLUT[pixel2]
                    font_array[base_y + v][base_x + u*2 + 1] = (greyscale_color,greyscale_color,greyscale_color)

    im = Image.fromarray(font_array, "RGB")
    im.show()

    return


def closest(colors,color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = int(np.where(distances==np.amin(distances))[0][0])
    smallest_distance = colors[index_of_smallest]
    return index_of_smallest 

def getAlpha(palette):
    for color_num in range(256):
        if palette[color_num][3] == 0:
            return color_num

    #print("ERROR: ALPHA NOT FOUND!!!!")
    return 0

def get_palette(target_TEX_path, offset):
    tex_file = open(target_TEX_path, 'rb')
    tex_file.seek(offset + PALETTE_START)

    palette = []
    CLUT_array = numpy.zeros((16, 16 , 4), dtype=numpy.uint8)
    for x in range(256):
        palette += [int.from_bytes(tex_file.read(4), "little")]

        red =    palette[x] &       0xFF
        green = (palette[x] &     0xFF00) >> 8
        blue =  (palette[x] &   0xFF0000) >> 16
        alpha = (palette[x] & 0xFF000000) >> 24
        if x % 32 >= 8 and x % 32 < 24:
            flipper = x % 16
            if flipper >= 8:
                CLUT_array[1 + (x//16)][x%8] = (red, green, blue, alpha)
            else:
                CLUT_array[(x//16) - 1][8 + (x%8)] = (red, green, blue, alpha)
        else:
            CLUT_array[x//16][x%16] = (red, green, blue, alpha)
    
    return CLUT_array

def packTEX2(target_TEX_path, offset, reference_PNG_path, edited_PNG_path):
    stem = Path(reference_PNG_path).stem
    basename = os.path.basename(reference_PNG_path)

    ref_im = Image.open(reference_PNG_path)
    edited_im = Image.open(edited_PNG_path)
    edited_im = edited_im.convert("RGBA")
    target_file = open(target_TEX_path, "r+b")

    target_file.seek(offset)

    #index_image = ref_im.convert('P', dither=Image.NONE, palette=Image.ADAPTIVE, colors=256)
    parent_tex = os.path.join("BD_EXTRACT", stem.split("_offset_")[0] + ".TEX")
    parent_offset = int(stem.split("_offset_0x")[1], base=16)
    palette_2D = get_palette(parent_tex, parent_offset)#ref_im.palette.colors
    palette = []
    for y in range(16):
        for x in range(16):
            palette += [palette_2D[y][x]]
    palette_array = []
    #for x in range(256):
    #    palette_array = palette_array + [palette[x]]

    for v in range(ref_im.height):
        for u in range(ref_im.width):
            ref_color = np.asarray(ref_im.getpixel((u,v)))
            ref_color[3] = min(255, ref_color[3]*2)
            edited_color = np.asarray(edited_im.getpixel((u,v)))
            edited_color[3] = min(255, edited_color[3]*2)

            if not np.array_equiv(ref_color, edited_color):
                if edited_color[3] == 0:
                    #Find any color with alpha=0
                    closest_color = getAlpha(palette)
                else:
                    closest_color = closest(palette, edited_color)
                
                graphics_val = closest_color
                target_file.seek(offset + v*ref_im.width + u)
                target_file.write(graphics_val.to_bytes(1, "little"))

    return



#takes path to an image and returns 8 bit indexed image with 32 bit RGBA clut
def convertTo8Bit(imagePath):
    stem = Path(imagePath).stem
    directory = os.path.dirname(imagePath)
    basename = os.path.basename(imagePath)

    image = Image.open(imagePath)
    #image.show()
    convertedImage = image.convert("P", palette=Image.ADAPTIVE, colors=256)
    #convertedImage.show()
    #print(len(convertedImage.palette.tobytes()))
    #print(convertedImage.tobytes())
    #convertedImage.save(os.path.join(directory, stem + "_8bit.png"))
    return convertedImage

def repack():

    for file in os.listdir(EDIT_FOLDER):
        stem = Path(file).stem
        directory = os.path.dirname(file)
        basename = os.path.basename(file)
        extension = Path(file).suffix
        if extension == ".png" or extension == ".PNG":
            parent_name = basename.split("_offset_")[0] + ".TEX"
            #TEX_file = open(os.path.join(REBUILD_FOLDER, parent_name), 'r+b')
            offset = basename.split("0x")[-1].split(".")[0]
            offset = int(offset, 16)
            reference_PNG_path = os.path.join(OUTPUT_FOLDER, file)
            edited_PNG_path =  os.path.join(EDIT_FOLDER, file)
            print("Packing Graphic: ", basename)
            referenceFilePath = os.path.join("INSTANCE", basename)
            parentFilePath = os.path.join("INSTANCE", basename + ".modified")
            shutil.copyfile(referenceFilePath, parentFilePath)
            if not os.path.exists(parentFilePath):
                shutil.copyfile( os.path.join("BD_EXTRACT", parent_name),parentFilePath)
                shutil.copyfile( os.path.join("BD_EXTRACT", parent_name),referenceFilePath)
            packTEX2(parentFilePath, 0, reference_PNG_path, edited_PNG_path)

    return

def prepareInsertionFiles():
    for file in os.listdir(EDIT_FOLDER):
        extension = Path(file).suffix
        basename = os.path.basename(file)
        if extension == ".png" or extension == ".PNG":
            parent_name = basename.split("_offset_")[0] + ".TEX"


#ripTIMpack(MAP_FOLDER + "/M_I01000/6.bin", MAP_TYPE)
#unpackIMGTIM2s()
#unpackMap()
#TIM2_to_PNG("C:\dev\\boku2\IMG_RIP\\system\\bumper2.tm2", 0x80)
#packTEX("C:\dev\maid\MAP_0x1521800_0x1546e00.TEX", 0x92d00, "C:\dev\maid\GFXrip\MAP_0x1521800_0x1546e00_offset_0x92d00 - Copy copy.png")
#convertTo8Bit("C:/Users/alibu/Desktop/MAP_0x1521800_0x15a8c00_133632.png")
#packTEX2("C:\dev\maid\BD_EDITS\MAP_0x7639000_0x7639040.TEX", 0, "C:\dev\maid\GFXrip\MAP_0x7639000_0x7639040_offset_0x0.png", "C:\dev\maid\IMAGE_EDITS\MAP_0x7639000_0x7639040_offset_0x0.png")
#unpackFont(FONT_PATH)
#unpackTEX2("C:\dev\maid\BD_EDITS\MAP_0x7639000_0x7639040.TEX")
#unpackAllTex()
#repack()