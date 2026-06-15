#!/usr/bin/env python3
"""Trigger macOS camera permission dialog"""
import cv2
import sys

print("Opening camera to trigger macOS permission dialog...")
print("If a dialog appears, click 'Allow'")

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
print(f"Camera opened: {cap.isOpened()}")

if cap.isOpened():
    ret, frame = cap.read()
    print(f"Frame read: {ret}")
    if ret:
        print(f"Frame shape: {frame.shape}")
    cap.release()
    print("Camera works!")
else:
    print("Camera failed to open")
    sys.exit(1)
