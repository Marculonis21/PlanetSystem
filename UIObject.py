#!/usr/bin/env python3

import pygame as PG

class UI:
    def __init__(self):
        self.image = None
        self.posOffset = None

        self.items = []
        self.itemPos = None
        self.values = []
        self.inputs = []

        self.FONT = PG.font.SysFont('Arial', 20, False, False)

    def Draw(self, screen, position):
        pos = PG.Vector2(position) + self.posOffset

        screen.blit(self.image, pos)

        for index, t in enumerate(self.items):
            textSurface = self.FONT.render(t, True, PG.Color("white"))
            screen.blit(textSurface, (pos.x+self.itemPos.x, 
                                      pos.y+self.itemPos.y + 25*index))

class ObjPopup(UI):
    def __init__(self):
        super().__init__()
        self.image = PG.image.load("Images/popup.png")
        self.image = PG.transform.scale(self.image, (260, 275))
        self.posOffset = PG.Vector2(-150,-275)

        self.itemPos = PG.Vector2(40,30)
        self.obj = None

        self.items = ["Object Values:",
                      "Mass:",
                      "Velocity:",
                      "X:",
                      "Y:",
                      "RGB Golor:"]

    def Draw(self, screen, obj, offset):
        pos = obj.startPosition + offset
        self.obj = obj
        if (self.inputs == []):
            self.SetupInput(pos+self.posOffset+self.itemPos, self.obj)

        super().Draw(screen,pos)

        for inp in self.inputs:
            inp.Draw(screen)

    def SetupInput(self, pos, obj):
        x = pos.x
        y = pos.y

        self.inputs = [InputField(x+100,  y+25,80,23,str(obj.mass),5,"mass"),
                       InputField(x+100,  y+75,80,23,str(obj.simSteps[0].vel.x),5,"xvel"),
                       InputField(x+100, y+100,80,23,str(obj.simSteps[0].vel.y),5,"yvel"),
                       InputField(x,    y+150,45,23,str(obj.color[0]),5,"r"),
                       InputField(x+50, y+150,45,23,str(obj.color[1]),5,"g"),
                       InputField(x+100,y+150,45,23,str(obj.color[2]),5,"b")]

    def Event_handler(self, event):
        for inp in self.inputs:
            if event.type == PG.MOUSEBUTTONDOWN:
                if inp.field.collidepoint(event.pos):
                    inp.selected = True
                    inp.cursor = 0
                    for other in self.inputs:
                        if not (other == inp):
                            other.selected = False

            if (inp.selected): # Handle events for selected input
                if event.type == PG.KEYDOWN:
                    # For easier use of pressed key 
                    key = PG.key.name(event.key)[0] 
                    if not key == "[":
                        pass
                    else: key = PG.key.name(event.key)[1]

                    # BACKSPACE, DELETE, ENTER (apply input and deselect)
                    if (event.key == PG.K_BACKSPACE): 
                        inp.text = inp.text[:len(inp.text)-inp.cursor-1] + inp.text[len(inp.text)-inp.cursor:]
                    elif (event.key == PG.K_DELETE):
                        inp.text = inp.text[:len(inp.text)-inp.cursor] + inp.text[len(inp.text)-inp.cursor+1:]
                        inp.cursor -= 1
                    elif (event.key == PG.K_RETURN): 
                        inp.selected = False
                        if (inp.text == ""):
                            if (inp.pointer == "mass"): inp.text = "1"
                            else: inp.text = "0"
                        else:
                            try: inp.text = str(int(inp.text))
                            except ValueError: inp.text = str(float(inp.text))

                    # ARROW KEYS - moving cursor around
                    elif (event.key == PG.K_LEFT):
                        inp.cursor += 1
                        if (inp.cursor > len(inp.text)): inp.cursor = len(inp.text) 
                    elif (event.key == PG.K_RIGHT):
                        inp.cursor -= 1
                        if (inp.cursor < 0): inp.cursor = 0

                    elif (event.key == PG.K_TAB):
                        idx = self.inputs.index(inp) 
                        inp.selected = False

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
                            inp.text = "-"+inp.text
                            if (len(inp.text) > 1):
                                if (inp.text[0] == inp.text[1] == "-"):
                                    print("1")
                                    inp.text = inp.text[2:]
                                
                        else:
                            inp.text = inp.text[:len(inp.text)-inp.cursor] + str(key) + inp.text[len(inp.text)-inp.cursor:]

                    # Final text2variable assign - value checks 
                    if (inp.pointer == "mass"): 
                        try: M = int(inp.text) 
                        except ValueError: M = 1
                        self.obj.SetMass(M)
                    if (inp.pointer == "xvel"): 
                        try: X = float(inp.text) 
                        except ValueError: X = 0
                        self.obj.simSteps[0].vel.x = X
                    if (inp.pointer == "yvel"): 
                        try: Y = float(inp.text) 
                        except ValueError: Y = 0
                        self.obj.simSteps[0].vel.y = Y

                    r = self.obj.color[0]
                    g = self.obj.color[1]
                    b = self.obj.color[2]
                    if (inp.pointer == "r"): 
                        try: int(inp.text)
                        except ValueError: inp.text = 0 
                        if (int(inp.text) > 255 or int(inp.text) < 0): pass
                        else: r = int(inp.text) 
                        inp.text = str(r)
                    if (inp.pointer == "g"):
                        try: int(inp.text)
                        except ValueError: inp.text = 0 
                        if (int(inp.text) > 255 or int(inp.text) < 0): pass
                        else: g = int(inp.text) 
                        inp.text = str(g)
                    if (inp.pointer == "b"):
                        try: int(inp.text)
                        except ValueError: inp.text = 0 
                        if (int(inp.text) > 255 or int(inp.text) < 0): pass
                        else: b = int(inp.text) 
                        inp.text = str(b)
                    
                    self.obj.SetColor(PG.Color(r,g,b))


class InputField:
    def __init__(self, x,y,width,height,text="",xalign=0,pointer=""):
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
        self.color = self.DESELECTED_COLOR
        self.bgcolor = PG.Color(90,90,90)

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
