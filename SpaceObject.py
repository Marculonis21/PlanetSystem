#!/usr/bin/env python3
import copy
import numpy as np
import pygame as PG
import random

MASS2SIZE = 1/3
class Object:
    def __init__(self, startPosition, startVelocity, mass, _list, zoom):
        self.sPos = PG.Vector2(startPosition)
        self.sVel = PG.Vector2(startVelocity)
        self.mass = mass

        self.size = mass**(MASS2SIZE) + 10

        # Default color is random (can be changed)
        self.color = PG.Color(random.randint(0,255),
                              random.randint(0,255),
                              random.randint(0,255))

        self.static = False

        self.simSteps = []
        self.ResetSteps()

    def ResetSteps(self):
        # Set to default values (startPosition, startVelocity)
        self.simSteps = [simVars(self.sPos, self.sVel)]
        self.simUpdate = True

    def ChangeCoordinates(self, b1, b2, TIMESTEP, paused, forwardSteps): 
        # Used for zoom function
        # Linear Algebra for the win - change coordinates with respect basis
        self.sPos = self.__changeCoords__(b1, b2, self.sPos)
        self.simSteps[0] = simVars(self.sPos, self.sVel)

        if (paused and TIMESTEP == 0): self.ResetSteps()

        # For zooming while sim is running - change coorinates on last N steps
        s = max(0, len(self.simSteps) - forwardSteps//4)
        for step in range(s, len(self.simSteps)):
            _pos = self.simSteps[step].pos

            nPos = self.__changeCoords__(b1,b2, _pos)
            self.simSteps[step].pos = nPos

    def __changeCoords__(self, b1, b2, pos):
        u = (pos.x * PG.Vector2(b1,0) + 
             pos.y * PG.Vector2(0,b1))

        a = np.array([[b2,0],
                      [0,b2]])

        b = np.array(u)
        x = np.linalg.solve(a, b)

        pos = PG.Vector2(x[0],x[1])
        return pos

    def SetStartVel(self, vel=(None, None)):
        if (vel[0] != None): self.sVel.x = vel[0]
        if (vel[1] != None): self.sVel.y = vel[1]

        if not (vel[0] == vel[1] == None):
            self.ResetSteps()
            self.simUpdate = True

    def ChangeStartPos(self, move, movespeed):
        if (move[0]): self.sPos += PG.Vector2(0, -movespeed)
        if (move[1]): self.sPos += PG.Vector2(0, +movespeed)
        if (move[2]): self.sPos += PG.Vector2(-movespeed, 0)
        if (move[3]): self.sPos += PG.Vector2(+movespeed, 0)
            
        if (move[0] or move[1] or move[2] or move[3]):
            self.ResetSteps()

    def SetMass(self, mass):
        if (mass <= 0): mass = 1
            
        self.mass = mass
        self.size = mass**(MASS2SIZE) + 10
        self.simUpdate = True

    def SetStatic(self, static):
        self.static = static
        self.simUpdate = True

    def SetColor(self, color):
        self.color = PG.Color(color[0],color[1],color[2])

    def GetStepPos(self, idx, translate):
        pos = self.simSteps[idx].pos + translate
        return (int(pos.x),int(pos.y)) # Pygame needs ints (pixels)

    def DrawSimPath(self, screen, offset, zoom, forwardSteps, paused, TIMESTEP, others):
        # For drawing future and past sim steps
        # s = start index -> 0 or N steps from the end
        if (paused and TIMESTEP == 0): s = 0 
        else: s = max(0, len(self.simSteps) - forwardSteps//4)
                
        # Check steps from s to end (not all -> saves time + makes nice
        # graphics - dotted line) and draw points on their positions
        for step in range(s, len(self.simSteps), forwardSteps//100):
            p = self.simSteps[step].pos+offset
            PG.draw.circle(screen, self.color, p, 1)

        # Check if last step didn't collide (if collision occures, it has to be
        # on last step) 
        colPos = self.Collides(len(self.simSteps)-1, others, zoom)

        if (colPos != None):
            PG.draw.circle(screen, PG.Color("red"), colPos+offset, self.size/zoom)

    def Contains(self, pos, zoom):
        # Constains function for mouse inputs
        if ((self.sPos - pos).magnitude() <= self.size/zoom): return True

    def Collides(self, TIMESTEP, others, zoom):
        # Collides for collision checks
        _pos = PG.Vector2(self.GetStepPos(TIMESTEP,PG.Vector2()))

        for obj in others:
            if (obj == self): continue
            
            _otherPos = PG.Vector2(obj.GetStepPos(TIMESTEP, PG.Vector2()))
            if ((_otherPos - _pos).magnitude() < (self.size/zoom) + (obj.size/zoom)):
                return _pos

# Class for easier storing of physics step data
class simVars:
    def __init__(self, position=PG.Vector2(), velocity=PG.Vector2()):
        self.pos = PG.Vector2(position)
        self.vel = PG.Vector2(velocity)
