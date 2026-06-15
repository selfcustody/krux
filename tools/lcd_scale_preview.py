#!/usr/bin/env python3
"""Preview how LCD will look on Amigo.
Camera 320x240 at top of 320x480 screen, bottom half is black for info.
"""
import cv2
import numpy as np
import sys

CAMERA_W, CAMERA_H = 320, 240
SCREEN_W, SCREEN_H = 320, 480

def create_test_pattern():
    img = np.zeros((CAMERA_H, CAMERA_W, 3), dtype=np.uint8)
    for y in range(CAMERA_H):
        for x in range(CAMERA_W):
            r = (x * 255 // CAMERA_W)
            g = (y * 255 // CAMERA_H)
            b = 128
            img[y, x] = [b, g, r]
    cv2.putText(img, "Camera 320x240", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return img

def main():
    if len(sys.argv) > 1:
        src = cv2.imread(sys.argv[1])
        if src is None:
            print(f"Cannot read: {sys.argv[1]}")
            sys.exit(1)
        src = cv2.resize(src, (CAMERA_W, CAMERA_H))
    else:
        src = create_test_pattern()

    canvas = np.zeros((SCREEN_H, SCREEN_W, 3), dtype=np.uint8)
    canvas[:CAMERA_H, :CAMERA_W] = src

    cv2.putText(canvas, "320x480 screen", (60, SCREEN_H - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Info area", (100, SCREEN_H - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

    out_path = "/Users/test/krux/tools/lcd_scale_preview.png"
    cv2.imwrite(out_path, canvas)
    print(f"Saved to {out_path}")
    print(f"Screen: {SCREEN_W}x{SCREEN_H}")
    print(f"Camera: {CAMERA_W}x{CAMERA_H} at (0,0)")
    print(f"Info area: {SCREEN_W}x{SCREEN_H - CAMERA_H} at bottom")

if __name__ == "__main__":
    main()
