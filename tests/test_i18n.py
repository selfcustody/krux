import pytest


@pytest.fixture
def tdata(mocker):
    import binascii

    return [
        {"en-US": {binascii.crc32("Hello world".encode("utf-8")): "Hello"}},
        {"es-MX": {binascii.crc32("Hello world".encode("utf-8")): "Hola"}},
    ]


def test_translations(mocker, m5stickv, tdata):
    import binascii
    from krux.i18n import translations

    cases = [
        (tdata[0], {binascii.crc32("Hello world".encode("utf-8")): "Hello"}),
        (tdata[1], None),
    ]
    for case in cases:
        mocker.patch("krux.i18n.translation_table", case[0])
        lookup = translations("en-US")

        assert lookup == case[1]


def test_t(mocker, m5stickv, tdata):
    from krux.i18n import t

    cases = [
        (tdata[0], "Hello world", "Hello"),
        (tdata[1], "Hello world", "Hello world"),
    ]
    for case in cases:
        mocker.patch("krux.i18n.translation_table", case[0])

        assert t(case[1]) == case[2]
