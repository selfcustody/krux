import pytest

# import binascii

# TRANSLATION_SLUGS = [
#     "Hello world",
#     "Hello",
#     "Untranslated slug",
# ]

# INDEX_REFERENCE = [
#     binascii.crc32(TRANSLATION_SLUGS[0].encode("utf-8")),
#     binascii.crc32(TRANSLATION_SLUGS[1].encode("utf-8")),
#     binascii.crc32(TRANSLATION_SLUGS[2].encode("utf-8")),
# ]

# PT_BR = [
#     "Olá mundo",
#     "Olá",
#     "Untranslated slug",
# ]


def test_translations(mocker, m5stickv):
    from krux.krux_settings import t, locale_control

    # Test default language
    assert t("Load Mnemonic") == "Load Mnemonic"

    # Test pt_BR
    locale_control.load_locale("pt_BR")
    assert t("Load Mnemonic") == "Carregar Mnemônico"

    # Test non existent slug
    assert t("New Text") == "New Text"
