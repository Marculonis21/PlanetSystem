#!/usr/bin/env python3
import pygame as PG
import random
import copy

MASS2SIZE = 1/3

class Object:
    def __init__(self, startPosition, startVelocity, mass, _list, zoom):
        if (len(_list) > 0):
            self.sPos = PG.Vector2(startPosition)
            posChange = _list[0].sPos - self.sPos
            self.origPos = copy.copy(_list[0].origPos - posChange*(1/zoom))
            print("l")
        else:
            self.origPos = PG.Vector2(startPosition)
            self.sPos = copy.copy(self.origPos)

        self.sVel = startVelocity

        self.mass = mass

        self.size = mass**(MASS2SIZE) + 20
        self.color = PG.Color(random.randint(0,255),
                              random.randint(0,255),
                              random.randint(0,255))

        self.simSteps = [simVars(self.sPos, self.sVel)]
        self.static = False

    def ResetSteps(self):    
        self.simSteps = [simVars(self.sPos, self.simSteps[0].vel)]

    def SetMass(self, mass):
        oldmass = self.mass

        self.mass = mass
        self.size = mass**(MASS2SIZE) + 20

    def SetColor(self, color):
        self.color = PG.Color(color[0],color[1],color[2])

    def GetStepPos(self, idx, translate):
        pos = self.simSteps[idx].pos + translate 
        return (int(pos.x),int(pos.y))

    def DrawSimPath(self, screen, offset, static, w):
        for step in range(1, len(self.simSteps)):
            # if not (static == None):
            #     p1 = (self.simSteps[step].pos+offset-static.simSteps[step].pos)+static.simSteps[0].pos
            #     p2 = (self.simSteps[step-1].pos+offset-static.simSteps[step-1].pos)+static.simSteps[0].pos
            # else:
            p1 = self.simSteps[step].pos+offset
            p2 = self.simSteps[step-1].pos+offset

            PG.draw.line(screen, self.color, p1, p2, 2)

    def Contains(self, pos, camZOOM):
        if ((self.sPos - pos).magnitude() <= self.size*camZOOM): return True

class simVars:
    def __init__(self, position=PG.Vector2(), velocity=PG.Vector2()):
        self.pos = PG.Vector2(position)
        self.vel = PG.Vector2(velocity)
        
