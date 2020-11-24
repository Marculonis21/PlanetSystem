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

    def draw(self, screen, position):
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

    def draw(self, screen, obj):
        pos = obj.startPosition
        self.obj = obj
        if (self.inputs == []):
            self.setupInput(pos+self.posOffset+self.itemPos, self.obj)

        super().draw(screen,pos)

        for inp in self.inputs:
            inp.draw(screen)

    def setupInput(self, pos, obj):
        x = pos.x
        y = pos.y

        self.inputs = [InputField(x+100,  y+25,80,23,str(obj.mass),5,"mass"),
                       InputField(x+100,  y+75,80,23,str(obj.startVelocity[0]),5,"xvel"),
                       InputField(x+100, y+100,80,23,str(obj.startVelocity[1]),5,"yvel"),
                       InputField(x,    y+150,45,23,str(obj.color[0]),5,"r"),
                       InputField(x+50, y+150,45,23,str(obj.color[1]),5,"g"),
                       InputField(x+100,y+150,45,23,str(obj.color[2]),5,"b")]

    def event_handler(self, event):
        for inp in self.inputs:
            if event.type == PG.MOUSEBUTTONDOWN:
                if inp.field.collidepoint(event.pos):
                    inp.selected = True
                    for other in self.inputs:
                        if not (other == inp):
                            other.selected = False

            if (inp.selected):
                if event.type == PG.KEYDOWN:
                    key = PG.key.name(event.key)[0] 
                    if not key == "[":
                        pass
                    else: key = PG.key.name(event.key)[1]

                    print(key)

                    if (str(key) in "123456789-."):
                        print("hoy")
                        if (key == "-" and inp.text == ""):
                            inp.text += key
                        else:
                            inp.text += key
                            print(key)

                    if (event.key == PG.K_BACKSPACE):
                        inp.text = inp.text[:-1]

                    if (event.key == PG.K_RETURN):
                        inp.selected = False
                        if (inp.text == ""):
                            if (inp.pointer == "mass"): inp.text = "1"
                            else: inp.text = "0"
                        else:
                            inp.text = str(int(inp.text))
                            
                    if (inp.pointer == "mass"): 
                        try: self.obj.mass = int(inp.text) 
                        except ValueError: self.obj.mass = 1
                    if (inp.pointer == "xvel"): 
                        try: self.obj.startVelocity[0] = float(inp.text) 
                        except ValueError: self.obj.startVelocity[0] = 0
                    if (inp.pointer == "yvel"): 
                        try: self.obj.startVelocity[1] = float(inp.text) 
                        except ValueError: self.obj.startVelocity[1] = 0

                    if (inp.pointer == "r"): 
                        try: self.obj.color[0] = int(inp.text)
                        except ValueError: self.obj.color[0] = 0
                    if (inp.pointer == "g"):
                        try: self.obj.color[1] = int(inp.text)
                        except ValueError: self.obj.color[1] = 0
                    if (inp.pointer == "b"):
                        try: self.obj.color[2] = int(inp.text)
                        except ValueError: self.obj.color[2] = 0


                        
                        

class InputField:
    def __init__(self, x,y,width,height,text="",xalign=0,pointer=""):
        self.field = PG.Rect(x,y,width,height)
        self.text = text
        self.FONT = PG.font.SysFont('Arial', 20, False, False)
        self.xalign = xalign
        self.pointer = pointer

        self.SELECTED_COLOR = PG.Color("white")
        self.DESELECTED_COLOR = PG.Color("gray")
        self.selected = False
        self.color = self.DESELECTED_COLOR

        self.textSurface = self.FONT.render(self.text, True, self.color)

    def draw(self, screen):
        self.color = self.SELECTED_COLOR if self.selected else self.DESELECTED_COLOR
            
        self.textSurface = self.FONT.render(self.text, True, self.color)
        PG.draw.rect(screen, PG.Color(90,90,90), self.field)
        screen.blit(self.textSurface, (self.field.x+self.xalign,self.field.y))
