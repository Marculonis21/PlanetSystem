#!/usr/bin/env python3

import pygame as PG

# Basic UI class - defines drawing
class UI:
    def __init__(self):
        self.image = None           # can be drawn as an image
        self.items = []             # collection text items
        self.itemPos = PG.Vector2() # text positions
        self.inputs = []            # collection of text inputs
        self.radioButtons = []      # collection of radio buttons

        self.FONT = PG.font.SysFont('Arial', 20, False, False) # default font

    def Draw(self, screen, pos):
        pos = PG.Vector2(pos)

        if (self.image != None):
            screen.blit(self.image, pos)

        for index, t in enumerate(self.items): # Printing text items
            textSurface = self.FONT.render(t, True, PG.Color("white"))
            screen.blit(textSurface, (pos.x+self.itemPos.x, 
                                      pos.y+self.itemPos.y + 25*index))

        # Draw all text inputs and buttons
        for inp in self.inputs: inp.Draw(screen)
        for rb in self.radioButtons: rb.Draw(screen)

class ObjPopup(UI):
    def __init__(self):
        super().__init__()
        self.obj = None # Save which object (planet) is being affected

        self.itemPos = PG.Vector2(25, 15) 
        self.items = ["Object Values:",
                      "Mass:",
                      "Velocity:",
                      "X:",
                      "Y:",
                      "Central object:", 
                      "RGB Golor:"] 
        self.dragStart = None

    def Draw(self, screen, obj):
        # Drawing with permanently set pos
        height = screen.get_height()
        pos = PG.Vector2(15, height-240)

        self.obj = obj # Save the object

        if (self.inputs == []): # First draw -> load inputs (reloads on each object)
            self.SetupInput(pos + self.itemPos, self.obj)

        # Draw colored rectangle as bg
        rect = PG.Rect(pos.x, pos.y, 250,225)
        PG.draw.rect(screen, PG.Color(40,40,40), rect, border_radius=10, 
                                                       border_top_right_radius=50)

        # Original draw method (takes care of drawing all the inputs, texts)
        super().Draw(screen, pos) 

    def SetupInput(self, pos, obj):
        x = pos.x
        y = pos.y
 
        # InputField class - (xPos, yPos, width, height, default, xPadding, pointer, minValue (-1=None), maxValue (-1=None), decimal places)
        self.inputs = [InputField(x+120, y+25,80,22,             str(obj.mass),5,obj.pointers.mass,  1, -1,0),
                       InputField(x+120, y+75,80,22,str(obj.simSteps[0].vel.x),5,obj.pointers.xvel, -1, -1,2),
                       InputField(x+120,y+100,80,22,str(obj.simSteps[0].vel.y),5,obj.pointers.yvel, -1, -1,2),
                       InputField(x,    y+175,45,22,         str(obj.color[0]),5,obj.pointers.r,     0,255,0),
                       InputField(x+50, y+175,45,22,         str(obj.color[1]),5,obj.pointers.g,     0,255,0),
                       InputField(x+100,y+175,45,22,         str(obj.color[2]),5,obj.pointers.b,     0,255,0)]

        # RadioButton class - (xPos, yPos, size, default)
        self.radioButtons = [RadioButton(x+178,y+125,22,self.obj.static)]

    def Event_handler(self, event, objectList):
        # Handler for all defined events

        # RadioButton event
        for rb in self.radioButtons:
            out = rb.Event_handler(event)
            if (out == 1):
                for obj in objectList:
                    obj.SetStatic(False)

                self.obj.SetStatic(True)
            elif (out == 0):
                self.obj.SetStatic(False)

        # InputField events
        for inp in self.inputs:
            # Input background color changes - drag/hover
            if (self.dragStart == None and inp.field.collidepoint(PG.mouse.get_pos())) or (inp.drag):
                inp.bgcolor = inp.HOVER_COLOR
            else:
                inp.bgcolor = inp.BG_COLOR
            
            if (event.type == PG.MOUSEBUTTONUP): # Selecting input (on click up)
                # Deselect all + select field if under cursor
                self.dragStart = None
                inp.selected = False
                inp.drag = False

                if (inp.field.collidepoint(event.pos)):
                    inp.selected = True
                    inp.cursor = 0
            
            # Continuous mouse press = Drag behaviour
            if(PG.mouse.get_pressed()[0]): 
                # Deselect all (but not self while dragging)
                for other in self.inputs:
                    if not (other.drag):
                        other.selected = False
                    
                # Check if mouse is already in drag mode
                dragging = False
                for _inp in self.inputs:
                    if (_inp.drag):
                        dragging = True
                        break

                mousePos = PG.Vector2(PG.mouse.get_pos())

                # If first frame of drag - get window drag start
                if (self.dragStart == None): self.dragStart = mousePos

                # Start drag on input field under held cursor
                if not (dragging):
                    if (inp.field.collidepoint(self.dragStart)):
                        inp.SetText(inp.text)
                        inp.drag = True
                        inp.selected = True
                        inp.dragOrigPos = self.dragStart
                        inp.dragOrigValue = float(inp.text)

                # Get/Update drag value - x distance from start drag pos
                elif (inp.drag):
                    if (inp.pointer == self.obj.pointers.mass):
                        value = inp.GetDragValue(mousePos, 1/10)
                    elif (inp.pointer == self.obj.pointers.r or inp.pointer == self.obj.pointers.g or inp.pointer == self.obj.pointers.b):
                        value = inp.GetDragValue(mousePos, 5)
                    elif (inp.pointer == self.obj.pointers.xvel or inp.pointer == self.obj.pointers.yvel):
                        value = inp.GetDragValue(mousePos, 50)

                    # Input field text update
                    inp.SetText(value)

                    # Value update
                    r = self.obj.color[0]
                    g = self.obj.color[1]
                    b = self.obj.color[2]
                    if (inp.pointer == self.obj.pointers.mass):   self.obj.SetMass(float(inp.text))
                    elif (inp.pointer == self.obj.pointers.xvel): self.obj.SetStartVel((float(inp.text), None))
                    elif (inp.pointer == self.obj.pointers.yvel): self.obj.SetStartVel((None, float(inp.text)))
                    elif (inp.pointer == self.obj.pointers.r):    r = int(inp.text)
                    elif (inp.pointer == self.obj.pointers.g):    g = int(inp.text)
                    elif (inp.pointer == self.obj.pointers.b):    b = int(inp.text)
                    self.obj.SetColor(PG.Color(r,g,b))

                    return

            # Keyboard events for selected input
            if (inp.selected): 
                if event.type == PG.KEYDOWN:
                    # RETURN mean that some events need main for careful
                    # handling = "stuff this class cannot work with" 
                    # (e.g. arrows collide with object movement)

                    # BACKSPACE, DELETE, ENTER (apply input and deselect)
                    if (event.key == PG.K_BACKSPACE): 
                        text = inp.text[:len(inp.text)-inp.cursor-1] + inp.text[len(inp.text)-inp.cursor:]
                        inp.text = text
                    elif (event.key == PG.K_DELETE):
                        text = inp.text[:len(inp.text)-inp.cursor] + inp.text[len(inp.text)-inp.cursor+1:]
                        if (text != inp.text): inp.cursor -= 1
                        inp.text = text
                        return "delete" 
                    elif (event.key == PG.K_RETURN): 
                        inp.selected = False
                        if (inp.text == "" or inp.text == "-"): inp.SetText(0)
                        else: inp.SetText(inp.text)

                    # ARROW KEYS - moving cursor around
                    elif (event.key == PG.K_LEFT):
                        inp.cursor += 1
                        if (inp.cursor > len(inp.text)): inp.cursor = len(inp.text) 
                        return "arrows"
                    elif (event.key == PG.K_RIGHT):
                        inp.cursor -= 1
                        if (inp.cursor < 0): inp.cursor = 0
                        return "arrows"
                    elif (event.key == PG.K_UP or event.key == PG.K_DOWN):
                        return "arrows" 

                    # TAB - changing selected
                    elif (event.key == PG.K_TAB):
                        idx = self.inputs.index(inp) 
                        inp.selected = False
                        inp.SetText(inp.text)

                        # SHIFT+TAB/TAB
                        if (PG.key.get_mods() & PG.KMOD_SHIFT): idx -= 1
                        else: idx += 1

                        # LOOP AROUND
                        try:
                            self.inputs[idx].selected = True
                        except IndexError:
                            idx = 0
                            self.inputs[idx].selected = True

                        self.inputs[idx].cursor = 0
                        break
                            
                    # Pygame's handling of some keys is weird => fix so they can
                    # be just plain strings
                    key = PG.key.name(event.key)[0] 
                    if not key == "[": pass
                    else: key = PG.key.name(event.key)[1]

                    # ALLOWED KEYS
                    if (str(key) in "0123456789-."):
                        # MINUS
                        if (key == "-"):
                            text = "-"+inp.text
                            if (len(text) > 1 and text[0] == text[1] == "-"): text = text[2:]

                            inp.SetText(text)

                        # DOT
                        elif (key == "."):
                            if (len(inp.text) == 0): text = "0."
                            elif (len(inp.text) == 1 and inp.text[0] == '-'): text = "-0."
                            elif ("." in inp.text): text = inp.text
                            else: text = inp.text + "."
                                
                            inp.text = text
                                
                        # NUMBERS
                        else:
                            if (len(inp.text) < 5): # Soft text len block (possible to go over with drag)
                                inp.text = inp.text[:len(inp.text)-inp.cursor] + str(key) + inp.text[len(inp.text)-inp.cursor:]


                    # Final text -> Variable change + value checks 
                    safeValue = None
                    if (inp.text == "" or inp.text == "-"):
                        if (inp.pointer == self.obj.pointers.mass): safeValue = 1
                        else: safeValue = 0

                    if (inp.pointer == self.obj.pointers.mass): 
                        if (safeValue == None): self.obj.SetMass(float(inp.text))
                        else: self.obj.SetMass(safeValue)
                    if (inp.pointer == self.obj.pointers.xvel): 
                        if (safeValue == None): self.obj.SetStartVel((float(inp.text), None))
                        else: self.obj.SetStartVel((float(safeValue), None))
                    if (inp.pointer == self.obj.pointers.yvel): 
                        if (safeValue == None): self.obj.SetStartVel((None, float(inp.text)))
                        else: self.obj.SetStartVel((None, float(safeValue)))

                    r = self.obj.color[0]
                    g = self.obj.color[1]
                    b = self.obj.color[2]
                    if (inp.pointer == self.obj.pointers.r): 
                        if (safeValue == None): inp.SetText(float(inp.text))
                        else: inp.SetText(safeValue)
                        r = int(inp.text)
                    if (inp.pointer == self.obj.pointers.g):
                        if (safeValue == None): inp.SetText(float(inp.text))
                        else: inp.SetText(safeValue)
                        g = int(inp.text)
                    if (inp.pointer == self.obj.pointers.b):
                        if (safeValue == None): inp.SetText(float(inp.text))
                        else: inp.SetText(safeValue)
                        b = int(inp.text)
                    
                    self.obj.SetColor(PG.Color(r,g,b))

class InputField: 
    def __init__(self, x, y, width, height, text, xPadding, pointer, minValue, maxValue, decimal):
        self.field = PG.Rect(x,y,width,height)                 # text field rectangle
        self.text = text                                       # text string
        self.cursor = 0                                        # cursor position
        self.FONT = PG.font.SysFont('Arial', 20, False, False) # default font
        self.xPadding = xPadding                               # text padding from the start of the line
        self.pointer = pointer                                 # pointer to object variable

        # UI variables
        self.selected = False                                  # if selected
        self.drag = False                                      # if in drag mode
        self.dragOrigPos = None                                # starting drag position
        self.dragOrigValue = None                              # starting drag value

        # COLOR variables
        self.SELECTED_COLOR = PG.Color("white")
        self.DESELECTED_COLOR = PG.Color("gray")
        self.BG_COLOR = PG.Color(90,90,90)
        self.HOVER_COLOR = PG.Color(120,120,120)

        self.color = self.DESELECTED_COLOR                     # color = fg color = text color
        self.bgcolor = self.BG_COLOR                           # bgcolor = color of the text rectangle

        # INPUT variables
        self.minValue = minValue                               # min possible value (-1 = no limit)
        self.maxValue = maxValue                               # max 
        self.decimal = str(decimal)                            # number of decimal places
        
    def Draw(self, screen):
        # Set fgcolor
        self.color = self.SELECTED_COLOR if self.selected else self.DESELECTED_COLOR

        # If cursor has to be drawn
        drawText = None
        if (self.selected):
            drawText = self.text[:len(self.text)-self.cursor] +"|"+self.text[len(self.text)-self.cursor:]
        else:
            drawText = self.text

        # Printing text to text surface
        # (object for Pygame text drawing)
        textSurface = self.FONT.render(drawText, True, self.color)
            
        # Drawing input field rectangle and text
        PG.draw.rect(screen, self.bgcolor, self.field)
        screen.blit(textSurface, (self.field.x+self.xPadding,self.field.y))

    def SetText(self, text):
        # Setting text with possible constrains on values

        if (text == ''): value = 0 # failsafe
        elif (text == '-'): 
            self.text = "-" 
            return
        else: 
            value = float(text)
            
        # constrains
        if (self.minValue > value and self.minValue != -1):
            value = self.minValue
        if (self.maxValue < value and self.maxValue != -1):
            value = self.maxValue

        if (value == -0 or value == -0.0):
            value = 0
            

        self.text = ("{:0."+self.decimal+"f}").format(value)

    def GetDragValue(self, mousePos, sensitivity):
        # Calculate value from drag change
        return (self.dragOrigValue + ((mousePos - self.dragOrigPos).x)/sensitivity)

class RadioButton:
    def __init__(self, x, y, size, is_checked):
        self.rect = PG.Rect(x,y,size,size)                     # button rectangle
        self.FONT = PG.font.SysFont('Arial', 20, False, False) # default font

        # COLOR variables
        self.BG_COLOR = PG.Color(90,90,90) 
        self.HOVER_COLOR = PG.Color(120,120,120)

        self.bgcolor = self.BG_COLOR

        # UI variables
        self.text = " "                                        # text " "/"X" button
        self.is_checked = is_checked                           # if it should be checked from the start

    def Draw(self, screen):
        self.text = "X" if self.is_checked else " " 

        # Printing text to text surface
        # (object for Pygame text drawing)
        textSurface = self.FONT.render(self.text, True, PG.Color("white"))
            
        # Drawing input field rectangle and text
        PG.draw.rect(screen, self.bgcolor, self.rect)
        screen.blit(textSurface, self.rect.topleft+PG.Vector2(4,2))

    def Event_handler(self, event): 
        # Own event handler - compact enough

        # Colors
        if (self.rect.collidepoint(PG.mouse.get_pos())): self.bgcolor = self.HOVER_COLOR
        else: self.bgcolor = self.BG_COLOR
            
        # Toggle
        if (event.type == PG.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)):
            self.is_checked = not self.is_checked
            if (self.is_checked): return 1
            else: return 0

class TopMenu(UI):
    def __init__(self):
        super().__init__()
        # UI variables
        self.itemPos = PG.Vector2(17,5)
        self.items = []                        # For TopMenu only 1 item = tab text

        self.rect = None                       # Tab rectangle (set in draw)
        self.pos = None

        self.rectWidth = 75
        self.rectHeight = 25
        self.borderRect = PG.Rect(0,0,400,200) # Set boundaries for tabs - if cursor leaves, tab closes

        # list of MenuItem objects
        self.inItems = []                      # Need new variable for items under the tab

        self.SELECTED = False                  # If this tab is currently in use

        # COLOR variables
        self.NORMAL_COLOR = PG.Color(40,40,40)
        self.HOVER_COLOR = PG.Color(50,50,50)

        self.color = self.NORMAL_COLOR

    def Setup(self, num, topbar):
        # num - number, needed for padding from other tabs
        offset = 15
        for i in range(num): offset += topbar[i].rectWidth + 15
        self.pos = PG.Vector2(offset, 0)
        self.rect = PG.Rect(self.pos.x, self.pos.y, self.rectWidth, self.rectHeight)

    def Draw(self, screen):
        # Drawing own rect
        self.rect = PG.Rect(self.pos.x, self.pos.y, self.rectWidth, self.rectHeight)
        PG.draw.rect(screen, self.color, self.rect, border_bottom_right_radius=5, border_bottom_left_radius=5)

        # Tab text drawn in original UI draw
        super().Draw(screen, self.pos)

        # If opened, draw all the other items as well
        if (self.SELECTED):
            for index, item in enumerate(self.inItems): 
                item.Draw(screen, self.pos, index)

    def Event_handler(self, event, others):
        # Own event handler for tabs

        # Colors (hover)
        if (self.rect.collidepoint(PG.mouse.get_pos())): 
            self.color = self.HOVER_COLOR
            self.rectHeight = 30
        else: 
            self.color = self.NORMAL_COLOR
            self.rectHeight = 25

        # Close tabs if mouse leaves tab space 
        if not (self.borderRect.collidepoint(PG.mouse.get_pos())):
            self.SELECTED = False
            return
            
        # Pass events to inner items if opened
        if (self.SELECTED):
            for item in self.inItems:
                out = item.Event_handler(event)
                if not (out == None): return out
                
        else: 
            # If not opened - check for tab clicks
            if (event.type == PG.MOUSEBUTTONDOWN):
                if (self.rect.collidepoint(event.pos)):
                    self.SELECTED = True

                    for other in others:
                        if (other == self): continue
                        other.SELECTED = False

                    if (self.items[0] == "About"): return "about"

class MenuItem(UI):
    def __init__(self, text, width, pointer=None, shortcut="", scPos=PG.Vector2()):
        super().__init__()
        # Class for entries inside topbar tabs

        # UI variables
        self.itemPos = PG.Vector2(15,5)
        self.items = [text]                    # items = main text 

        self.rect = None                       # Entry rectangle
        self.shortcut = shortcut               # Shortcut text
        self.scPos = PG.Vector2(scPos)         # Shortcut line offset
        self.width = width                     # Entry width
        self.pointer = pointer                 # Object/function pointer (for event handling)

        # COLOR variables
        self.NORMAL_COLOR = PG.Color(40,40,40) 
        self.HOVER_COLOR = PG.Color(50,50,50)

        self.color = self.NORMAL_COLOR

        # Default font
        self.FONT = PG.font.SysFont('Arial', 20, False, False)

    def Draw(self, screen, pos, index):
        pos = PG.Vector2(pos) # for readability 
        pos = PG.Vector2(pos.x, 30+pos.y + 30*index)

        # Rectangle drawing
        self.rect = PG.Rect(pos.x, pos.y, self.width, 28)
        PG.draw.rect(screen, self.color, self.rect)

        # Possible shortcut drawing
        if not (self.shortcut == ""):
            textSurface = self.FONT.render(self.shortcut, True, PG.Color("gray"))
            screen.blit(textSurface, (pos.x+self.scPos.x, 
                                      pos.y+self.scPos.y))

        super().Draw(screen, pos)

    def Event_handler(self, event):
        # Own event handler
        # Colors
        if not (self.pointer == None):
            if (self.rect.collidepoint(PG.mouse.get_pos())): self.color = self.HOVER_COLOR
            else: self.color = self.NORMAL_COLOR
            
        # Mouse clicks -> sends back pointer to function (has to be done in main)
        if (event.type == PG.MOUSEBUTTONDOWN):
            if (self.rect.collidepoint(event.pos)):
                return self.pointer
