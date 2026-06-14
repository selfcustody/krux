"""Benchmark for QR scanning performance.
Run on device: exec(open('benchmark_qr.py').read())
"""
import time
import sensor
from krux.camera import QR_SCAN_MODE, ANTI_GLARE_MODE, ZOOMED_MODE, BINARY_GRID_MODE
from krux.settings import THIN_SPACE

FRAME_COUNT = 30


def benchmark_find_qrcodes():
    """Benchmark find_qrcodes() per frame"""
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.run(1)
    time.sleep_ms(500)  # Let camera warm up

    times = []
    for i in range(FRAME_COUNT):
        img = sensor.snapshot()
        start = time.ticks_us()
        img.find_qrcodes()
        elapsed = time.ticks_diff(time.ticks_us(), start)
        times.append(elapsed)

    avg_us = sum(times) // len(times)
    max_us = max(times)
    min_us = min(times)
    fps = 1_000_000 // avg_us if avg_us > 0 else 0

    print("=== find_qrcodes() benchmark ===")
    print("  Frames: %d" % FRAME_COUNT)
    print("  Avg: %d us (%d ms)" % (avg_us, avg_us // 1000))
    print("  Min: %d us" % min_us)
    print("  Max: %d us" % max_us)
    print("  Max FPS: %d" % fps)
    print()
    return avg_us


def benchmark_frame_skip():
    """Benchmark with frame skip"""
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.run(1)
    time.sleep_ms(500)

    skip = 2
    times = []
    frame_counter = 0
    for i in range(FRAME_COUNT * skip):
        img = sensor.snapshot()
        frame_counter += 1
        if frame_counter % skip == 0:
            start = time.ticks_us()
            img.find_qrcodes()
            elapsed = time.ticks_diff(time.ticks_us(), start)
            times.append(elapsed)

    avg_us = sum(times) // len(times)
    fps = 1_000_000 // avg_us if avg_us > 0 else 0

    print("=== Frame skip (skip=%d) benchmark ===" % skip)
    print("  Scanned frames: %d / %d" % (len(times), FRAME_COUNT * skip))
    print("  Avg scan: %d us (%d ms)" % (avg_us, avg_us // 1000))
    print("  Max FPS: %d" % fps)
    print()
    return avg_us


def benchmark_grayscale_vs_rgb():
    """Compare RGB565 vs GRAYSCALE"""
    results = {}

    for pixfmt, name in [(sensor.RGB565, "RGB565"), (sensor.GRAYSCALE, "GRAYSCALE")]:
        sensor.reset()
        sensor.set_pixformat(pixfmt)
        sensor.set_framesize(sensor.QVGA)
        sensor.run(1)
        time.sleep_ms(500)

        # Benchmark snapshot + find_qrcodes
        times = []
        for i in range(FRAME_COUNT):
            start = time.ticks_us()
            img = sensor.snapshot()
            img.find_qrcodes()
            elapsed = time.ticks_diff(time.ticks_us(), start)
            times.append(elapsed)

        avg_us = sum(times) // len(times)
        results[name] = avg_us

        print("=== %s snapshot+find_qrcodes ===" % name)
        print("  Avg: %d us (%d ms)" % (avg_us, avg_us // 1000))
        print()

    if "RGB565" in results and "GRAYSCALE" in results:
        improvement = (results["RGB565"] - results["GRAYSCALE"]) * 100 // results["RGB565"]
        print("=== GRAYSCALE vs RGB565 ===")
        print("  RGB565:   %d us" % results["RGB565"])
        print("  GRAYSCALE: %d us" % results["GRAYSCALE"])
        print("  Improvement: %d%%" % improvement)
        print()


def benchmark_mode_switch():
    """Benchmark camera mode switching"""
    from krux.camera import Camera

    cam = Camera()
    modes = [QR_SCAN_MODE, ANTI_GLARE_MODE, ZOOMED_MODE, BINARY_GRID_MODE]

    print("=== Camera mode switch benchmark ===")
    for mode in modes:
        start = time.ticks_ms()
        cam.initialize_run(mode)
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        print("  Mode %d: %d ms" % (mode, elapsed))
    print()


def run_all():
    """Run all benchmarks"""
    print("Krux QR Benchmark")
    print("=" * 40)
    print()

    benchmark_find_qrcodes()
    benchmark_frame_skip()
    benchmark_grayscale_vs_rgb()
    benchmark_mode_switch()

    print("Done!")


run_all()
