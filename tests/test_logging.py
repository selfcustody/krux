from .shared_mocks import *
import os

TEST_LOG_PATH = os.path.join(os.path.dirname(__file__), 'krux.log')
    
def test_init():
    from krux.logging import Logger, DEBUG
    
    logger = Logger(TEST_LOG_PATH, DEBUG)
    
    assert isinstance(logger, Logger)
    assert logger.filepath == TEST_LOG_PATH
    assert logger.level == DEBUG
    
def test_log(mocker):
    m = mock.mock_open()
    mocker.patch('builtins.open', m)
    from krux.logging import Logger, DEBUG, INFO, WARN, ERROR, NONE
    
    for i, level in enumerate([DEBUG, INFO, WARN, ERROR, NONE]):
        logger = Logger(TEST_LOG_PATH, level)
        
        cases = [
            (DEBUG, 'test', 'DEBUG:test\n'),
            (INFO, 'test', 'INFO:test\n'),
            (WARN, 'test', 'WARN:test\n'),
            (ERROR, 'test', 'ERROR:test\n')
        ]
        for j, case in enumerate(cases):
            m().reset_mock()
            logger.log(case[0], case[1])
            if j >= i:
                m().write.assert_called_with(case[2])
            else:
                m().write.assert_not_called()

def test_log_fails_quietly_if_file_unavailable(mocker):
    m = mock.mock_open().side_effect = IOError()
    mocker.patch('builtins.open', m)
    from krux.logging import Logger, DEBUG
    
    logger = Logger(TEST_LOG_PATH, DEBUG)
    
    logger.log(DEBUG, 'test')
    assert logger.file is None

def test_debug(mocker):
    m = mock.mock_open()
    mocker.patch('builtins.open', m)
    from krux.logging import Logger, DEBUG
    logger = Logger(TEST_LOG_PATH, DEBUG)
    mocker.spy(logger, 'log')
    
    logger.debug('test')
    
    logger.log.assert_called_with(DEBUG, 'test')
    
def test_info(mocker):
    m = mock.mock_open()
    mocker.patch('builtins.open', m)
    from krux.logging import Logger, INFO
    logger = Logger(TEST_LOG_PATH, INFO)
    mocker.spy(logger, 'log')
    
    logger.info('test')
    
    logger.log.assert_called_with(INFO, 'test')
    
def test_warn(mocker):
    m = mock.mock_open()
    mocker.patch('builtins.open', m)
    from krux.logging import Logger, WARN
    logger = Logger(TEST_LOG_PATH, WARN)
    mocker.spy(logger, 'log')
    
    logger.warn('test')
    
    logger.log.assert_called_with(WARN, 'test')
    
def test_error(mocker):
    m = mock.mock_open()
    mocker.patch('builtins.open', m)
    from krux.logging import Logger, ERROR
    logger = Logger(TEST_LOG_PATH, ERROR)
    mocker.spy(logger, 'log')
    
    logger.error('test')
    
    logger.log.assert_called_with(ERROR, 'test')
    
def test_exception(mocker):
    m = mock.mock_open()
    mocker.patch('builtins.open', m)
    from krux.logging import Logger, ERROR
    logger = Logger(TEST_LOG_PATH, ERROR)
    mocker.spy(logger, 'log')
    
    logger.exception('test')
    
    logger.log.assert_called_with(ERROR, 'test\n')
