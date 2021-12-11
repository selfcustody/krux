from .shared_mocks import *
from unittest import mock
from krux.camera import Camera
import sensor

def test_init(mocker):
    spy = mocker.spy(Camera, 'initialize_sensor')

    c = Camera()

    assert isinstance(c, Camera)
    spy.assert_called()

def test_initialize_sensor():
    c = Camera()

    c.initialize_sensor()

    sensor.reset.assert_called()
    sensor.set_pixformat.assert_called()
    assert (
        sensor.set_pixformat.call_args.args[0]._extract_mock_name() ==
        'mock.GRAYSCALE'
    )
    sensor.set_framesize.assert_called()
    assert (
        sensor.set_framesize.call_args.args[0]._extract_mock_name() ==
        'mock.QVGA'
    )

@mock.patch('sensor.snapshot', new=snapshot_generator(outcome=SNAP_SUCCESS))
@mock.patch('krux.camera.QRPartParser', new=MockQRPartParser)
def test_capture_qr_code_loop():
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            sensor.run.assert_called_with(1)
        nonlocal prev_parsed_count
        assert parsed_count > prev_parsed_count
        if parsed_count > 0:
            assert is_new
            assert total_count == MockQRPartParser.TOTAL
        prev_parsed_count = parsed_count
        return False

    result, format = c.capture_qr_code_loop(progress_callback)
    assert result == '12345678910'
    assert format == MockQRPartParser.FORMAT
    assert prev_parsed_count == MockQRPartParser.TOTAL - 1
    sensor.run.assert_called_with(0)
    
@mock.patch('sensor.snapshot', new=snapshot_generator(outcome=SNAP_SUCCESS))
@mock.patch('krux.camera.QRPartParser', new=MockQRPartParser)
def test_capture_qr_code_loop_returns_early_when_requested():
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            sensor.run.assert_called_with(1)
        nonlocal prev_parsed_count
        assert parsed_count > prev_parsed_count
        if parsed_count > 0:
            assert is_new
            assert total_count == MockQRPartParser.TOTAL
        prev_parsed_count = parsed_count
        return True

    result, format = c.capture_qr_code_loop(progress_callback)
    assert result is None
    assert format is None
    assert prev_parsed_count < MockQRPartParser.TOTAL - 1
    sensor.run.assert_called_with(0)

@mock.patch('sensor.snapshot', new=snapshot_generator(outcome=SNAP_HISTOGRAM_FAIL))
@mock.patch('krux.camera.QRPartParser', new=MockQRPartParser)
def test_capture_qr_code_loop_skips_bad_histogram():
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            sensor.run.assert_called_with(1)
        nonlocal prev_parsed_count
        if parsed_count == prev_parsed_count:
            assert not is_new
        else:
            assert parsed_count > prev_parsed_count
            if parsed_count > 0:
                assert is_new
                assert total_count == MockQRPartParser.TOTAL
        prev_parsed_count = parsed_count
        return False

    result, format = c.capture_qr_code_loop(progress_callback)
    assert result == '134567891011'
    assert format == MockQRPartParser.FORMAT
    assert prev_parsed_count == MockQRPartParser.TOTAL - 1
    sensor.run.assert_called_with(0)

@mock.patch('sensor.snapshot', new=snapshot_generator(outcome=SNAP_FIND_QRCODES_FAIL))
@mock.patch('krux.camera.QRPartParser', new=MockQRPartParser)
def test_capture_qr_code_loop_skips_missing_qrcode():
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            sensor.run.assert_called_with(1)
        nonlocal prev_parsed_count
        if parsed_count == prev_parsed_count:
            assert not is_new
        else:
            assert parsed_count > prev_parsed_count
            if parsed_count > 0:
                assert is_new
                assert total_count == MockQRPartParser.TOTAL
        prev_parsed_count = parsed_count
        return False

    result, format = c.capture_qr_code_loop(progress_callback)
    assert result == '134567891011'
    assert format == MockQRPartParser.FORMAT
    assert prev_parsed_count == MockQRPartParser.TOTAL - 1
    sensor.run.assert_called_with(0)

@mock.patch('sensor.snapshot', new=snapshot_generator(outcome=SNAP_REPEAT_QRCODE))
@mock.patch('krux.camera.QRPartParser', new=MockQRPartParser)
def test_capture_qr_code_loop_skips_duplicate_qrcode():
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            sensor.run.assert_called_with(1)
        nonlocal prev_parsed_count
        if parsed_count == prev_parsed_count:
            assert not is_new
        else:
            assert parsed_count > prev_parsed_count
            if parsed_count > 0:
                assert is_new
                assert total_count == MockQRPartParser.TOTAL
        prev_parsed_count = parsed_count
        return False

    result, format = c.capture_qr_code_loop(progress_callback)
    assert result == '134567891011'
    assert format == MockQRPartParser.FORMAT
    assert prev_parsed_count == MockQRPartParser.TOTAL - 1
    sensor.run.assert_called_with(0)
