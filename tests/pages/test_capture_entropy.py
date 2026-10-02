from ..shared_mocks import mock_context, snapshot_generator, SNAP_SUCCESS, IMAGE_TO_HASH
import hashlib
import random


def _called_with_insufficient_entropy_message(ctx):
    """Helper bool to determine if ctx.display.draw_centered_text was called with a message including "Insufficient" """
    return (
        len(
            [
                call
                for call in ctx.display.draw_centered_text.call_args_list
                if "Insufficient" in call.args[0]
            ]
        )
        > 0
    )


def test_cancel_capture(amigo, mocker):
    """Test that the capture method returns None when the user cancels the capture"""
    from krux.pages.capture_entropy import CameraEntropy

    # Mock snapshot to return a successful snapshot
    mocker.patch(
        "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
    )

    # Create a mock context
    ctx = mock_context(mocker)

    # Mock page_event to return True and other events to return False
    mocker.patch.object(ctx.input, "enter_event", return_value=False)
    mocker.patch.object(ctx.input, "touch_event", return_value=False)
    # run 2 times before cancel button is pressed
    mocker.patch.object(ctx.input, "page_event", side_effect=[False, False, True])
    mocker.patch.object(ctx.input, "page_prev_event", return_value=False)

    # Create an instance of CameraEntropy
    camera_entropy = CameraEntropy(ctx)

    # Mock flash_text to monitor its calls
    camera_entropy.flash_text = mocker.MagicMock()

    # Call the capture method
    result = camera_entropy.capture()

    # Assert that the result is None, indicating cancellation
    assert result is None

    # Assert ctx.flash_text was called with "Capture cancelled"
    camera_entropy.flash_text.assert_called_with("Capture cancelled")


def test_insufficient_variance(amigo, mocker):
    """Test that the capture method returns None when the variance is below the threshold"""
    from krux.pages.capture_entropy import (
        CameraEntropy,
        INSUFFICIENT_VARIANCE_TH,
        INSUFFICIENT_SHANNONS_ENTROPY_TH,
    )

    # Mock snapshot to return a successful snapshot
    mocker.patch(
        "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
    )

    # Create a mock context
    ctx = mock_context(mocker)

    # Mock touch_event to return True and other events to return False
    mocker.patch.object(ctx.input, "enter_event", return_value=False)
    mocker.patch.object(ctx.input, "touch_event", return_value=True)
    mocker.patch.object(ctx.input, "page_event", return_value=False)
    mocker.patch.object(ctx.input, "page_prev_event", return_value=False)

    # Create an instance of CameraEntropy
    camera_entropy = CameraEntropy(ctx)

    # Mock rms value to return a value below the threshold
    variance = INSUFFICIENT_VARIANCE_TH - 1
    camera_entropy.rms_value = mocker.MagicMock(return_value=variance)

    # Mock shannon.entropy_img16b to return a value above the threshold
    shannon_value = INSUFFICIENT_SHANNONS_ENTROPY_TH + 1
    mocker.patch("shannon.entropy_img16b", return_value=shannon_value)

    # Call the capture method
    result = camera_entropy.capture()

    # Assert that the result is None
    assert result is None

    # Assert ctx.display.draw_centered_text was called with "Insufficient entropy!"
    assert _called_with_insufficient_entropy_message(ctx)


def test_insufficient_shannons_entropy(amigo, mocker):
    """Test that the capture method returns None when the Shannon's entropy is below the threshold"""
    from krux.pages.capture_entropy import (
        CameraEntropy,
        INSUFFICIENT_VARIANCE_TH,
        INSUFFICIENT_SHANNONS_ENTROPY_TH,
    )

    # Mock snapshot to return a successful snapshot
    mocker.patch(
        "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
    )

    # Create a mock context
    ctx = mock_context(mocker)

    # Mock touch_event to return True and other events to return False
    mocker.patch.object(ctx.input, "enter_event", return_value=False)
    mocker.patch.object(ctx.input, "touch_event", return_value=True)
    mocker.patch.object(ctx.input, "page_event", return_value=False)
    mocker.patch.object(ctx.input, "page_prev_event", return_value=False)

    # Create an instance of CameraEntropy
    camera_entropy = CameraEntropy(ctx)

    # Mock rms value to return a value above the threshold
    variance = INSUFFICIENT_VARIANCE_TH + 1
    camera_entropy.rms_value = mocker.MagicMock(return_value=variance)

    # Mock shannon.entropy_img16b to return a value below the threshold
    shannon_value = INSUFFICIENT_SHANNONS_ENTROPY_TH - 1
    mocker.patch("shannon.entropy_img16b", return_value=shannon_value)

    # Call the capture method
    result = camera_entropy.capture()

    # Assert that the result is None
    assert result is None

    # Assert ctx.display.draw_centered_text was called with "Insufficient entropy!"
    assert _called_with_insufficient_entropy_message(ctx)


def test_poor_variance(amigo, mocker):
    """
    Test that the capture method return a valid hash when the variance is below poor threshold,
    but above the insufficient threshold, and the Shannon's entropy is above the threshold
    """
    from krux.pages.capture_entropy import (
        CameraEntropy,
        POOR_VARIANCE_TH,
        INSUFFICIENT_SHANNONS_ENTROPY_TH,
    )

    # Mock snapshot to return a successful snapshot
    mocker.patch(
        "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
    )

    # Create a mock context
    ctx = mock_context(mocker)

    # Mock touch_event to return True and other events to return False
    mocker.patch.object(ctx.input, "enter_event", return_value=False)
    mocker.patch.object(ctx.input, "touch_event", return_value=True)
    mocker.patch.object(ctx.input, "page_event", return_value=False)
    mocker.patch.object(ctx.input, "page_prev_event", return_value=False)

    # Create an instance of CameraEntropy
    camera_entropy = CameraEntropy(ctx)

    # Mock rms value to return a value below the poor threshold, but above insufficient
    variance = POOR_VARIANCE_TH - 1
    camera_entropy.rms_value = mocker.MagicMock(return_value=variance)

    # Mock shannon.entropy_img16b to return a value above the threshold
    shannon_value = INSUFFICIENT_SHANNONS_ENTROPY_TH + 1
    mocker.patch("shannon.entropy_img16b", return_value=shannon_value)

    # Call the capture method
    result = camera_entropy.capture()

    # Assert that the result has the a valid hash
    hasher = hashlib.sha256()
    hasher.update(IMAGE_TO_HASH)

    assert result == hasher.digest()

    # Assert ctx.display.draw_centered_text was NOT called with "Insufficient entropy!"
    assert not _called_with_insufficient_entropy_message(ctx)


def test_good_variance_good_shannons_entropy(amigo, mocker):
    """
    Test that the capture method return a valid hash when the variance and Shannon's entropy are above
    poor and insufficient thresholds
    """
    from krux.pages.capture_entropy import (
        CameraEntropy,
        POOR_VARIANCE_TH,
        INSUFFICIENT_SHANNONS_ENTROPY_TH,
    )

    # Mock snapshot to return a successful snapshot
    mocker.patch(
        "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
    )

    # Create a mock context
    ctx = mock_context(mocker)

    # Mock touch_event to return True and other events to return False
    mocker.patch.object(ctx.input, "enter_event", return_value=False)
    mocker.patch.object(ctx.input, "touch_event", return_value=True)
    mocker.patch.object(ctx.input, "page_event", return_value=False)
    mocker.patch.object(ctx.input, "page_prev_event", return_value=False)

    # Create an instance of CameraEntropy
    camera_entropy = CameraEntropy(ctx)

    # Mock rms value to return a value below the poor threshold, but above insufficient
    variance = POOR_VARIANCE_TH + 1
    camera_entropy.rms_value = mocker.MagicMock(return_value=variance)

    # Mock shannon.entropy_img16b to return a value above the threshold
    shannon_value = INSUFFICIENT_SHANNONS_ENTROPY_TH + 1
    mocker.patch("shannon.entropy_img16b", return_value=shannon_value)

    # Call the capture method
    result = camera_entropy.capture()

    # Assert that the result has the a valid hash
    hasher = hashlib.sha256()
    hasher.update(IMAGE_TO_HASH)

    assert result == hasher.digest()

    # Assert ctx.display.draw_centered_text was NOT called with "Insufficient entropy!"
    assert not _called_with_insufficient_entropy_message(ctx)


def test_entropy_measurement_update_state_2(amigo, mocker):
    """
    Test that runs capture() enough times to hit
    measurement states 2 triggering a_stdev and b_stdev updates.
    """
    from krux.pages.capture_entropy import (
        CameraEntropy,
        INSUFFICIENT_SHANNONS_ENTROPY_TH,
        POOR_VARIANCE_TH,
    )

    # Create a mock context
    ctx = mock_context(mocker)

    # Mock touch_event to return True and other events to return False
    # We will run 3 frames before the capture is triggered, ensuring that
    # the measurement_machine_state property progresses through states 0, 1, 2
    # thus executing the under test standard deviation update branches
    mocker.patch.object(ctx.input, "enter_event", return_value=False)
    mocker.patch.object(
        ctx.input, "touch_event", side_effect=[False, False, False, True]
    )

    # Trigger capture in 4th frame
    mocker.patch.object(ctx.input, "page_event", return_value=False)
    mocker.patch.object(ctx.input, "page_prev_event", return_value=False)

    # Prepare mock statistics with nearly known values
    def mock_snapshot():
        mock_img = mocker.MagicMock()
        mock_stats = mocker.MagicMock()
        mock_stats.l_stdev.return_value = POOR_VARIANCE_TH + 1
        mock_stats.a_stdev.return_value = random.randint(40, 60)
        mock_stats.b_stdev.return_value = 75
        mock_img.get_statistics.return_value = mock_stats
        mock_img.to_bytes.return_value = IMAGE_TO_HASH
        mock_img.width.return_value = 320
        mock_img.height.return_value = 240
        return mock_img

    # Provide 4 frames to hit state
    mocker.patch(
        "krux.camera.sensor.snapshot", side_effect=[mock_snapshot() for _ in range(4)]
    )

    # Patch entropy and verify it's above threshold
    shannon_val = INSUFFICIENT_SHANNONS_ENTROPY_TH + 1
    mocker.patch("shannon.entropy_img16b", return_value=shannon_val)

    # Create an instance of CameraEntropy
    camera_entropy = CameraEntropy(ctx)

    # Run capture and confirm final hash matches expected
    result = camera_entropy.capture()
    expected_hash = hashlib.sha256(IMAGE_TO_HASH).digest()
    assert result == expected_hash


def test_entropy_measurement_update_state_3(amigo, mocker):
    """
    Test to ensure measurement_machine_state == 3
    path is hit BEFORE final capture, and b_stdev is executed
    outside the all_at_once block.
    """
    from krux.pages.capture_entropy import (
        CameraEntropy,
        INSUFFICIENT_SHANNONS_ENTROPY_TH,
        POOR_VARIANCE_TH,
    )

    # Create a mock context
    ctx = mock_context(mocker)

    # Mock touch_event to return True and other events to return False
    # We will run 4 frames before the capture is triggered, this ensures that
    # the entropy measurement state machine progresses through
    # states 0, 1, 2, 3 thus executing all the standard deviation
    # update branches
    mocker.patch.object(ctx.input, "enter_event", return_value=False)
    mocker.patch.object(
        ctx.input, "touch_event", side_effect=[False, False, False, False, True]
    )

    # Trigger capture in 5th frame
    mocker.patch.object(ctx.input, "page_event", return_value=False)
    mocker.patch.object(ctx.input, "page_prev_event", return_value=False)

    # Prepare mock statistics with nearly known values
    def mock_snapshot():
        mock_img = mocker.MagicMock()
        mock_stats = mocker.MagicMock()
        mock_stats.l_stdev.return_value = POOR_VARIANCE_TH + 1
        mock_stats.a_stdev.return_value = random.randint(40, 60)
        mock_stats.b_stdev.return_value = 99
        mock_img.get_statistics.return_value = mock_stats
        mock_img.to_bytes.return_value = IMAGE_TO_HASH
        mock_img.width.return_value = 320
        mock_img.height.return_value = 240
        return mock_img

    # Provide 5 frames to hit state
    mocker.patch(
        "krux.camera.sensor.snapshot", side_effect=[mock_snapshot() for _ in range(5)]
    )

    # Patch entropy and verify it's above threshold
    shannon_val = INSUFFICIENT_SHANNONS_ENTROPY_TH + 1
    mocker.patch("shannon.entropy_img16b", return_value=shannon_val)

    # Create an instance of CameraEntropy
    camera_entropy = CameraEntropy(ctx)

    # Run capture and confirm final hash matches expected
    result = camera_entropy.capture()
    expected_hash = hashlib.sha256(IMAGE_TO_HASH).digest()
    assert result == expected_hash
