#!/usr/bin/env python3

import pygame as PG

class UI:
    def __init__(self):
        self.image = None

        self.items = []
        self.itemPos = PG.Vector2()
        self.inputs = []
        self.radioButtons = []

        self.FONT = PG.font.SysFont('Arial', 20, False, False)

    def Draw(self, screen, pos):
        pos = PG.Vector2(pos)

        if (self.image != None):
            screen.blit(self.image, pos)

        if not (pos == None):
            for index, t in enumerate(self.items):
                textSurface = self.FONT.render(t, True, PG.Color("white"))
                screen.blit(textSurface, (pos.x+self.itemPos.x, 
                                          pos.y+self.itemPos.y + 25*index))

        for inp in self.inputs:
            inp.Draw(screen)
        for rb in self.radioButtons:
            rb.Draw(screen)

class ObjPopup(UI):
    def __init__(self):
        super().__init__()
        self.itemPos = PG.Vector2(40, -225)
        self.obj = None
        self.dragStart = None

        self.items = ["Object Values:",
                      "Mass:",
                      "Velocity:",
                      "X:",
                      "Y:",
                      "Central object:",
                      "RGB Golor:"]

        self.radioButtons = []

    def Draw(self, screen, obj):
        height = screen.get_height()
        pos = (0, height)
        self.obj = obj

        if (self.inputs == []): # First draw -> load inputs
            self.SetupInput(pos + self.itemPos, self.obj)

        r = PG.Rect(15,height-240,250,225)
        PG.draw.rect(screen, PG.Color(40,40,40), r, border_radius=10,border_top_right_radius=50)

        super().Draw(screen, pos)

    def SetupInput(self, pos, obj):
        x = pos.x
        y = pos.y
 
        self.inputs = [InputField(x+120, y+25,80,22,             str(obj.mass),5,"mass", 1, -1,0),
                       InputField(x+120, y+75,80,22,str(obj.simSteps[0].vel.x),5,"xvel",-1, -1,1),
                       InputField(x+120,y+100,80,22,str(obj.simSteps[0].vel.y),5,"yvel",-1, -1,1),
                       InputField(x,    y+175,45,22,         str(obj.color[0]),5,   "r", 0,255,0),
                       InputField(x+50, y+175,45,22,         str(obj.color[1]),5,   "g", 0,255,0),
                       InputField(x+100,y+175,45,22,         str(obj.color[2]),5,   "b", 0,255,0)]

        self.radioButtons = [RadioButton(x+178,y+125,22,22,self.obj.static)]


    def Event_handler(self, event, objectList):
        for rb in self.radioButtons:
            # RadioButton events
            out = rb.Event_handler(event)
            if (out == 1):
                for obj in objectList:
                    obj.SetStatic(False)

                self.obj.SetStatic(True)
            elif (out == 0):
                self.obj.SetStatic(False)

        for inp in self.inputs:
            # Input background color changes - drag/hover
            if (self.dragStart == None and inp.field.collidepoint(PG.mouse.get_pos())) or (inp.drag):
                inp.bgcolor = inp.HOVER_COLOR
            else:
                inp.bgcolor = inp.BG_COLOR

            if (event.type == PG.MOUSEBUTTONUP): # Selecting input (on click up)
                # Deselect all + select field under cursor
                self.dragStart = None
                inp.selected = False
                inp.drag = False

                if (inp.field.collidepoint(event.pos)):
                    inp.selected = True
                    inp.cursor = 0

            if(PG.mouse.get_pressed()[0]): # Continuous mouse press - drag
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
                if (self.dragStart == None):
                    self.dragStart = mousePos

                # Start drag on input under held cursor
                if not (dragging):
                    if (inp.field.collidepoint(self.dragStart)):
                        inp.SetText(inp.text)
                        inp.drag = True
                        inp.selected = True
                        inp.dragOrigPos = self.dragStart
                        inp.dragOrigValue = float(inp.text)

                # Get/Update drag value - x distance from orig drag pos
                elif (inp.drag):
                    if (inp.pointer == "mass"):
                        value = inp.GetDragValue(mousePos, 1/10)
                    elif (inp.pointer == "r" or inp.pointer == "g" or inp.pointer == "b"):
                        value = inp.GetDragValue(mousePos, 5)
                    elif (inp.pointer == "xvel" or inp.pointer == "yvel"):
                        value = inp.GetDragValue(mousePos, 50)

                    inp.SetText(value)

                    # Value update
                    r = self.obj.color[0]
                    g = self.obj.color[1]
                    b = self.obj.color[2]
                    if (inp.pointer == "mass"):   self.obj.SetMass(float(inp.text))
                    elif (inp.pointer == "xvel"): self.obj.SetStartVel((float(inp.text), None))
                    elif (inp.pointer == "yvel"): self.obj.SetStartVel((None, float(inp.text)))
                    elif (inp.pointer == "r"):    r = int(inp.text)
                    elif (inp.pointer == "g"):    g = int(inp.text)
                    elif (inp.pointer == "b"):    b = int(inp.text)
                    self.obj.SetColor(PG.Color(r,g,b))

            if (inp.selected): # Handle events for selected input
                if event.type == PG.KEYDOWN:
                    key = PG.key.name(event.key)[0] 
                    if not key == "[": pass
                    else: key = PG.key.name(event.key)[1]

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
                            
                    # ALLOWED KEYS
                    elif (str(key) in "0123456789-."):
                        # MINUS
                        if (key == "-"):
                            text = "-"+inp.text
                            if (len(text) > 1 and text[0] == text[1] == "-"): text = text[2:]

                            inp.SetText(text)

                        # DOT
                        elif (key == "."):
                            if (len(inp.text) == 0): text = "0."
                            elif ("." in inp.text): text = inp.text
                            else: text = inp.text + "."
                                
                            inp.text = text
                                
                        # NUMBERS
                        else:
                            if (len(inp.text) < 5): # Soft text len block (possible to go over with drag)
                                inp.text = inp.text[:len(inp.text)-inp.cursor] + str(key) + inp.text[len(inp.text)-inp.cursor:]


                    # Final Text->Variable + value checks 
                    value = None
                    if (inp.text == "" or inp.text == "-"):
                        if (inp.pointer == "mass"): value = 1
                        else: value = 0

                    if (inp.pointer == "mass"): 
                        if (value == None): self.obj.SetMass(float(inp.text))
                        else: self.obj.SetMass(value)
                    if (inp.pointer == "xvel"): 
                        if (value == None): self.obj.SetStartVel((float(inp.text), None))
                        else: self.obj.SetStartVel((float(value), None))
                    if (inp.pointer == "yvel"): 
                        if (value == None): self.obj.SetStartVel((None, float(inp.text)))
                        else: self.obj.SetStartVel((None, float(value)))

                    r = self.obj.color[0]
                    g = self.obj.color[1]
                    b = self.obj.color[2]
                    if (inp.pointer == "r"): 
                        if (value == None): inp.SetText(float(inp.text))
                        else: inp.SetText(value)
                        r = int(inp.text)
                    if (inp.pointer == "g"):
                        if (value == None): inp.SetText(float(inp.text))
                        else: inp.SetText(value)
                        g = int(inp.text)
                    if (inp.pointer == "b"):
                        if (value == None): inp.SetText(float(inp.text))
                        else: inp.SetText(value)
                        b = int(inp.text)
                    
                    self.obj.SetColor(PG.Color(r,g,b))

class InputField: 
    def __init__(self, x,y,width,height,text="",xalign=0,pointer="",minValue=-1,maxValue=-1,decimal=0):
        self.field = PG.Rect(x,y,width,height)
        self.text = text
        self.cursor = 0 
        self.FONT = PG.font.SysFont('Arial', 20, False, False)
        self.xalign = xalign
        self.pointer = pointer

        self.selected = False
        self.drag = False
        self.dragOrigPos = None
        self.dragOrigValue = None

        self.SELECTED_COLOR = PG.Color("white")
        self.DESELECTED_COLOR = PG.Color("gray")
        self.BG_COLOR = PG.Color(90,90,90)
        self.HOVER_COLOR = PG.Color(120,120,120)

        self.color = self.DESELECTED_COLOR
        self.bgcolor = self.BG_COLOR

        self.minValue = minValue
        self.maxValue = maxValue
        self.decimal = str(decimal)

        self.textSurface = self.FONT.render(self.text, True, self.color)

    def Draw(self, screen):
        self.color = self.SELECTED_COLOR if self.selected else self.DESELECTED_COLOR

        drawText = None
        if (self.selected):
            drawText = self.text[:len(self.text)-self.cursor] +"|"+self.text[len(self.text)-self.cursor:]
        else:
            drawText = self.text

        self.textSurface = self.FONT.render(drawText, True, self.color)
            
        PG.draw.rect(screen, self.bgcolor, self.field)
        screen.blit(self.textSurface, (self.field.x+self.xalign,self.field.y))

    def SetText(self, text):
        if (text == ''):
            value = 0
            
        else: value = float(text)
            
        if (self.minValue > value and self.minValue != -1):
            value = self.minValue
        if (self.maxValue < value and self.maxValue != -1):
            value = self.maxValue

        self.text = ("{:0."+self.decimal+"f}").format(value)

    def GetDragValue(self, mousePos, scale):
        return (self.dragOrigValue + ((mousePos - self.dragOrigPos).x)/scale)

class RadioButton:
    def __init__(self, x, y, width, height, default=False):
        self.rect = PG.Rect(x,y,width,height)
        self.FONT = PG.font.SysFont('Arial', 20, False, False)

        self.BG_COLOR = PG.Color(90,90,90)
        self.HOVER_COLOR = PG.Color(120,120,120)

        self.bgcolor = self.BG_COLOR

        self.text = " "
        self.toggle = default

    def Draw(self, screen):
        if (self.toggle): self.text = "X"
        else: self.text = ""

        self.textSurface = self.FONT.render(self.text, True, PG.Color("white"))
            
        PG.draw.rect(screen, self.bgcolor, self.rect)
        screen.blit(self.textSurface, self.rect.topleft+PG.Vector2(4,2))

    def Event_handler(self, event): 
        if (self.rect.collidepoint(PG.mouse.get_pos())): self.bgcolor = self.HOVER_COLOR
        else: self.bgcolor = self.BG_COLOR
            
        if (event.type == PG.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)):
            self.toggle = not self.toggle
            if (self.toggle): return 1
            else: return 0

class TopMenu(UI):
    def __init__(self):
        super().__init__()
        self.itemPos = PG.Vector2(17,5)
        self.items = []
        self.inItems = [] 
        self.SELECTED = False
        self.rect = None
        self.rectHeight = 25
        self.borderRect = PG.Rect(0,0,300,200)

        self.NORMAL_COLOR = PG.Color(40,40,40)
        self.HOVER_COLOR = PG.Color(50,50,50)

        self.color = self.NORMAL_COLOR

    def Draw(self, screen, num):
        pos = (15+90*num, 0)

        self.rect = PG.Rect(15+90*num, 0, 75, self.rectHeight)
        PG.draw.rect(screen, self.color, self.rect, border_bottom_right_radius=5, border_bottom_left_radius=5)

        super().Draw(screen, pos)

        if (self.SELECTED):
            for index, item in enumerate(self.inItems): 
                item.Draw(screen, pos, index)

    def Event_hanlder(self, event, others):
        if (self.rect.collidepoint(PG.mouse.get_pos())): 
            self.color = self.HOVER_COLOR
            self.rectHeight = 30
        else: 
            self.color = self.NORMAL_COLOR
            self.rectHeight = 25

        if not (self.borderRect.collidepoint(PG.mouse.get_pos())):
            for other in others:
                if (other == self): continue
                other.SELECTED = False
            return
            
        if (self.SELECTED):
            for item in self.inItems:
                out = item.Event_hanlder(event)
                if not (out == None): return out
                
        else: 
            if (event.type == PG.MOUSEBUTTONDOWN):
                if (self.rect.collidepoint(event.pos)):
                    self.SELECTED = True

                    for other in others:
                        if (other == self): continue
                        other.SELECTED = False

                    if (self.items[0] == "About"): return "about"

class MenuItem(UI):
    def __init__(self, text, pointer, shortcut="", scPos=PG.Vector2(), width=120):
        super().__init__()
        self.itemPos = PG.Vector2(15,5)
        self.items = [text]
        self.shortcut = shortcut
        self.scPos = PG.Vector2(scPos)
        self.width = width
        self.pointer = pointer
        self.rect = None

        self.NORMAL_COLOR = PG.Color(40,40,40)
        self.HOVER_COLOR = PG.Color(50,50,50)

        self.color = self.NORMAL_COLOR

        self.FONT = PG.font.SysFont('Arial', 20, False, False)

    def Draw(self, screen, pos, index):
        pos = PG.Vector2(pos)
        pos = PG.Vector2(pos.x+0, pos.y+30+30*index)

        self.rect = PG.Rect(pos.x, pos.y, self.width, 28)
        PG.draw.rect(screen, self.color, self.rect)

        if not (self.shortcut == ""):
            textSurface = self.FONT.render(self.shortcut, True, PG.Color("gray"))
            screen.blit(textSurface, (pos.x+self.scPos.x, 
                                      pos.y+self.scPos.y))

        super().Draw(screen, pos)

    def Event_hanlder(self, event):
        if not (self.pointer == None):
            if (self.rect.collidepoint(PG.mouse.get_pos())): self.color = self.HOVER_COLOR
            else: self.color = self.NORMAL_COLOR
            
        if (event.type == PG.MOUSEBUTTONDOWN):
            if (self.rect.collidepoint(event.pos)):
                return self.pointer
