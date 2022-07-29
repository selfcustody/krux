import pytest


@pytest.fixture
def tdata(mocker):
    import os
    from collections import namedtuple

    TEST_LOG_PATH = os.path.join(os.path.dirname(__file__), "krux.log")

    return namedtuple("TestData", ["TEST_LOG_PATH"])(TEST_LOG_PATH)


def test_init(mocker, m5stickv, tdata):
    from krux.logging import Logger, DEBUG

    logger = Logger(tdata.TEST_LOG_PATH, DEBUG)

    assert isinstance(logger, Logger)
    assert logger.filepath == tdata.TEST_LOG_PATH
    assert logger.level == DEBUG


def test_log(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger, DEBUG, INFO, WARN, ERROR, NONE

    for i, level in enumerate([DEBUG, INFO, WARN, ERROR, NONE]):
        logger = Logger(tdata.TEST_LOG_PATH, level)

        cases = [
            (DEBUG, "test", "DEBUG:test\n"),
            (INFO, "test", "INFO:test\n"),
            (WARN, "test", "WARN:test\n"),
            (ERROR, "test", "ERROR:test\n"),
        ]
        for j, case in enumerate(cases):
            m().reset_mock()
            logger.log(case[0], case[1])
            if j >= i:
                m().write.assert_called_with(case[2])
            else:
                m().write.assert_not_called()


def test_log_fails_quietly_if_file_unavailable(mocker, m5stickv, tdata):
    m = mocker.mock_open().side_effect = IOError()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger, DEBUG

    logger = Logger(tdata.TEST_LOG_PATH, DEBUG)

    logger.log(DEBUG, "test")
    assert logger.file is None


def test_debug(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger, DEBUG

    logger = Logger(tdata.TEST_LOG_PATH, DEBUG)
    mocker.spy(logger, "log")

    logger.debug("test")

    logger.log.assert_called_with(DEBUG, "test")


def test_info(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger, INFO

    logger = Logger(tdata.TEST_LOG_PATH, INFO)
    mocker.spy(logger, "log")

    logger.info("test")

    logger.log.assert_called_with(INFO, "test")


def test_warn(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger, WARN

    logger = Logger(tdata.TEST_LOG_PATH, WARN)
    mocker.spy(logger, "log")

    logger.warn("test")

    logger.log.assert_called_with(WARN, "test")


def test_error(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger, ERROR

    logger = Logger(tdata.TEST_LOG_PATH, ERROR)
    mocker.spy(logger, "log")

    logger.error("test")

    logger.log.assert_called_with(ERROR, "test")


def test_exception(mocker, m5stickv, tdata):
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    from krux.logging import Logger, ERROR

    logger = Logger(tdata.TEST_LOG_PATH, ERROR)
    mocker.spy(logger, "log")

    logger.exception("test")

    logger.log.assert_called_with(ERROR, "test\n")
