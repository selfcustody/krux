from . import create_ctx


def test_fill_flash(amigo, mocker):
    from krux.pages.fill_flash import (
        FillFlash,
        BLOCK_SIZE,
        IMAGE_BYTES_SIZE,
        TOTAL_BLOCKS,
    )
    from krux.input import BUTTON_ENTER
    from krux.firmware import FLASH_SIZE
    import flash

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Confirm fill flash
    ]
    IMAGE_BYTES = b"\x00" * IMAGE_BYTES_SIZE

    def mock_flash_read(address, size):
        # Simulate the second half of the flash is empty
        if address > FLASH_SIZE // 2:
            return b"\xff" * size
        else:
            return b"\x00" * size

    mocker.patch("flash.read", side_effect=mock_flash_read)
    mocker.spy(flash, "write")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    fill_flash = FillFlash(ctx)
    fill_flash.capture_image_with_sufficient_entropy = mocker.MagicMock(
        return_value=IMAGE_BYTES
    )
    fill_flash.fill_flash_with_camera_entropy()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    # Check that the flash was written to on half of the blocks
    assert flash.write.call_count == TOTAL_BLOCKS // 2 - 1


def test_capture_image_with_sufficient_entropy(amigo, mocker):
    from krux.pages.fill_flash import FillFlash
    from krux.pages.capture_entropy import CameraEntropy, POOR_VARIANCE_TH

    # Mocks 3 poor entropy measurements then 1 good entropy measurement
    STDEV_INDEX = [*([POOR_VARIANCE_TH - 1] * 3), POOR_VARIANCE_TH + 1]

    ctx = create_ctx(mocker, [])
    fill_flash = FillFlash(ctx)
    entropy_measurement = CameraEntropy(ctx)
    mocker.spy(entropy_measurement, "entropy_measurement_update")
    entropy_measurement.rms_value = mocker.PropertyMock(side_effect=STDEV_INDEX)
    fill_flash.capture_image_with_sufficient_entropy(entropy_measurement)

    # Check that the entropy_measurement_update was called 4 times
    # 3 times for poor entropy and 1 time for good entropy
    assert entropy_measurement.entropy_measurement_update.call_count == 4
