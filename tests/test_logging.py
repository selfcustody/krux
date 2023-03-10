import pytest


@pytest.fixture
def tdata(mocker):
    import os
    from collections import namedtuple

    TEST_LOG_PATH = os.path.join(os.path.dirname(__file__), "krux.log")

    return namedtuple("TestData", ["TEST_LOG_PATH"])(TEST_LOG_PATH)


def test_init(mocker, m5stickv, tdata):
    from krux.logging import Logger

    logger = Logger(tdata.TEST_LOG_PATH)

    assert isinstance(logger, Logger)
    assert logger.filepath == tdata.TEST_LOG_PATH


def test_log(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger
    from krux.krux_settings import Settings
    from krux.krux_settings import LoggingSettings

    for i, level in enumerate(["DEBUG", "INFO", "WARN", "ERROR", "NONE"]):
        logger = Logger(tdata.TEST_LOG_PATH)
        Settings().logging.level = level

        cases = [
            (LoggingSettings.DEBUG, "test", "DEBUG:test\n"),
            (LoggingSettings.INFO, "test", "INFO:test\n"),
            (LoggingSettings.WARN, "test", "WARN:test\n"),
            (LoggingSettings.ERROR, "test", "ERROR:test\n"),
        ]
        for j, case in enumerate(cases):
            m().reset_mock()
            logger.log(case[0], case[1])
            if j >= i:
                m().write.assert_called_with(case[2])
            else:
                m().write.assert_not_called()


def test_log_fails_quietly_if_file_unavailable(mocker, m5stickv, tdata):
    m = mocker.mock_open().side_effect = OSError()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger
    from krux.krux_settings import LoggingSettings

    logger = Logger(tdata.TEST_LOG_PATH)

    logger.log(LoggingSettings.DEBUG, "test")
    assert logger.file is None


def test_debug(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger
    from krux.krux_settings import LoggingSettings

    logger = Logger(tdata.TEST_LOG_PATH)
    mocker.spy(logger, "log")

    logger.debug("test")

    logger.log.assert_called_with(LoggingSettings.DEBUG, "test")


def test_info(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger
    from krux.krux_settings import LoggingSettings

    logger = Logger(tdata.TEST_LOG_PATH)
    mocker.spy(logger, "log")

    logger.info("test")

    logger.log.assert_called_with(LoggingSettings.INFO, "test")


def test_warn(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger
    from krux.krux_settings import LoggingSettings

    logger = Logger(tdata.TEST_LOG_PATH)
    mocker.spy(logger, "log")

    logger.warn("test")

    logger.log.assert_called_with(LoggingSettings.WARN, "test")


def test_error(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger
    from krux.krux_settings import LoggingSettings

    logger = Logger(tdata.TEST_LOG_PATH)
    mocker.spy(logger, "log")

    logger.error("test")

    logger.log.assert_called_with(LoggingSettings.ERROR, "test")


def test_exception(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger
    from krux.krux_settings import LoggingSettings

    logger = Logger(tdata.TEST_LOG_PATH)
    mocker.spy(logger, "log")

    logger.exception("test")

    logger.log.assert_called_with(LoggingSettings.ERROR, "test\n")
