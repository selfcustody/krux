import binascii
from unittest import mock


def translation_tables():
    return [
        {"en-US": {binascii.crc32("Hello world".encode("utf-8")): "Hello"}},
        {"es-MX": {binascii.crc32("Hello world".encode("utf-8")): "Hola"}},
    ]


def test_translations(mocker):
    from krux.i18n import translations

    tables = translation_tables()
    cases = [
        (tables[0], {binascii.crc32("Hello world".encode("utf-8")): "Hello"}),
        (tables[1], None),
    ]
    for case in cases:
        mocker.patch("krux.i18n.translation_table", case[0])
        lookup = translations("en-US")

        assert lookup == case[1]


def test_t(mocker):
    from krux.i18n import t

    tables = translation_tables()
    cases = [
        (tables[0], "Hello world", "Hello"),
        (tables[1], "Hello world", "Hello world"),
    ]
    for case in cases:
        mocker.patch("krux.i18n.translation_table", case[0])

        assert t(case[1]) == case[2]
