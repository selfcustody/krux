"""Test: log dimensions when display() is called with ROI"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest import mock
from kruxsim.mocks.board import BOARD_CONFIG
import importlib

# Load board config first
project_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'firmware', 'MaixPy', 'projects', 'maixpy_amigo', 'builtin_py')
spec = importlib.util.spec_from_file_location("board", os.path.join(project_dir, "board.py"))
board_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board_mod)
BOARD_CONFIG.update(board_mod.config)
sys.modules["board"] = mock.MagicMock(config=BOARD_CONFIG)

import pygame as pg
pg.init()
screen = pg.Surface((320, 480))

import cv2
import numpy as np

# Simulate what display() does with our fix
image_width, image_height = 240, 320
portrait = True

# Camera frame: 320x240 (what real camera gives)
frame = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
print(f"1. Camera frame: {frame.shape} (numpy: h={frame.shape[0]}, w={frame.shape[1]})")

# Aspect ratio crop (already correct for 320x240 camera)
# Resize to image_width x image_height  
frame = cv2.resize(frame, (image_width, image_height), interpolation=cv2.INTER_AREA)
print(f"2. After resize({image_width},{image_height}): {frame.shape} (numpy: h={frame.shape[0]}, w={frame.shape[1]})")

# swapaxes for pygame
frame = frame.swapaxes(0, 1)
print(f"3. After swapaxes: {frame.shape} (pygame: w={frame.shape[0]}, h={frame.shape[1]})")

# ROI = (0, 0, 320, 240)
roi = (0, 0, 320, 240)
x, y, w, h = roi
frame = frame[y:y+h, x:x+w]
print(f"4. After ROI crop [{y}:{y+h}, {x}:{x+w}]: {frame.shape} (pygame: w={frame.shape[0]}, h={frame.shape[1]})")

# My fix
frame = cv2.resize(frame.swapaxes(0, 1), (w, h), interpolation=cv2.INTER_LINEAR)
frame = frame.swapaxes(0, 1)
print(f"5. After resize to ROI: {frame.shape} (pygame: w={frame.shape[0]}, h={frame.shape[1]})")

surface = pg.surfarray.make_surface(frame)
print(f"6. Surface size: {surface.get_size()}")
print(f"7. Screen size: {screen.get_size()}")
print(f"8. Fills width: {surface.get_width() >= screen.get_width()}")
