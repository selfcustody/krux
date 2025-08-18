import pytest
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
    mocker.patch.object(entropy_measurement, "rms_value", side_effect=STDEV_INDEX)
    fill_flash.capture_image_with_sufficient_entropy(entropy_measurement)

    # Check that the entropy_measurement_update was called 4 times
    # 3 times for poor entropy and 1 time for good entropy
    assert entropy_measurement.entropy_measurement_update.call_count == 4


@pytest.fixture
def mock_flash_normal_operations(mocker):
    # Mock normal flash read operations with realistic memory state simulation
    # Simulates flash memory with second half empty (0xff) and first half occupied (0x00)
    # NOTE: This simulation needs validation from @jdlcdl for hardware accuracy
    from krux.firmware import FLASH_SIZE

    def _mock_flash_read(address, size):
        if address > FLASH_SIZE // 2:
            return b"\xff" * size
        else:
            return b"\x00" * size

    mocker.patch("flash.read", side_effect=_mock_flash_read)
    mocker.patch("flash.write", return_value=None)


@pytest.fixture
def mock_flash_write_error(mocker):
    # Mock flash write error to test error handling during flash operations
    # Simulates hardware failures or write protection scenarios
    from krux.firmware import FLASH_SIZE

    def _mock_flash_read(address, size):
        if address > FLASH_SIZE // 2:
            return b"\xff" * size
        else:
            return b"\x00" * size

    mocker.patch("flash.read", side_effect=_mock_flash_read)
    mocker.patch("flash.write", side_effect=Exception("Flash write error"))


def test_fill_flash_entropy_timeout_scenario(amigo, mocker):
    # Test entropy timeout scenario with user confirmation navigation
    # User hesitates, checks options, then accepts but entropy capture times out
    from krux.pages.fill_flash import FillFlash
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    btn_sequence = [
        BUTTON_PAGE_PREV,  # Navigate to "No" (user hesitates)
        BUTTON_PAGE,  # Navigate back to "Yes" (user reconsiders)
        BUTTON_PAGE_PREV,  # Navigate to "No" again (still unsure)
        BUTTON_PAGE,  # Finally navigate back to "Yes"
        BUTTON_ENTER,  # Confirm "Yes" after deliberation
    ]

    # Mock entropy capture method to simulate timeout
    mocker.patch(
        "krux.pages.fill_flash.FillFlash.capture_image_with_sufficient_entropy",
        side_effect=ValueError("Insufficient entropy!"),
    )

    ctx = create_ctx(mocker, btn_sequence)
    fill_flash = FillFlash(ctx)

    # Execute test and verify timeout exception
    with pytest.raises(ValueError):
        fill_flash.fill_flash_with_camera_entropy()

    # Verify user interaction occurred as expected
    assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_fill_flash_insufficient_entropy_scenario(amigo, mocker):
    # Test insufficient entropy scenario using mocker.patch instead of PropertyMock
    # Following @qlrd recommendation to avoid false positive assertions
    from krux.pages.fill_flash import FillFlash
    from krux.pages.capture_entropy import CameraEntropy, INSUFFICIENT_VARIANCE_TH
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    btn_sequence = [
        BUTTON_PAGE_PREV,  # Navigate to "No" (user hesitates)
        BUTTON_PAGE,  # Navigate back to "Yes" (user decides to try)
        BUTTON_ENTER,  # Confirm "Yes"
    ]

    ctx = create_ctx(mocker, btn_sequence)
    fill_flash = FillFlash(ctx)
    entropy_measurement = CameraEntropy(ctx)

    # Use mocker.patch.object instead of PropertyMock as per @qlrd recommendation
    # This avoids false positive assertions that can occur with PropertyMock
    mocker.patch.object(
        entropy_measurement,
        "rms_value",
        return_value=INSUFFICIENT_VARIANCE_TH - 1,  # Below minimum threshold
    )

    # Mock the entropy measurement creation to return our configured instance
    mocker.patch(
        "krux.pages.fill_flash.CameraEntropy", return_value=entropy_measurement
    )

    # Execute test and verify insufficient entropy is handled
    with pytest.raises(ValueError, match="Insufficient entropy!"):
        fill_flash.fill_flash_with_camera_entropy()

    # Verify user interaction occurred as expected
    assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_fill_flash_touch_decline_scenario(amigo, mocker):
    # Test touch interface rejection scenario with navigation
    # User navigates through options then uses touch to decline
    from krux.pages.fill_flash import FillFlash, MENU_CONTINUE
    from krux.input import BUTTON_TOUCH, BUTTON_PAGE, BUTTON_PAGE_PREV

    btn_sequence = [
        BUTTON_PAGE,  # Navigate options to understand choices
        BUTTON_PAGE_PREV,  # Navigate back to explore both options
        BUTTON_TOUCH,  # Finally use touch interface to decline
    ]

    ctx = create_ctx(mocker, btn_sequence, touch_seq=[0])  # 0 = "No" option
    fill_flash = FillFlash(ctx)

    # Execute test and verify menu continuation
    result = fill_flash.fill_flash_with_camera_entropy()
    assert result == MENU_CONTINUE

    # Verify user interaction occurred as expected
    assert ctx.input.wait_for_button.call_count == len(btn_sequence)
    # Verify touch interface was called
    ctx.input.touch.current_index.assert_called()


def test_fill_flash_write_error_scenario(amigo, mocker, mock_flash_write_error):
    # Test flash write error handling with complex user navigation
    # User hesitates, navigates through options, confirms, but flash write fails
    from krux.pages.fill_flash import FillFlash, MENU_CONTINUE, IMAGE_BYTES_SIZE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    btn_sequence = [
        BUTTON_PAGE_PREV,  # User hesitates (go to "No")
        BUTTON_PAGE,  # Navigate to "Yes" (user reconsiders)
        BUTTON_ENTER,  # Confirm "Yes" (final decision)
    ]

    # Mock successful entropy capture
    mocker.patch(
        "krux.pages.fill_flash.FillFlash.capture_image_with_sufficient_entropy",
        return_value=b"\x00" * IMAGE_BYTES_SIZE,
    )

    ctx = create_ctx(mocker, btn_sequence)
    fill_flash = FillFlash(ctx)

    # Execute test and verify menu continuation due to flash error
    result = fill_flash.fill_flash_with_camera_entropy()
    assert result == MENU_CONTINUE

    # Verify user interaction occurred as expected
    assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_fill_flash_successful_scenarios(amigo, mocker, mock_flash_normal_operations):
    # Test successful fill flash scenarios with complex user navigation patterns
    # Covers various realistic user decision-making flows
    from krux.pages.fill_flash import FillFlash, IMAGE_BYTES_SIZE
    from krux.input import BUTTON_ENTER, BUTTON_TOUCH, BUTTON_PAGE, BUTTON_PAGE_PREV

    # Test cases as tuples following project standards
    # Format: (btn_sequence, touch_return, description)
    cases = [
        # Test complex navigation followed by acceptance
        # User explores all options extensively before final decision
        (
            [
                BUTTON_PAGE_PREV,  # Go to "No" first
                BUTTON_PAGE,  # Go to "Yes"
                BUTTON_PAGE_PREV,  # Back to "No" (exploring)
                BUTTON_PAGE_PREV,  # Stay on "No" (wrap around behavior)
                BUTTON_PAGE,  # To "Yes"
                BUTTON_PAGE,  # Stay on "Yes" (wrap around behavior)
                BUTTON_ENTER,  # Finally confirm "Yes" after exploration
            ],
            None,  # No touch interaction
            "User explores extensively before accepting",
        ),
        # Test mixed input methods with complex decision making
        # User switches between button navigation and touch interface
        (
            [
                BUTTON_PAGE_PREV,  # Navigate to "No" using buttons
                BUTTON_PAGE,  # Navigate to "Yes" using buttons
                BUTTON_TOUCH,  # Final decision using touch interface
            ],
            1,  # Touch "Yes" region
            "Mixed input methods with touch confirmation",
        ),
    ]

    # Mock successful entropy capture for all test cases
    mocker.patch(
        "krux.pages.fill_flash.FillFlash.capture_image_with_sufficient_entropy",
        return_value=b"\x00" * IMAGE_BYTES_SIZE,
    )

    for btn_sequence, touch_return, _ in cases:
        ctx = create_ctx(mocker, btn_sequence)
        fill_flash = FillFlash(ctx)

        # Configure touch interface if test case uses touch
        if touch_return is not None:
            mocker.patch.object(
                ctx.input.touch, "current_index", return_value=touch_return
            )

        # Execute test and verify results
        result = fill_flash.fill_flash_with_camera_entropy()
        # All successful operations return MENU_CONTINUE (0), not None
        assert result == 0

        # Verify user interaction occurred as expected
        assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_fill_flash_user_rejection_scenarios(amigo, mocker):
    # Tests user rejection patterns in fill flash confirmation dialog
    # Covers realistic scenarios of user hesitation and decision-making leading to rejection
    from krux.pages.fill_flash import FillFlash, MENU_CONTINUE, IMAGE_BYTES_SIZE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # Setup flash operations mocks for all rejection scenarios
    def mock_flash_read(address, size):  # pylint: disable=unused-argument
        return b"\xff" * size  # All flash empty, needs filling

    mocker.patch("flash.read", side_effect=mock_flash_read)
    mocker.patch("flash.write", return_value=None)

    # Test cases as tuples following project standards
    # Format: (btn_sequence, description)
    cases = [
        # User declines operation after careful consideration
        # Simulates thoughtful user exploring options before decisive rejection
        (
            [
                BUTTON_PAGE,  # Start by exploring "Yes" option
                BUTTON_PAGE_PREV,  # Navigate to "No" to compare
                BUTTON_PAGE,  # Go back to "Yes" for comparison
                BUTTON_PAGE_PREV,  # Return to "No" after consideration
                BUTTON_PAGE_PREV,  # Stay on "No" (confirming choice)
                BUTTON_ENTER,  # Decisively confirm "No"
            ],
            "User rejects after careful consideration",
        ),
        # Test rapid navigation followed by rejection
        # User quickly explores options then decisively rejects
        (
            [
                BUTTON_PAGE,  # Quick navigation to explore
                BUTTON_PAGE_PREV,  # Quick navigation back
                BUTTON_PAGE,  # Quick navigation forward again
                BUTTON_PAGE_PREV,  # Navigate to "No"
                BUTTON_ENTER,  # Decisively confirm "No"
            ],
            "User quickly explores then rejects",
        ),
    ]

    # Mock entropy capture to focus on user interaction testing
    mocker.patch(
        "krux.pages.fill_flash.FillFlash.capture_image_with_sufficient_entropy",
        return_value=b"\x00" * IMAGE_BYTES_SIZE,
    )

    for btn_sequence, _ in cases:
        ctx = create_ctx(mocker, btn_sequence)
        fill_flash = FillFlash(ctx)

        # Execute test and verify menu continuation (user rejected)
        result = fill_flash.fill_flash_with_camera_entropy()
        assert result == MENU_CONTINUE

        # Verify user interaction occurred as expected
        assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_fill_flash_user_acceptance_scenarios(amigo, mocker):
    # Tests user acceptance patterns with complex indecisive behavior
    # Covers realistic scenarios of extensive navigation before final acceptance
    from krux.pages.fill_flash import FillFlash, IMAGE_BYTES_SIZE
    from krux.input import BUTTON_ENTER, BUTTON_TOUCH, BUTTON_PAGE, BUTTON_PAGE_PREV

    # Setup flash operations mocks for all acceptance scenarios
    def mock_flash_read(address, size):  # pylint: disable=unused-argument
        return b"\xff" * size  # All flash empty, needs filling

    mocker.patch("flash.read", side_effect=mock_flash_read)
    mocker.patch("flash.write", return_value=None)

    # Test cases as tuples following project standards
    # Format: (btn_sequence, touch_return, description)
    cases = [
        # User extensively navigates before accepting
        # Simulates indecisive user behavior with multiple option toggles
        (
            [
                BUTTON_PAGE_PREV,  # Go to "No"
                BUTTON_PAGE,  # Back to "Yes"
                BUTTON_PAGE_PREV,  # To "No" again
                BUTTON_PAGE_PREV,  # Still "No" (wraps around)
                BUTTON_PAGE,  # Back to "Yes"
                BUTTON_ENTER,  # Finally confirm "Yes"
            ],
            None,
            "User navigates extensively before accepting",
        ),
        # Complex mixed input methods with extensive exploration
        # Tests sophisticated user behavior switching between input modes
        (
            [
                BUTTON_PAGE_PREV,  # Explore "No" option with buttons
                BUTTON_PAGE,  # Explore "Yes" option with buttons
                BUTTON_PAGE_PREV,  # Return to "No" with buttons
                BUTTON_PAGE,  # Go to "Yes" again with buttons
                BUTTON_PAGE,  # Stay on "Yes" (wrap around check)
                BUTTON_TOUCH,  # Final decision using touch interface
            ],
            1,  # Touch "Yes" region for acceptance
            "Sophisticated mixed input navigation with touch",
        ),
        # Extreme indecision followed by acceptance
        # Simulates highly indecisive user with multiple changes of mind
        (
            [
                BUTTON_PAGE_PREV,  # Initial exploration: go to "No"
                BUTTON_PAGE,  # Change mind: go to "Yes"
                BUTTON_PAGE_PREV,  # Doubt again: back to "No"
                BUTTON_PAGE,  # Reconsider: back to "Yes"
                BUTTON_PAGE_PREV,  # More doubt: to "No" again
                BUTTON_PAGE_PREV,  # Stay on "No" (wrap check)
                BUTTON_PAGE,  # Final reconsideration: to "Yes"
                BUTTON_PAGE,  # Confirm staying on "Yes" (wrap check)
                BUTTON_PAGE_PREV,  # Last minute doubt: to "No"
                BUTTON_PAGE,  # Final decision: back to "Yes"
                BUTTON_ENTER,  # Finally commit to "Yes"
            ],
            None,
            "Extreme user indecision with multiple mind changes",
        ),
    ]

    # Mock entropy capture to focus on user interaction testing
    mocker.patch(
        "krux.pages.fill_flash.FillFlash.capture_image_with_sufficient_entropy",
        return_value=b"\x00" * IMAGE_BYTES_SIZE,
    )

    for btn_sequence, touch_return, _ in cases:
        ctx = create_ctx(mocker, btn_sequence)

        # Configure touch interface if test case uses touch
        if touch_return is not None:
            mocker.patch.object(
                ctx.input.touch, "current_index", return_value=touch_return
            )

        fill_flash = FillFlash(ctx)

        # Execute test and verify successful completion (user accepted)
        result = fill_flash.fill_flash_with_camera_entropy()
        # All operations return MENU_CONTINUE (0) when completed
        assert result == 0

        # Verify user interaction occurred as expected
        assert ctx.input.wait_for_button.call_count == len(btn_sequence)
