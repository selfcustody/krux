from .shared_mocks import *

TEST_SPLASH = """
BTCBTCBTCBTCBTCB
TCBTC      BTCBT
CBTCB      TCBTC
BTCBT      CBTCB
TCBTC      BTCBT
CBTCB      TCBTC
B              T
C  K  r  u  x  B
T              C
BTCBT      CBTCB
TCBTC      BTCBT
CBTCB      TCBTC
BTCBT      CBTCB
TCBTC      BTCBT
CBTCB      TCBTC
BTCBT      CBTCB
TCBTCBTCBTCBTCBT
"""

def test_init(mocker):
    mocker.patch('krux.display.lcd', new=mock.MagicMock())
    import krux
    from krux.display import Display
    import board
    mocker.spy(Display, 'initialize_lcd')

    d = Display()

    assert isinstance(d, Display)
    d.initialize_lcd.assert_called()
    
    krux.display.lcd.init.assert_called_once()
    assert 'type' in krux.display.lcd.init.call_args.kwargs
    assert (
        krux.display.lcd.init.call_args.kwargs['type'] ==
        board.config['lcd']['lcd_type']
    )

def test_to_lines(mocker):
    from krux.display import Display
    
    cases = [
        (135, 10, 'Two Words', ['Two Words']),
        (135, 10, 'Two\nWords', ['Two', 'Words']),
        (135, 10, 'Two\n\nWords', ['Two', '', 'Words']),
        (135, 10, 'More Than Two Words', ['More Than', 'Two Words']),
        (135, 10, 'A bunch of words that span multiple lines..', ['A bunch of', 'words that span', 'multiple lines..']),
        (135, 10, 'tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s', ['tpubDCDuqu5HtBX2', 'aD7wxvnHcj1DgFN1', 'UVgzLkA1Ms4Va4P7', 'TpJ3jDknkPLwWT2S', 'qrKXNNAtJBCPcbJ8', 'Tcpm6nLxgFapCZyh', 'KgqwcEGv1BVpD7s']),
        (135, 10, 'xpub: tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s', ['xpub:', 'tpubDCDuqu5HtBX2', 'aD7wxvnHcj1DgFN1', 'UVgzLkA1Ms4Va4P7', 'TpJ3jDknkPLwWT2S', 'qrKXNNAtJBCPcbJ8', 'Tcpm6nLxgFapCZyh', 'KgqwcEGv1BVpD7s']),
        (135, 10, 'Log Level\nNONE', ['Log Level', 'NONE']),
        (135, 10, 'Log Level\nDEBUG', ['Log Level', 'DEBUG']),
        (135, 10, 'Log Level\nWARNING', ['Log Level', 'WARNING']),
        
        (75, 10, 'Two Words', ['Two', 'Words']),
        (75, 10, 'Two\nWords', ['Two', 'Words']),
        (75, 10, 'Two\n\nWords', ['Two', '', 'Words']),
        (75, 10, 'More Than Two Words', ['More', 'Than', 'Two', 'Words']),
        (75, 10, 'A bunch of text that spans multiple lines..', ['A bunch', 'of text', 'that', 'spans', 'multipl', 'e', 'lines..']),
        (75, 10, 'tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s', ['tpubDCD', 'uqu5HtB', 'X2aD7wx', 'vnHcj1D', 'gFN1UVg', 'zLkA1Ms', '4Va4P7T', 'pJ3jDkn', 'kPLwWT2', 'SqrKXNN', 'AtJBCPc', 'bJ8Tcpm', '6nLxgFa', 'pCZyhKg', 'qwcEGv1', 'BVpD7s']),
        (75, 10, 'xpub: tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s', ['xpub:', 'tpubDCD', 'uqu5HtB', 'X2aD7wx', 'vnHcj1D', 'gFN1UVg', 'zLkA1Ms', '4Va4P7T', 'pJ3jDkn', 'kPLwWT2', 'SqrKXNN', 'AtJBCPc', 'bJ8Tcpm', '6nLxgFa', 'pCZyhKg', 'qwcEGv1', 'BVpD7s']),
        (75, 10, 'Log Level\nNONE', ['Log', 'Level', 'NONE']),
        (75, 10, 'Log Level\nDEBUG', ['Log', 'Level', 'DEBUG']),
        (75, 10, 'Log Level\nWARNING', ['Log', 'Level', 'WARNING']),
        
        (240, 10, 'Two Words', ['Two Words']),
        (240, 10, 'Two\nWords', ['Two', 'Words']),
        (240, 10, 'Two\n\nWords', ['Two', '', 'Words']),
        (240, 10, 'More Than Two Words', ['More Than Two Words']),
        (240, 10, 'A bunch of text that spans multiple lines..', ['A bunch of text that', 'spans multiple lines..']),
        (240, 10, 'tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s', ['tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN', '1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT', '2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapC', 'ZyhKgqwcEGv1BVpD7s']),
        (240, 10, 'xpub: tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s', ['xpub:', 'tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN', '1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT', '2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapC', 'ZyhKgqwcEGv1BVpD7s']),
        (240, 10, 'Log Level\nNONE', ['Log Level', 'NONE']),
        (240, 10, 'Log Level\nDEBUG', ['Log Level', 'DEBUG']),
        (240, 10, 'Log Level\nWARNING', ['Log Level', 'WARNING']),
    ]
    for case in cases:
        mocker.patch('krux.display.lcd', new=mock.MagicMock(
            height=mock.MagicMock(return_value=case[0])
        ))
        d = Display()

        lines = d.to_lines(case[2], padding=case[1])
        assert lines == case[3]
    