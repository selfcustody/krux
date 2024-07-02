import pytest
from ..shared_mocks import (
    mock_context,
    snapshot_generator,
    MockQRPartParser,
    TimeMocker,
    SNAP_SUCCESS,
    DONT_FIND_ANYTHING,
)


@pytest.fixture
def mock_page_cls(mocker):
    from krux.pages import Page, Menu

    class MockPage(Page):
        def __init__(self, ctx):
            Page.__init__(
                self,
                ctx,
                Menu(
                    ctx,
                    [
                        (("Test"), mocker.MagicMock()),
                    ],
                ),
            )

    return MockPage


def test_init(mocker, m5stickv, mock_page_cls):
    from krux.pages import Page

    page = mock_page_cls(mock_context(mocker))

    assert isinstance(page, Page)


def test_flash_text(mocker, m5stickv, mock_page_cls):
    from krux.display import FLASH_MSG_TIME
    from krux.themes import WHITE, RED

    ctx = mock_context(mocker)
    mocker.patch("time.ticks_ms", new=lambda: 0)
    page = mock_page_cls(ctx)

    page.flash_text("Hello world", duration=1000)

    ctx.display.flash_text.assert_called_with("Hello world", WHITE, 1000)

    page.flash_error("Error")

    assert ctx.display.flash_text.call_count == 2
    ctx.display.flash_text.assert_called_with("Error", RED, FLASH_MSG_TIME)


def test_capture_qr_code(mocker, m5stickv, mock_page_cls):
    mocker.patch(
        "krux.camera.sensor.snapshot", new=snapshot_generator(outcome=SNAP_SUCCESS)
    )
    mocker.patch("krux.camera.QRPartParser", new=MockQRPartParser)
    from krux.camera import Camera

    ctx = mock_context(mocker)
    ctx.camera = Camera()

    mocker.patch("time.ticks_ms", new=lambda: 0)

    page = mock_page_cls(ctx)
    ctx.input.flush_events()

    qr_code, qr_format = page.capture_qr_code()
    assert qr_code == "12345678910"
    assert qr_format == MockQRPartParser.FORMAT

    ctx.display.to_landscape.assert_has_calls([mocker.call() for _ in range(10)])
    ctx.display.to_portrait.assert_has_calls([mocker.call() for _ in range(10)])
    ctx.display.draw_centered_text.assert_has_calls([mocker.call("Loading Camera..")])


def test_camera_antiglare_7740(mocker, m5stickv, mock_page_cls):
    from krux.camera import Camera, OV7740_ID, OV2640_ID, GC2145_ID

    time_mocker = TimeMocker(1001)

    mocker.patch(
        "krux.camera.sensor.snapshot",
        new=snapshot_generator(outcome=DONT_FIND_ANYTHING),
    )
    cameras = [OV7740_ID, OV2640_ID, GC2145_ID]
    for cam_id in cameras:
        mocker.patch("krux.camera.sensor.get_id", lambda: cam_id)
        mocker.patch("krux.camera.QRPartParser", new=MockQRPartParser)

        ctx = mock_context(mocker)
        ENTER_SEQ = [False, True, False, True, False]
        PAGE_PREV_SEQ = [False, False, False, True]
        mocker.patch("time.ticks_ms", time_mocker.tick)
        ctx.input.enter_event = mocker.MagicMock(side_effect=ENTER_SEQ)
        ctx.input.page_event = mocker.MagicMock(side_effect=ENTER_SEQ)
        ctx.input.page_prev_event = mocker.MagicMock(side_effect=PAGE_PREV_SEQ)
        ctx.camera = Camera()
        ctx.camera.cam_id = OV7740_ID
        mocker.spy(ctx.camera, "disable_antiglare")
        mocker.spy(ctx.camera, "enable_antiglare")
        mocker.spy(ctx.light, "turn_on")
        mocker.spy(ctx.light, "turn_off")
        page = mock_page_cls(ctx)

        qr_code, _ = page.capture_qr_code()
        assert qr_code == None
        ctx.camera.disable_antiglare.assert_called_once()
        ctx.camera.enable_antiglare.assert_called_once()
        ctx.light.turn_on.call_count == 2
        ctx.light.turn_off.call_count == 2


def test_prompt_m5stickv(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    # Enter pressed
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_ENTER])
    assert page.prompt("test prompt") == True

    # Page pressed
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_PAGE])
    assert page.prompt("test prompt") == False


def test_prompt_amigo(mocker, amigo, mock_page_cls):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_TOUCH

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    # Enter pressed
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_ENTER])
    assert page.prompt("test prompt") == True

    # Page, than Enter pressed
    page_press = [BUTTON_PAGE, BUTTON_ENTER]
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=page_press)
    assert page.prompt("test prompt") == False

    ctx.input.buttons_active = False
    # Index 0 = YES pressed
    ctx.input.touch = mocker.MagicMock(current_index=mocker.MagicMock(side_effect=[0]))
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_TOUCH])
    assert page.prompt("test prompt") == True

    # Index 1 = No pressed
    ctx.input.touch = mocker.MagicMock(current_index=mocker.MagicMock(side_effect=[1]))
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_TOUCH])
    assert page.prompt("test prompt") == False
