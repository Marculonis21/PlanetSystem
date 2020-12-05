#!/usr/bin/env python3

import pygame as PG
import numpy as np

class World:
    def __init__(self, center, screen_dim):
        self.center = center
        self.base = [PG.Vector2(1,0),PG.Vector2(0,1)]
        self.WIDTH, self.HEIGHT = screen_dim[0], screen_dim[1]

    def screen2world(self, pos, offset):
        pos -= offset
        coords = pos - self.center
        coords = PG.Vector2(coords.x * self.base.x,coords.y * self.base.y)
        return coords

    def world2screen(self, pos, offset):
        pos += offset
        coords = pos + self.center
        coords = PG.Vector2(coords .x * self.base.x,coords .y * self.base.y)
        return coords

    def zoom(self, x):
        self.base.x += x
        self.base.y += x
