#!/usr/bin/env python3

import pygame as PG

class UI:
    def __init__(self):
        self.image = None
        self.posOffset = PG.Vector2()

        self.items = []
        self.itemPos = None
        self.values = []
        self.inputs = []

        self.FONT = PG.font.SysFont('Arial', 20, False, False)

    def Draw(self, screen, position):
        pos = PG.Vector2(position) + self.posOffset

        if (self.image != None):
            screen.blit(self.image, pos)

        for index, t in enumerate(self.items):
            textSurface = self.FONT.render(t, True, PG.Color("white"))
            screen.blit(textSurface, (pos.x+self.itemPos.x, 
                                      pos.y+self.itemPos.y + 25*index))

class ObjPopup(UI):
    def __init__(self):
        super().__init__()
        self.itemPos = PG.Vector2(40, -200)
        self.obj = None

        self.items = ["Object Values:",
                      "Mass:",
                      "Velocity:",
                      "X:",
                      "Y:",
                      "RGB Golor:"]

    def Draw(self, screen, obj):
        height = screen.get_height()
        pos = (0, height)
        self.obj = obj

        if (self.inputs == []):
            self.SetupInput(pos + self.itemPos, self.obj)

        r = PG.Rect(15,height-215,250,200)
        PG.draw.rect(screen, PG.Color(40,40,40), r, border_radius=10,border_top_right_radius=50)

        super().Draw(screen,pos)

        for inp in self.inputs:
            inp.Draw(screen)

    def SetupInput(self, pos, obj):
        x = pos.x
        y = pos.y

        self.inputs = [InputField(x+100,  y+25,80,23,str(obj.mass),5,"mass",1,-1,0),
                       InputField(x+100,  y+75,80,23,str(obj.simSteps[0].vel.x),5,"xvel",-1,-1,1),
                       InputField(x+100, y+100,80,23,str(obj.simSteps[0].vel.y),5,"yvel",-1,-1,1),
                       InputField(x,    y+150,45,23,str(obj.color[0]),5,"r",0,255,0),
                       InputField(x+50, y+150,45,23,str(obj.color[1]),5,"g",0,255,0),
                       InputField(x+100,y+150,45,23,str(obj.color[2]),5,"b",0,255,0)]


    def Event_handler(self, event):
        for inp in self.inputs:
            if (event.type == PG.MOUSEBUTTONUP): # Selecting input - write
                inp.selected = False
                inp.drag = False

                if (inp.field.collidepoint(event.pos)):
                    inp.selected = True
                    inp.cursor = 0
                    for other in self.inputs:
                        if not (other == inp):
                            other.selected = False
                            other.SetText(other.text)


            if(PG.mouse.get_pressed()[0]): # Continuous mouse press - drag
                mousePos = PG.Vector2(PG.mouse.get_pos())
                if not (inp.drag):
                    if (inp.field.collidepoint(mousePos)):
                        inp.drag = True
                        inp.selected = False
                        inp.dragOrig = mousePos
                        inp.dragOrigValue = float(inp.text)
                else:
                    if (inp.pointer == "mass"):
                        value = (inp.dragOrigValue + ((mousePos - inp.dragOrig).x))
                    elif (inp.pointer == "r" or inp.pointer == "g" or inp.pointer == "b"):
                        value = (inp.dragOrigValue + ((mousePos - inp.dragOrig).x)/5)
                    elif (inp.pointer == "xvel" or inp.pointer == "yvel"):
                        value = (inp.dragOrigValue + ((mousePos - inp.dragOrig).x)/10)

                    inp.SetText(value)

                    r = self.obj.color[0]
                    g = self.obj.color[1]
                    b = self.obj.color[2]
                    if (inp.pointer == "mass"):   self.obj.SetMass(float(inp.text))
                    elif (inp.pointer == "xvel"): self.obj.simSteps[0].vel.x = float(inp.text)
                    elif (inp.pointer == "yvel"): self.obj.simSteps[0].vel.y = float(inp.text)
                    elif (inp.pointer == "r"):    r = int(inp.text)
                    elif (inp.pointer == "g"):    g = int(inp.text)
                    elif (inp.pointer == "b"):    b = int(inp.text)

                    self.obj.SetColor(PG.Color(r,g,b))

            if (inp.selected): # Handle events for selected input
                if event.type == PG.KEYDOWN:
                    # For easier use of pressed key 
                    key = PG.key.name(event.key)[0] 
                    if not key == "[":
                        pass
                    else: key = PG.key.name(event.key)[1]

                    # BACKSPACE, DELETE, ENTER (apply input and deselect)
                    if (event.key == PG.K_BACKSPACE): 
                        text = inp.text[:len(inp.text)-inp.cursor-1] + inp.text[len(inp.text)-inp.cursor:]
                        inp.text = text
                        # inp.SetText(text)
                    elif (event.key == PG.K_DELETE):
                        text = inp.text[:len(inp.text)-inp.cursor] + inp.text[len(inp.text)-inp.cursor+1:]
                        # inp.SetText(text)
                        inp.text = text
                        inp.cursor -= 1
                    elif (event.key == PG.K_RETURN): 
                        inp.selected = False
                        if (inp.text == ""):
                            inp.SetText(0)
                        else:
                            inp.SetText(inp.text)

                    # ARROW KEYS - moving cursor around
                    elif (event.key == PG.K_LEFT):
                        inp.cursor += 1
                        if (inp.cursor > len(inp.text)): inp.cursor = len(inp.text) 
                    elif (event.key == PG.K_RIGHT):
                        inp.cursor -= 1
                        if (inp.cursor < 0): inp.cursor = 0

                    # TAB - changing selected
                    elif (event.key == PG.K_TAB):
                        idx = self.inputs.index(inp) 
                        inp.selected = False
                        inp.SetText(inp.text)

                        if (PG.key.get_mods() & PG.KMOD_SHIFT):
                            idx -= 1
                        else:
                            idx += 1

                        try:
                            self.inputs[idx].selected = True
                        except IndexError:
                            idx = 0
                            self.inputs[idx].selected = True

                        self.inputs[idx].cursor = 0
                        break
                            
                    # ALLOWED KEYS
                    elif (str(key) in "0123456789-."):
                        if (key == "-"):
                            inp.SetText("-"+inp.text)
                            if (len(inp.text) > 1):
                                if (inp.text[0] == inp.text[1] == "-"):
                                    print("1")
                                    inp.SetText(inp.text[2:])
                                
                        else:
                            text = inp.text[:len(inp.text)-inp.cursor] + str(key) + inp.text[len(inp.text)-inp.cursor:]
                            inp.SetText(text)

                    # Final text2variable assign - value checks 
                    if (inp.text == ""):
                        inp.text = "0"
                        inp.SetText(inp.text)
                        
                    if (inp.pointer == "mass"): 
                        self.obj.SetMass(int(inp.text))
                    if (inp.pointer == "xvel"): 
                        self.obj.simSteps[0].vel.x = float(inp.text)
                    if (inp.pointer == "yvel"): 
                        self.obj.simSteps[0].vel.y = float(inp.text)

                    r = self.obj.color[0]
                    g = self.obj.color[1]
                    b = self.obj.color[2]
                    if (inp.pointer == "r"): 
                        r = int(inp.text)
                        inp.SetText(inp.text)
                    if (inp.pointer == "g"):
                        g = int(inp.text)
                        inp.SetText(inp.text)
                    if (inp.pointer == "b"):
                        g = int(inp.text)
                        inp.SetText(inp.text)
                    
                    self.obj.SetColor(PG.Color(r,g,b))


class InputField:
    def __init__(self, x,y,width,height,text="",xalign=0,pointer="",minValue=-1,maxValue=-1,decimal=0):
        self.field = PG.Rect(x,y,width,height)
        self.text = text
        self.fText = text
        self.cursor = 0 
        self.FONT = PG.font.SysFont('Arial', 20, False, False)
        self.xalign = xalign
        self.pointer = pointer

        self.SELECTED_COLOR = PG.Color("white")
        self.DESELECTED_COLOR = PG.Color("gray")
        self.selected = False
        self.drag = False
        self.dragOrig = None
        self.dragOrigValue = None
        self.color = self.DESELECTED_COLOR
        self.bgcolor = PG.Color(90,90,90)

        self.minValue = minValue
        self.maxValue = maxValue
        self.decimal = str(decimal)

        self.textSurface = self.FONT.render(self.text, True, self.color)

    def Draw(self, screen):
        self.color = self.SELECTED_COLOR if self.selected else self.DESELECTED_COLOR

        drawText = None
        if (self.selected):
            self.fText = self.text[:len(self.text)-self.cursor] +"|"+self.text[len(self.text)-self.cursor:]
            drawText = self.fText
        else:
            drawText = self.text

        self.textSurface = self.FONT.render(drawText, True, self.color)
            
        PG.draw.rect(screen, self.bgcolor, self.field)
        screen.blit(self.textSurface, (self.field.x+self.xalign,self.field.y))

    def SetText(self, text):
        if (text == ""):
            value = 0
            
        value = float(text)
        if (self.minValue > value and self.minValue != -1):
            value = self.minValue
        if (self.maxValue < value and self.maxValue != -1):
            value = self.maxValue

        self.text = ("{:0."+self.decimal+"f}").format(value)
