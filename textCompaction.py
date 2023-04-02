import os
import shutil
from pathlib import Path
import resource
import polib
import math
from MSG import readFont,INSERTION
import regex as re


COMPACTION_MIN = 2
COMPACTION_MAX = 16

SPACING = 2


START_ROW = 15
END_ROW = 45
N_COLUMNS = 23

BLOCK_CHAR = "扉"

#Gets frequency of each substring of length n in s
def getSubstringFrequency(s, n):
    substrings=[s[j:j+n]for j in range(len(s)-n+1)]

    unique_substrings = set(substrings)
    frequencies = {}

    for substring in unique_substrings:
        #count = len(re.findall(s, substring))
        count = substrings.count(substring)
        frequencies[substring] = count

    return frequencies

# Gets list of substrings and their appearance count across the given strings,
# within the MIN and MAX lengths
def getCompactions(strings):
    
    compaction_dict = {}

    for string in strings:
        for compaction_size in range(COMPACTION_MAX, COMPACTION_MIN -1, -1):
            if compaction_size > len(string):
                continue
            frequencies = getSubstringFrequency(string, compaction_size)

            for substring in frequencies:
                if substring in compaction_dict:
                    compaction_dict[substring] = compaction_dict[substring] + frequencies[substring]
                else:
                    compaction_dict[substring] = frequencies[substring]

    return compaction_dict

#Removes not-letter symbols from string
def isolateText(string):
    string = string.replace("{STOP}", '')
    #string = string.replace("\\n", '')
    string = string.replace("\'", "'")
    search_string = string
    while "{WAIT=0x" in string:
        start_index = string.index("{WAIT=0x")
        end_index = string[start_index:].index("}") + start_index
        symbol = string[start_index:end_index+1]
        string = string.replace(symbol, "")

    return re.split("\n|" + BLOCK_CHAR,string)  #string.split("\n")


#Returns a map of characters to their width
def getKerning(kerning_bin, font):
    kerning_file = open(kerning_bin, "rb")
    kerning = {}
    for char in font:
        kerning_file.seek(font[char])
        char_width = int.from_bytes(kerning_file.read(1), "little")
        kerning[char] = char_width

    return kerning

#Returns the superstring power value of a parent string
def getSuperstringPower(powers, superstring):
    superstring_power = 0
    for child_string in powers:
        if superstring.startswith(child_string) and len(superstring) > len(child_string):
            superstring_power += powers[child_string]

    return superstring_power

# Returns a sorted list of the byte saving potential of each substring,
# and a dictionary of substrings to cell sizes
def getSubstringPower(substring_frequencies, kerning):
    CELL_WIDTH = 0x16
    substring_powers = {}
    cell_counts = {}
    for substring in substring_frequencies:
        substring_width = 0
        for char in substring:
            substring_width += kerning[char] + SPACING
        substring_width -= SPACING

        if substring_width > 255:
            continue
        num_cells = math.ceil(substring_width/CELL_WIDTH)
        byte_savings = substring_frequencies[substring] * (len(substring) - 1)*2
        substring_powers[substring] = byte_savings#/num_cells
        cell_counts[substring] = num_cells

    sorted_powers = sorted(substring_powers.items(), key=lambda x:x[1], reverse=True)

    return sorted_powers,  cell_counts

#Finds the best compaction of text in a MSG table in a po file
def findBestCompactions(po, table_num):
    all_lines = []
    for entry in po:
        table_comment = "Table:" + str(table_num) + "-"
        if table_comment not in entry.comment:
            continue
        clean_lines = isolateText(entry.msgstr)
        all_lines += clean_lines

    compactions = getCompactions(all_lines)

    font = readFont("font-inject.txt", 0, INSERTION)
    kerning = getKerning("font_kerning.bin", font)

    return getSubstringPower(compactions,kerning)

# Erases substring power of given parent string from child strings,
# and removes it from the dictionary
def removeSubstring(compactions, cell_counts, string):

    for x in range(len(compactions)):
        if compactions[x][0] == string:
            parent_power = compactions[x][1]
            parent_cell_count = cell_counts[string]
            parent_byte_save = parent_power*cell_counts[string]
            parent_byte_save_per_appearance = ((len(string) - 1)*2)
            parent_appearance_count = parent_byte_save/parent_byte_save_per_appearance
            parent_index = x
            break

    for x in range(len(compactions)):
        child_string = compactions[x][0]
        child_power = compactions[x][1]
        child_cell_count = cell_counts[child_string]
        child_byte_save = child_power*child_cell_count
        child_byte_save_per_appearance = ((len(child_string) - 1)*2)
        child_appearance_count = child_byte_save/child_byte_save_per_appearance

        if child_string in string and len(string) > len(child_string):
            compactions[x] = (child_string,(child_appearance_count - parent_appearance_count)*child_byte_save_per_appearance/child_cell_count)
            #compactions[x] = (child_string,compactions[x][1] - (parent_appearance_count*child_byte_save_per_appearance/child_cell_count))
            #compactions[x][1] -= (parent_appearance_count*(len(child_string)-1)*2)/cell_counts[child_string]
        elif string in child_string and len(child_string) > len(string):
            diff = (child_byte_save_per_appearance - parent_byte_save_per_appearance)*child_appearance_count/child_cell_count
            compactions[x] = (child_string,compactions[x][1] - diff)
            #compactions[x] = (child_string,compactions[x][1] - (parent_appearance_count*(len(string)-1)*2)/cell_counts[child_string])
            #compactions[x][1] -= (parent_appearance_count*(len(string)-1)*2)/cell_counts[child_string]

    compactions.pop(parent_index)
    compactions.sort(key = lambda a: a[1], reverse=True)
    return compactions

def processDuplication(compactions, cell_counts, free_cells):
    compaction_map = {}

    for x in range(len(compactions)):
        #TODO: when substring is plucked, lessen substrings and superstrings of it
        compaction = compactions[0][0]
        for row_number in range(len(free_cells)):
            if cell_counts[compaction] <= free_cells[row_number]:
                #Add to map
                #map[substring] = (column, row)
                compaction_map[compaction] = (free_cells[row_number] - N_COLUMNS, row_number + START_ROW)
                free_cells[row_number] -= cell_counts[compaction]

                #best_compactions.pop(compaction)
                compactions = removeSubstring(compactions, cell_counts, compaction)
                break

            elif row_number == END_ROW - START_ROW:
                #No space for compaction, skip it
                compactions.pop(compaction)
            else:
                #Try next row
                continue

    return compaction_map


def remove_string_from_po(po,string):
    for entry in po:
        entry.msgstr = entry.msgstr.replace(string, "扉")

    return po

def mapCompactions(po, table_num):
    total_savings = 0

    free_cells = []
    skipped_entries = 0
    for x in range(END_ROW - START_ROW):
        free_cells.append(N_COLUMNS)

    cells_remaining = (END_ROW - START_ROW)*N_COLUMNS
    
    compaction_map = {}
    while cells_remaining > 0:

        best_compactions, cell_counts = findBestCompactions(po, table_num)
        if len(best_compactions) == 0:
            #print("Total Savings:", total_savings , "bytes")
            break
        next_string = best_compactions[0][0]
        next_size = cell_counts[next_string]

        for row_number in range(len(free_cells)):
            if next_size <= free_cells[row_number]:
                #Add to map
                #map[substring] = (column, row)
                compaction_map[next_string] = (N_COLUMNS - free_cells[row_number], row_number + START_ROW)
                free_cells[row_number] -= next_size

                po = remove_string_from_po(po, next_string)
                print("Added to map:", next_string)
                total_savings += best_compactions[0][1]
                print("Saved:",best_compactions[0][1],"bytes", "Total Savings:", total_savings , "bytes")
                break

            elif row_number == END_ROW - START_ROW:
                #No space for compaction, skip it
                best_compactions.pop(0)
            else:
                #Try next row
                continue
        
        if len(best_compactions) == 0:
            #print("Total Savings:", total_savings , "bytes")
            break



    #compaction_map = processDuplication(best_compactions, cell_counts, free_cells)
    
    updateKerning(compaction_map, "font_kerning.bin")
    return compaction_map


def updateKerning(map, kerning_path):
    kerning_file = open(kerning_path, "r+b")
    font = readFont("font-inject.txt", 0, INSERTION)
    kerning = getKerning(kerning_path, font)

    kerning_file.seek(START_ROW*N_COLUMNS)

    for x in range((END_ROW - START_ROW)*N_COLUMNS):
        null = 0
        kerning_file.write(null.to_bytes(1, "little"))

    for mapping in map:
        string = mapping
        column = map[mapping][0]
        row = map[mapping][1]

        string_width = 0
        for char in string:
            string_width += kerning[char] + SPACING
        string_width -= SPACING

        assert string_width < 256, "STRING TOO LONG TO KERN: " + string 
        kerning_file.seek(column + row*N_COLUMNS)
        kerning_file.write(string_width.to_bytes(1, "little"))


        
    return

#print(re.findall("11", "1011101111", overlapped=False))   

po = polib.pofile("boku-no-natsuyasumi-2\\m_a01000\\MAP\\en\\M_B25000.po")
map = mapCompactions(po,2)
#list = findBestCompactions(po, 2)
#updateKerning(map, "font_kerning.bin")
pass
#print(isolateText("Hello{WAIT=0x12}, {STOP} dinosaur\nwings{WAIT=0x2}monkey"))
#print(getCompactions(["strings", "rings", "spaghetti and meatballsrings"]))