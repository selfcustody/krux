from krux.input import BUTTON_ENTER, BUTTON_PAGE
from krux.pages import Menu, Page
from ..shared_mocks import *

class MockPage(Page):
    def __init__(self, ctx):
        Page.__init__(self, ctx, Menu(ctx, [
            (( 'Test' ), mock.MagicMock()),
        ]))

def test_init():
    from krux.pages import Page
    
    page = MockPage(mock.MagicMock())
        
    assert isinstance(page, Page)

def test_capture_qr_code(mocker):
    mocker.patch('krux.camera.sensor.snapshot', new=snapshot_generator(outcome=SNAP_SUCCESS))
    mocker.patch('krux.camera.QRPartParser', new=MockQRPartParser)
    from krux.camera import Camera

    ctx = mock.MagicMock(
        input=mock.MagicMock(wait_for_button=mock.MagicMock(
            side_effect=[BUTTON_ENTER, BUTTON_PAGE]
        )),
        camera=Camera()
    )
        
    page = MockPage(ctx)
    
    qr_code, qr_format = page.capture_qr_code()
    assert qr_code == '12345678910'
    assert qr_format == MockQRPartParser.FORMAT
    
    ctx.display.to_landscape.assert_has_calls([mock.call() for _ in range(10)])
    ctx.display.to_portrait.assert_has_calls([mock.call() for _ in range(10)])
    ctx.display.draw_centered_text.assert_has_calls([
        mock.call('10%'),
        mock.call('20%'),
        mock.call('30%'),
        mock.call('40%'),
        mock.call('50%'),
        mock.call('60%'),
        mock.call('70%'),
        mock.call('80%'),
        mock.call('90%'),
    ])
