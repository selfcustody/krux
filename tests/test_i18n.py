from unittest import mock


def test_translations(mocker):
    from krux.i18n import translations, TRANSLATIONS_FILE

    cases = [
        (None, None),
        ("""{"Hello world":"Hello world"}""", {"Hello world": "Hello world"}),
    ]
    for case in cases:
        mo = mock.mock_open(read_data=case[0])
        mocker.patch("builtins.open", mo)

        lookup = translations("en-US")

        assert lookup == case[1]
        mo.assert_called_once_with(TRANSLATIONS_FILE % "en-US", "r")


def test_t(mocker):
    from krux.i18n import t

    cases = [
        ("Hello world", None, "Hello world"),
        ("Hello world", """{"Hello world":"Hello"}""", "Hello"),
    ]
    for case in cases:
        mo = mock.mock_open(read_data=case[1])
        mocker.patch("builtins.open", mo)

        assert t(case[0]) == case[2]
