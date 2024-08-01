from . import create_ctx
from ..test_qr import tdata
from krux.qr import FORMAT_PMOFN

from ..shared_mocks import (
    snapshot_generator,
    SNAP_ANIMATED_QR,
    DONT_FIND_ANYTHING,
    TimeMocker,
    mock_context,
)


def test_capture_qr_code(mocker, m5stickv, tdata):
    from krux.pages.qr_capture import QRCodeCapture

    ctx = create_ctx(mocker, None)

    # Mocking the snapshot method to return an animated QR code
    # tdata.TEST_PARTS_FORMAT_PMOFN contains tdata.TEST_DATA_B58,
    # split in a 3 parts PMofN QR code
    mocker.patch.object(
        ctx.camera,
        "snapshot",
        new=snapshot_generator(
            outcome=SNAP_ANIMATED_QR,
            animated_qr=tdata.TEST_PARTS_FORMAT_PMOFN,
        ),
    )
    qr_capturer = QRCodeCapture(ctx)

    qr_code, qr_format = qr_capturer.qr_capture_loop()
    assert qr_code == tdata.TEST_DATA_B58
    assert qr_format == FORMAT_PMOFN

    ctx.display.to_landscape.assert_has_calls(
        [mocker.call() for _ in range(len(tdata.TEST_PARTS_FORMAT_PMOFN))]
    )
    ctx.display.to_portrait.assert_has_calls(
        [mocker.call() for _ in range(len(tdata.TEST_PARTS_FORMAT_PMOFN))]
    )
    ctx.display.draw_centered_text.assert_has_calls([mocker.call("Loading Camera..")])


def test_camera_antiglare(mocker, m5stickv):
    from krux.pages.qr_capture import QRCodeCapture
    from krux.camera import Camera, OV7740_ID, OV2640_ID, GC2145_ID

    time_mocker = TimeMocker(1001)

    ctx = mock_context(mocker)
    mocker.patch.object(
        ctx.camera,
        "snapshot",
        new=snapshot_generator(outcome=DONT_FIND_ANYTHING),
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


# def test_capture_qr_code_loop(mocker, all_devices):
#     mocker.patch(
#         "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
#     )
#     mocker.patch("krux.camera.QRPartParser", new=MockQRPartParser)
#     import krux
#     from krux.camera import Camera

#     c = Camera()

#     prev_parsed_count = -1

#     def progress_callback(total_count, parsed_count, is_new):
#         if parsed_count == 0:
#             krux.camera.sensor.run.assert_called_with(1)
#         nonlocal prev_parsed_count
#         assert parsed_count > prev_parsed_count
#         if parsed_count > 0:
#             assert is_new
#             assert total_count == MockQRPartParser.TOTAL
#         prev_parsed_count = parsed_count
#         return False

#     result, format = c.capture_qr_code_loop(progress_callback)
#     assert result == "12345678910"
#     assert format == MockQRPartParser.FORMAT
#     assert prev_parsed_count == MockQRPartParser.TOTAL - 1
#     krux.camera.sensor.run.assert_called_with(0)
#     krux.camera.wdt.feed.assert_called()


# def test_capture_qr_code_loop_returns_early_when_requested(mocker, m5stickv):
#     mocker.patch(
#         "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
#     )
#     mocker.patch("krux.camera.QRPartParser", new=MockQRPartParser)
#     import krux
#     from krux.camera import Camera

#     c = Camera()

#     prev_parsed_count = -1

#     def progress_callback(total_count, parsed_count, is_new):
#         if parsed_count == 0:
#             krux.camera.sensor.run.assert_called_with(1)
#         nonlocal prev_parsed_count
#         assert parsed_count > prev_parsed_count
#         if parsed_count > 0:
#             assert is_new
#             assert total_count == MockQRPartParser.TOTAL
#         prev_parsed_count = parsed_count
#         return True

#     result, format = c.capture_qr_code_loop(progress_callback)
#     assert result is None
#     assert format is None
#     assert prev_parsed_count < MockQRPartParser.TOTAL - 1
#     krux.camera.sensor.run.assert_called_with(0)
#     krux.camera.wdt.feed.assert_called()


# def test_capture_qr_code_loop_skips_missing_qrcode(mocker, m5stickv):
#     mocker.patch(
#         "krux.camera.sensor.snapshot",
#         new=snapshot_generator(outcome=SNAP_FIND_QRCODES_FAIL),
#     )
#     mocker.patch("krux.camera.QRPartParser", new=MockQRPartParser)
#     import krux
#     from krux.camera import Camera

#     c = Camera()

#     prev_parsed_count = -1

#     def progress_callback(total_count, parsed_count, is_new):
#         if parsed_count == 0:
#             krux.camera.sensor.run.assert_called_with(1)
#         nonlocal prev_parsed_count
#         if parsed_count == prev_parsed_count:
#             assert not is_new
#         else:
#             assert parsed_count > prev_parsed_count
#             if parsed_count > 0:
#                 assert is_new
#                 assert total_count == MockQRPartParser.TOTAL
#         prev_parsed_count = parsed_count
#         return False

#     result, format = c.capture_qr_code_loop(progress_callback)
#     assert result == "134567891011"
#     assert format == MockQRPartParser.FORMAT
#     assert prev_parsed_count == MockQRPartParser.TOTAL - 1
#     krux.camera.sensor.run.assert_called_with(0)
#     krux.camera.wdt.feed.assert_called()


# def test_capture_qr_code_loop_skips_duplicate_qrcode(mocker, m5stickv):
#     mocker.patch(
#         "krux.camera.sensor.snapshot",
#         new=snapshot_generator(outcome=SNAP_REPEAT_QRCODE),
#     )
#     mocker.patch("krux.camera.QRPartParser", new=MockQRPartParser)
#     import krux
#     from krux.camera import Camera

#     c = Camera()

#     prev_parsed_count = -1

#     def progress_callback(total_count, parsed_count, is_new):
#         if parsed_count == 0:
#             krux.camera.sensor.run.assert_called_with(1)
#         nonlocal prev_parsed_count
#         if parsed_count == prev_parsed_count:
#             assert not is_new
#         else:
#             assert parsed_count > prev_parsed_count
#             if parsed_count > 0:
#                 assert is_new
#                 assert total_count == MockQRPartParser.TOTAL
#         prev_parsed_count = parsed_count
#         return False

#     result, format = c.capture_qr_code_loop(progress_callback)
#     assert result == "134567891011"
#     assert format == MockQRPartParser.FORMAT
#     assert prev_parsed_count == MockQRPartParser.TOTAL - 1
#     krux.camera.sensor.run.assert_called_with(0)
#     krux.camera.wdt.feed.assert_called()
