#!/usr/bin/env python3
import pygame as PG
import random

MASS2SIZE = 1/8

class Object:
    def __init__(self, startPosition, startVelocity, mass):
        self.startPosition = startPosition
        self.startVelocity = startVelocity
        self.mass = mass

        self.size = mass*(MASS2SIZE) + 10
        self.color = (random.randint(0,255),
                      random.randint(0,255),
                      random.randint(0,255))

        self.simSteps = [simVars(startPosition,startVelocity)]

    def GetStepPos(self, idx, translate = PG.Vector2()):
        pos = self.simSteps[idx].pos + translate
        return (int(pos.x),int(pos.y))

    def SetMass(self, mass):
        self.mass = mass
        self.size2D = mass*(MASS2SIZE)

    def SetColor(self, color):
        self.color = color

class simVars:
    def __init__(self, position=PG.Vector2(), velocity=PG.Vector2()):
        self.pos = PG.Vector2(position)
        self.vel = PG.Vector2(velocity)
        
