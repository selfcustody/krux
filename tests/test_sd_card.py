import pytest


@pytest.fixture
def mocker_sd_card_ok(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=""))
    mocker.patch("os.remove", mocker.mock_open(read_data=""))


def test_sd_read_without_mock(m5stickv):
    import machine
    from krux.sd_card import SDHandler

    ex = False
    try:
        with SDHandler() as sd:
            sd.read("afile")
    except:
        ex = True

    machine.SDCard.remount.assert_called()
    assert ex == True  # runned without mock


def test_sd_read_with_mock(m5stickv, mocker_sd_card_ok):
    import machine
    from krux.sd_card import SDHandler

    ex = False
    try:
        with SDHandler() as sd:
            sd.read("afile")
            sd.read_binary("afile")
            sd.write("afile", "")
            sd.write_binary("afile", "")
            sd.delete("afile")
    except:
        ex = True

    machine.SDCard.remount.assert_called()
    assert ex == False  # runned with mock, everything fine!
