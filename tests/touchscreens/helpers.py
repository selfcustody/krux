# Test helpers for touchscreen tests


def create_cst816_touch_data(points, event, x_coord, y_coord):
    """Helper to construct CST816 touch data bytes.

    Args:
        points: Number of touch points (0x00 or 0x01)
        event: Event type (e.g., EVENT_TOUCH_CONTACT)
        x_coord: X coordinate (0-4095)
        y_coord: Y coordinate (0-4095)

    Returns:
        list: 6-byte touch data array
    """
    x_high = (x_coord >> 8) & 0x0F
    x_low = x_coord & 0xFF
    y_high = (y_coord >> 8) & 0x0F
    y_low = y_coord & 0xFF

    return [
        0x00,  # gesture
        points,
        (event << 6) | x_high,
        x_low,
        y_high,
        y_low,
    ]


def create_ft6x36_touch_data(x_coord, y_coord):
    """Helper to construct FT6X36 touch data bytes.

    Args:
        x_coord: X coordinate (0-4095)
        y_coord: Y coordinate (0-4095)

    Returns:
        list: 4-byte touch data array [x_high, x_low, y_high, y_low]
    """
    x_high = (x_coord >> 8) & 0x0F
    x_low = x_coord & 0xFF
    y_high = (y_coord >> 8) & 0x0F
    y_low = y_coord & 0xFF

    return [x_high, x_low, y_high, y_low]
