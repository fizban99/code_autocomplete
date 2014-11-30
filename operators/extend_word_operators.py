import bpy, keyword
from script_auto_complete.text_editor_utils import *
from script_auto_complete.operators.text_operators import *

words = []

def get_extend_word_operators():
    operators = []
    word_start = get_word_start().upper()
    all_existing_words = words
    additional_existing_words = []
    for word in all_existing_words:
        if word.upper().startswith(word_start):
            operators.append(ExtendWordOperator(word))
        else:
            additional_existing_words.append(word)
    return operators

def get_word_start():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    text = text_line.body
    character_index = text_block.current_character
    return text[get_word_start_index(text, character_index):character_index]
    
def get_word_start_index(text, character_index):
    for i in reversed(range(0, character_index)):
        if text[i].upper() not in word_characters:
            return i + 1
    return 0
    
def update_word_list():
    global words
    words = []
    words.extend(get_existing_words())
    words.extend(keyword.kwlist)
    words = list(set(words))
    words.sort(key = str.lower)
    