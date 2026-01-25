import pytest
from . import create_ctx


BMP_DATA = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"


def test_hide_and_retrive_data_from_bmp(mocker, m5stickv):
    from unittest.mock import mock_open, patch
    from kapps.steganography import Kapp

    ctx = create_ctx(mocker, [])
    steg = Kapp(ctx)

    def _bits_generator(payload):
        for i in range(0, len(payload), 2):
            chunk = payload[i : i + 2]
            yield int.from_bytes(chunk, byteorder="big")

    written_data = []  # will hold the stego-BMP
    bit_gen = _bits_generator(BMP_DATA)
    width_holder = [10]  # mutable value ;)
    mocker.patch(
        "image.Image",
        return_value=mocker.MagicMock(
            width=lambda: width_holder[0],
            height=lambda: 10,
            get_pixel=lambda x, y, rgbtuple: next(bit_gen),
            set_pixel=lambda a, b, pixel: written_data.append(
                pixel.to_bytes(2, byteorder="big")
            ),
        ),
    )

    secret_to_hide = b"This is a secret"
    steg.hide_data(secret_to_hide, "in.bmp", "out.bmp")

    written_data = b"".join(written_data)
    steg_bmp = written_data + BMP_DATA[len(written_data) :]
    assert len(steg_bmp) <= len(BMP_DATA)

    bit_gen = _bits_generator(steg_bmp)
    retrieved = steg.extract_data("in.bmp")
    assert retrieved == secret_to_hide

    width_holder = [
        1
    ]  # change width to 1 will raise Exception "Not enough px to retrieve data"
    with pytest.raises(ValueError):
        steg.extract_data("in.bmp")

    width_holder = [10]
    secret_to_hide = b"This is a secret" * 3  # secret too big, don't fit the image
    with pytest.raises(ValueError):
        steg.hide_data(secret_to_hide, "in.bmp", "out.bmp")
