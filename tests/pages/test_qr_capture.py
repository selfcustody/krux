from . import create_ctx
from ..test_qr import tdata

from ..shared_mocks import (
    snapshot_generator,
    SNAP_ANIMATED_QR,
    DONT_FIND_ANYTHING,
    SNAP_FIND_ANIMATED_SKIPPING,
    SNAP_REPEAT_QRCODE,
    TimeMocker,
    mock_context,
)


def test_capture_qr_code(mocker, multiple_devices, tdata):
    from krux.pages.qr_capture import QRCodeCapture
    from krux.qr import FORMAT_PMOFN, FORMAT_UR
    from ur.ur import UR
    from urtypes.crypto.psbt import PSBT
    from krux.wdt import wdt

    cases = [
        [
            # tdata.TEST_PARTS_FORMAT_PMOFN contains tdata.TEST_DATA_B58,
            # split in a 3 parts PMofN QR code
            tdata.TEST_PARTS_FORMAT_PMOFN,
            tdata.TEST_DATA_B58,
        ],
        [
            # UR QR code
            tdata.TEST_PARTS_FORMAT_MULTIPART_UR,
            tdata.TEST_DATA_BYTES,
        ],
    ]
    for case in cases:
        ctx = create_ctx(mocker, None)
        # Mocking the snapshot method to return an animated QR code
        mocker.patch.object(
            ctx.camera,
            "snapshot",
            new=snapshot_generator(
                outcome=SNAP_ANIMATED_QR,
                animated_qr=case[0],
            ),
        )
        spy_wdt = mocker.spy(wdt, "feed")
        spy_sensor_stop = mocker.spy(ctx.camera, "stop_sensor")
        qr_capturer = QRCodeCapture(ctx)

        qr_code, qr_format = qr_capturer.qr_capture_loop()
        if isinstance(qr_code, str):
            assert qr_code == case[1]
            assert qr_format == FORMAT_PMOFN
        elif isinstance(qr_code, UR):
            qr_data = PSBT.from_cbor(qr_code.cbor).data
            assert qr_data == case[1]
            assert qr_format == FORMAT_UR

        ctx.display.to_landscape.assert_has_calls(
            [mocker.call() for _ in range(len(case[0]))]
        )
        ctx.display.to_portrait.assert_has_calls(
            [mocker.call() for _ in range(len(case[0]))]
        )
        ctx.display.draw_centered_text.assert_has_calls(
            [mocker.call("Loading Camera..")]
        )
        spy_sensor_stop.assert_called()
        spy_wdt.assert_called()


def test_camera_antiglare(mocker, m5stickv):
    from krux.pages.qr_capture import QRCodeCapture
    from krux.camera import Camera, OV7740_ID, OV2640_ID, GC2145_ID

    antiglare_on = False

    def toggle_antiglare():
        nonlocal antiglare_on
        antiglare_on = not antiglare_on
        return antiglare_on

    time_mocker = TimeMocker(1001)
    ctx = mock_context(mocker)
    mocker.patch.object(
        ctx.camera,
        "snapshot",
        new=snapshot_generator(outcome=DONT_FIND_ANYTHING),
    )
    mocker.patch.object(
        ctx.camera,
        "toggle_antiglare",
        side_effect=toggle_antiglare,
    )
    cameras = [OV7740_ID, OV2640_ID, GC2145_ID]
    for cam_id in cameras:
        mocker.patch.object(ctx.camera.sensor, "get_id", lambda: cam_id)
        PAGE_SEQ = [False, True, False, True, False]
        PAGE_PREV_SEQ = [False, False, False, False, True]
        mocker.patch("time.ticks_ms", time_mocker.tick)
        ctx.input.page_event = mocker.MagicMock(side_effect=PAGE_SEQ)
        ctx.input.page_prev_event = mocker.MagicMock(side_effect=PAGE_PREV_SEQ)
        mocker.spy(ctx.camera, "toggle_antiglare")
        qr_capturer = QRCodeCapture(ctx)
        qr_code, qr_format = qr_capturer.qr_capture_loop()
        assert qr_code == None
        ctx.camera.toggle_antiglare.assert_has_calls([mocker.call()] * 2)
        ctx.light.turn_on.call_count == 0
        ctx.display.draw_centered_text.assert_has_calls(
            [mocker.call("Anti-glare enabled")]
        )
        ctx.display.draw_centered_text.assert_has_calls(
            [mocker.call("Anti-glare disabled")]
        )


def test_light_control(mocker, multiple_devices):
    from krux.pages.qr_capture import QRCodeCapture

    time_mocker = TimeMocker(1001)

    ctx = create_ctx(mocker, None)
    mocker.patch.object(
        ctx.camera,
        "snapshot",
        new=snapshot_generator(outcome=DONT_FIND_ANYTHING),
    )
    mocker.patch("time.ticks_ms", time_mocker.tick)
    # Light goes on when the enter button is pressed (and value becomes 0-False)
    ENTER_SEQ = [
        True,
        False,
        True,
        True,
        True,
    ]
    ctx.input.enter_value = mocker.MagicMock(side_effect=ENTER_SEQ)
    # Leaves the loop at 5th iteration
    PAGE_PREV_SEQ = [False, False, False, False, True]
    ctx.input.page_prev_event = mocker.MagicMock(side_effect=PAGE_PREV_SEQ)
    qr_capturer = QRCodeCapture(ctx)
    qr_code, qr_format = qr_capturer.qr_capture_loop()
    assert qr_code == None
    if ctx.light:
        ctx.light.turn_on.assert_called_once()
        ctx.light.turn_off.assert_called()


def test_capture_qr_code_loop_returns_early_when_requested(mocker, m5stickv, tdata):
    from krux.pages.qr_capture import QRCodeCapture
    from krux.qr import FORMAT_PMOFN

    time_mocker = TimeMocker(1001)

    ctx = create_ctx(mocker, None)

    # Mocking the snapshot method to return an animated QR code
    mocker.patch.object(
        ctx.camera,
        "snapshot",
        new=snapshot_generator(
            outcome=SNAP_ANIMATED_QR,
            animated_qr=tdata.TEST_PARTS_FORMAT_PMOFN,
        ),
    )
    # Leaves the loop at 2nd iteration
    PAGE_PREV_SEQ = [False, True, False]
    mocker.patch("time.ticks_ms", time_mocker.tick)
    ctx.input.page_prev_event = mocker.MagicMock(side_effect=PAGE_PREV_SEQ)
    qr_capturer = QRCodeCapture(ctx)

    qr_code, qr_format = qr_capturer.qr_capture_loop()
    assert qr_code == None

    # Assert only one frame was processed
    ctx.display.to_landscape.assert_has_calls([mocker.call()])


def test_capture_qr_code_loop_skipping(mocker, m5stickv, tdata):
    from krux.pages.qr_capture import QRCodeCapture
    from krux.wdt import wdt

    ctx = create_ctx(mocker, None)

    # Mocking the snapshot method to return an animated QR code
    # Skipping every other frame
    mocker.patch.object(
        ctx.camera,
        "snapshot",
        new=snapshot_generator(
            outcome=SNAP_FIND_ANIMATED_SKIPPING,
            animated_qr=tdata.TEST_PARTS_FORMAT_PMOFN,
        ),
    )
    # Use wdt as loop iteration counter
    spy_wdt = mocker.spy(wdt, "feed")
    qr_capturer = QRCodeCapture(ctx)

    qr_code, qr_format = qr_capturer.qr_capture_loop()
    assert qr_code == tdata.TEST_DATA_B58

    # Assert all frames were processed once
    ctx.display.to_landscape.assert_has_calls(
        [mocker.call() for _ in range(len(tdata.TEST_PARTS_FORMAT_PMOFN))]
    )
    # Assert looped 2 * fames count - 1
    spy_wdt.assert_has_calls(
        [mocker.call() for _ in range(len(tdata.TEST_PARTS_FORMAT_PMOFN) * 2 - 1)]
    )


def test_capture_qr_code_loop_duplicated_frames(mocker, m5stickv, tdata):
    from krux.pages.qr_capture import QRCodeCapture
    from krux.wdt import wdt

    ctx = create_ctx(mocker, None)

    # Mocking the snapshot method to return an animated QR code
    # Repeating once every frame
    mocker.patch.object(
        ctx.camera,
        "snapshot",
        new=snapshot_generator(
            outcome=SNAP_REPEAT_QRCODE,
            animated_qr=tdata.TEST_PARTS_FORMAT_PMOFN,
        ),
    )
    # Use wdt as loop iteration counter
    spy_wdt = mocker.spy(wdt, "feed")
    qr_capturer = QRCodeCapture(ctx)

    qr_code, qr_format = qr_capturer.qr_capture_loop()
    assert qr_code == tdata.TEST_DATA_B58

    # Assert all frames were processed once
    ctx.display.to_landscape.assert_has_calls(
        [mocker.call() for _ in range(len(tdata.TEST_PARTS_FORMAT_PMOFN))]
    )
    # Assert looped 2 * fames count - 2
    spy_wdt.assert_has_calls(
        [mocker.call() for _ in range(len(tdata.TEST_PARTS_FORMAT_PMOFN) * 2 - 2)]
    )
