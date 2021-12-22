from .shared_mocks import *

def test_init(mocker):
    from krux.camera import Camera
    spy = mocker.spy(Camera, 'initialize_sensor')

    c = Camera()

    assert isinstance(c, Camera)
    spy.assert_called()

def test_initialize_sensor():
    import krux
    from krux.camera import Camera
    c = Camera()

    c.initialize_sensor()

    krux.camera.sensor.reset.assert_called()
    krux.camera.sensor.set_pixformat.assert_called()
    assert (
        krux.camera.sensor.set_pixformat.call_args.args[0]._extract_mock_name() ==
        'mock.GRAYSCALE'
    )
    krux.camera.sensor.set_framesize.assert_called()
    assert (
        krux.camera.sensor.set_framesize.call_args.args[0]._extract_mock_name() ==
        'mock.QVGA'
    )

def test_capture_qr_code_loop(mocker):
    mocker.patch('krux.camera.sensor.snapshot', new=snapshot_generator(outcome=SNAP_SUCCESS))
    mocker.patch('krux.camera.QRPartParser', new=MockQRPartParser)
    import krux
    from krux.camera import Camera
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            krux.camera.sensor.run.assert_called_with(1)
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
    krux.camera.sensor.run.assert_called_with(0)
    
def test_capture_qr_code_loop_returns_early_when_requested(mocker):
    mocker.patch('krux.camera.sensor.snapshot', new=snapshot_generator(outcome=SNAP_SUCCESS))
    mocker.patch('krux.camera.QRPartParser', new=MockQRPartParser)
    import krux
    from krux.camera import Camera
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            krux.camera.sensor.run.assert_called_with(1)
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
    krux.camera.sensor.run.assert_called_with(0)

def test_capture_qr_code_loop_skips_bad_histogram(mocker):
    mocker.patch('krux.camera.sensor.snapshot', new=snapshot_generator(outcome=SNAP_HISTOGRAM_FAIL))
    mocker.patch('krux.camera.QRPartParser', new=MockQRPartParser)
    import krux
    from krux.camera import Camera
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            krux.camera.sensor.run.assert_called_with(1)
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
    krux.camera.sensor.run.assert_called_with(0)

def test_capture_qr_code_loop_skips_missing_qrcode(mocker):
    mocker.patch('krux.camera.sensor.snapshot', new=snapshot_generator(outcome=SNAP_FIND_QRCODES_FAIL))
    mocker.patch('krux.camera.QRPartParser', new=MockQRPartParser)
    import krux
    from krux.camera import Camera
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            krux.camera.sensor.run.assert_called_with(1)
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
    krux.camera.sensor.run.assert_called_with(0)

def test_capture_qr_code_loop_skips_duplicate_qrcode(mocker):
    mocker.patch('krux.camera.sensor.snapshot', new=snapshot_generator(outcome=SNAP_REPEAT_QRCODE))
    mocker.patch('krux.camera.QRPartParser', new=MockQRPartParser)
    import krux
    from krux.camera import Camera
    c = Camera()

    prev_parsed_count = -1
    def progress_callback(total_count, parsed_count, is_new):
        if parsed_count == 0:
            krux.camera.sensor.run.assert_called_with(1)
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
    krux.camera.sensor.run.assert_called_with(0)
