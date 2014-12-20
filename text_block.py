import bpy, re

class TextBlock:
    def __init__(self, text_block):
        self.text_block = text_block
        
    @property
    def current_line(self):
        return self.text_block.current_line.body
    @current_line.setter
    def current_line(self, text):
        self.text_block.current_line.body = text
       
    @property
    def current_character_index(self):
        return self.get_character_index()
    @current_character_index.setter
    def current_character_index(self, index):
        self.set_cursor_position_horizontal(index)
        
    @property
    def current_line_index(self):
        return self.get_line_index()
    @current_line_index.setter
    def current_line_index(self, index):
        self.set_cursor_position_vertical(index)
        
    @property
    def line_amount(self):
        return len(self.text_block.lines)
        
    @property
    def text_before_cursor(self):
        return self.current_line[:self.current_character_index]
        
    @property
    def current_word(self):
        return self.get_last_word(self.text_before_cursor)
    
    # 'bpy.context.sce' -> 'sce'
    def get_last_word(self, text):
        match = re.search("(?!\w*\W).*", text)
        if match: return match.group()
        return ""
        
    @property
    def parents_of_current_word(self):
        return self.get_parent_words(self.text_before_cursor)
    
    # 'bpy.context.sce' -> ['bpy', 'context']    
    def get_parent_words(self, text):
        parents = []
        text = self.text_before_cursor
        while True:
            parent = self.get_parent_word(text)
            if parent is None: break
            text = text[:-len(self.get_last_word(text))-1]
            parents.append(parent)
        parents.reverse()
        return parents
        
    @property
    def parent_of_current_word(self):
        return self.get_parent_word(self.text_before_cursor)
    
    # 'bpy.context.sce' -> 'context'
    def get_parent_word(self, text):
        match = re.search("(\w+)\.(?!.*\W)", text)
        if match:
            return match.group(1)
        return None
        
    @property
    def text(self):
        return self.text_block.as_string()
        
    def get_existing_words(self):
        existing_words = []
        existing_parts = set(re.sub("[^\w]", " ", self.text).split())
        for part in existing_parts:
            if not part.isdigit(): existing_words.append(part)
        return existing_words
            
    def insert(self, text):
        self.make_active()
        bpy.ops.text.insert(text = text)
        
    def get_current_text_after_pattern(self, pattern):
        return self.get_text_after_pattern(pattern, self.text_before_cursor)
        
    def get_text_after_pattern(self, pattern, text):
        match = self.get_last_match(pattern, text)
        if match:
            return text[match.end():]
            
    def get_last_match(self, pattern, text):
        match = None
        for match in re.finditer(pattern, text): pass
        return match
        
    def delete_current_word(self):
        match = re.search("\w*\z", self.text_before_cursor)
        if match:
            length = match.end() - match.start()
            for i in range(length):
                self.remove_character_before_cursor()
        
    def set_selection_in_line(self, start, end):
        line = self.current_line_index
        if start > end: start, end = end, start
        self.set_selection(line, start, line, end)
        
    def set_selection(self, start_line, start_character, end_line, end_character):
        self.set_cursor_position(start_line, start_character, select = False)
        self.set_cursor_position(end_line, end_character, select = True)
        
    def set_cursor_position(self, line_index, character_index, select = False):
        self.set_cursor_position_vertical(line_index, select)
        self.set_cursor_position_horizontal(character_index, select)
        
    def set_cursor_position_horizontal(self, target_index, select = False):
        self.move_cursor_to_line_end(select)
        self.move_cursor_left_to_target_index(target_index, select)
            
    def move_cursor_left_to_target_index(self, target_index, select):
        target_index = max(1, target_index)
        while self.get_character_index(select) >= target_index:
            self.move_cursor_left(select)
        
    def set_cursor_position_vertical(self, target_line, select = False):
        move_function = self.move_cursor_up
        if target_line > self.get_line_index(select):
            move_function = self.move_cursor_down
        move_amount = abs(self.current_line_index - target_line)
        for i in range(move_amount):
            move_function(select)
            
    def get_character_index(self, select = False):
        if select: return self.text_block.select_end_character
        return self.text_block.current_character
    def get_line_index(self, select = False):
        return self.text_block.current_line_index
            
    def move_cursor_to_line_begin(self, select = False):
        self.move_cursor("LINE_BEGIN", select)
    def move_cursor_to_line_end(self, select = False):
        self.move_cursor("LINE_END", select)  
        
    # note: this may change the character index more than one (if there is TAB)
    def move_cursor_right(self, select = False):
        self.move_cursor("NEXT_CHARACTER", select)
    def move_cursor_left(self, select = False):
        self.move_cursor("PREVIOUS_CHARACTER", select)   
        
    def move_cursor_up(self, select = False):
        self.move_cursor("PREVIOUS_LINE", select)
    def move_cursor_down(self, select = False):
        self.move_cursor("NEXT_LINE", select)
        
    def move_cursor(self, type, select = False):
        self.make_active()
        if select: bpy.ops.text.move_select(type = type)
        else: bpy.ops.text.move(type = type)
        
    def remove_character_before_cursor(self):
        self.make_active()
        bpy.ops.text.delete(type = "PREVIOUS_CHARACTER")
        
    def make_active(self):
        bpy.context.space_data.text = self.text_block
        
     