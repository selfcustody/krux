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
    from krux.krux_settings import _translations

    cases = [
        (tdata[0], None),
        (tdata[1], {binascii.crc32("Hello world".encode("utf-8")): "Hola"}),
    ]
    for case in cases:
        mocker.patch("krux.krux_settings.translation_index", list(case[0].keys())[0])
        mocker.patch("krux.translations_es_MX.translation_dict", case[1])
        lookup = _translations(list(case[0].keys())[0])

        assert lookup == case[1]


def test_t(mocker, m5stickv, tdata):
    from krux.krux_settings import t

    cases = [
        (tdata[0], "Hello", "Hello"),
        (tdata[1], "Hello world", "Hello world"),
    ]

    for case in cases:
        mocker.patch("krux.krux_settings.translation_index", list(case[0].keys())[0])

        assert t(case[1]) == case[2]
