from krux.display import DEFAULT_PADDING
from krux.key import Key
from ..shared_mocks import *
from krux.input import BUTTON_ENTER, BUTTON_PAGE
from krux.qr import FORMAT_PMOFN, FORMAT_NONE
from embit.networks import NETWORKS

TEST_12_WORD_MNEMONIC = 'olympic term tissue route sense program under choose bean emerge velvet absurd'
TEST_24_WORD_MNEMONIC = 'brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major'

SINGLEKEY_12_WORD_KEY = Key(TEST_12_WORD_MNEMONIC, False, NETWORKS['main'])
SINGLEKEY_24_WORD_KEY = Key(TEST_24_WORD_MNEMONIC, False, NETWORKS['main'])
MULTISIG_12_WORD_KEY = Key(TEST_12_WORD_MNEMONIC, True, NETWORKS['main'])
    
SPECTER_SINGLEKEY_WALLET_DATA = '{"label": "Specter Singlekey Wallet", "blockheight": 0, "descriptor": "wpkh([55f8fc5d/84h/0h/0h]xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA/0/*)#9qx3vqss", "devices": [{"type": "other", "label": "Key1"}]}'
SPECTER_MULTISIG_WALLET_DATA = '{"label": "Specter Multisig Wallet", "blockheight": 0, "descriptor": "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/0/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/0/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/0/*))#3nfc6jdy", "devices": [{"type": "other", "label": "Key1"}, {"type": "other", "label": "Key2"}, {"type": "other", "label": "Key3"}]}'

def test_mnemonic(mocker):
    from krux.pages.home import Home
    from krux.wallet import Wallet

    cases = [
        # No print prompt
        (Wallet(SINGLEKEY_12_WORD_KEY), None, [BUTTON_ENTER]),
        (Wallet(SINGLEKEY_24_WORD_KEY), None, [BUTTON_ENTER, BUTTON_ENTER]),
        # Print
        (Wallet(SINGLEKEY_12_WORD_KEY), MockPrinter(), [BUTTON_ENTER, BUTTON_ENTER]),
        (Wallet(SINGLEKEY_24_WORD_KEY), MockPrinter(), [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        # Decline to print
        (Wallet(SINGLEKEY_12_WORD_KEY), MockPrinter(), [BUTTON_ENTER, BUTTON_PAGE]),
        (Wallet(SINGLEKEY_24_WORD_KEY), MockPrinter(), [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE]),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(
                side_effect=case[2]
            )),
            wallet=case[0],
            printer=case[1]
        )
        home = Home(ctx)
        
        mocker.spy(home, 'display_mnemonic')
        mocker.spy(home, 'print_qr_prompt')
        
        home.mnemonic()
    
        home.display_mnemonic.assert_called_with(ctx.wallet.key.mnemonic)
        assert ctx.input.wait_for_button.call_count == len(case[2])
        home.print_qr_prompt.assert_called_with(ctx.wallet.key.mnemonic, FORMAT_NONE)
    
def test_public_key(mocker):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    
    cases = [
        # No print prompt
        (Wallet(SINGLEKEY_12_WORD_KEY), None, False, [BUTTON_ENTER, BUTTON_ENTER]),
        (Wallet(MULTISIG_12_WORD_KEY), None, True, [BUTTON_ENTER, BUTTON_ENTER]),
        # Print
        (Wallet(SINGLEKEY_12_WORD_KEY), MockPrinter(), False, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        (Wallet(MULTISIG_12_WORD_KEY), MockPrinter(), True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        # Decline to print
        (Wallet(SINGLEKEY_12_WORD_KEY), MockPrinter(), False, [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_PAGE]),
        (Wallet(MULTISIG_12_WORD_KEY), MockPrinter(), True, [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_PAGE]),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(
                side_effect=case[3]
            )),
            wallet=case[0],
            printer=case[1]
        )
        home = Home(ctx)
        
        mocker.spy(home, 'display_qr_codes')
        mocker.spy(home, 'print_qr_prompt')
        
        home.public_key()
    
        display_qr_calls = [mock.call(ctx.wallet.key.xpub_btc_core(), FORMAT_NONE, ctx.wallet.key.xpub(), DEFAULT_PADDING + 1)]
        print_qr_calls = [mock.call(ctx.wallet.key.xpub_btc_core(), FORMAT_NONE)]
        if case[2]:
            display_qr_calls.append(mock.call(ctx.wallet.key.p2wsh_zpub_btc_core(), FORMAT_NONE, ctx.wallet.key.p2wsh_zpub(), DEFAULT_PADDING + 1))
            print_qr_calls.append(mock.call(ctx.wallet.key.p2wsh_zpub_btc_core(), FORMAT_NONE))
        else:
            display_qr_calls.append(mock.call(ctx.wallet.key.p2wpkh_zpub_btc_core(), FORMAT_NONE, ctx.wallet.key.p2wpkh_zpub(), DEFAULT_PADDING + 1))
            print_qr_calls.append(mock.call(ctx.wallet.key.p2wpkh_zpub_btc_core(), FORMAT_NONE))
            
        home.display_qr_codes.assert_has_calls(display_qr_calls)
        assert ctx.input.wait_for_button.call_count == len(case[3])
        home.print_qr_prompt.assert_has_calls(print_qr_calls)
    
def test_wallet(mocker):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    
    cases = [
        # Don't load
        (False, SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, None, [BUTTON_PAGE]),
        # Load, good data, accept
        (False, SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, None, [BUTTON_ENTER, BUTTON_ENTER]),
        # Load, good data, decline
        (False, SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, None, [BUTTON_ENTER, BUTTON_PAGE]),
        # Load, bad capture
        (False, SINGLEKEY_12_WORD_KEY, None, None, [BUTTON_ENTER]),
        # Load, bad wallet data
        (False, SINGLEKEY_12_WORD_KEY, '{}', None, [BUTTON_ENTER, BUTTON_ENTER]),
        # No print prompt
        (True, SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, None, [BUTTON_ENTER]),
        # Print
        (True, SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, MockPrinter(), [BUTTON_ENTER, BUTTON_ENTER]),
        # Decline to print
        (True, SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, MockPrinter(), [BUTTON_ENTER, BUTTON_PAGE]),
        # Multisig wallet, no print prompt
        (True, MULTISIG_12_WORD_KEY, SPECTER_MULTISIG_WALLET_DATA, None, [BUTTON_ENTER]),
    ]
    for case in cases:
        wallet = Wallet(case[1])
        if case[0]:
            wallet.load(case[2], FORMAT_PMOFN)
            
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(
                side_effect=case[4]
            )),
            wallet=wallet,
            printer=case[3]
        )
        
        home = Home(ctx)
        mocker.patch.object(home, 'capture_qr_code', new=lambda: (case[2], FORMAT_PMOFN))
        mocker.patch.object(home, 'display_qr_codes', new=lambda data, qr_format, title=None, title_padding=10: ctx.input.wait_for_button())
        mocker.spy(home, 'print_qr_prompt')
        mocker.spy(home, 'capture_qr_code')
        mocker.spy(home, 'display_wallet')
        
        home.wallet()
        
        if case[0]:
            home.display_wallet.assert_called_once()
            if case[3] is not None:
                home.print_qr_prompt.assert_called_once()
        else:
            if case[4][0] == BUTTON_ENTER:
                home.capture_qr_code.assert_called_once()
                if case[2] is not None and case[2] != '{}':
                    home.display_wallet.assert_called_once()
        assert ctx.input.wait_for_button.call_count == len(case[4])

def test_scan_address(mocker):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    
    cases = [
        # Addresses belonging to the wallet
        # No print prompt
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, 'bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, False, 'bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        # Print
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, 'bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y', MockPrinter(), True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        # Decline to print
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, 'bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y', MockPrinter(), True, [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER]),
        (MULTISIG_12_WORD_KEY, SPECTER_MULTISIG_WALLET_DATA, True, 'bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        (MULTISIG_12_WORD_KEY, SPECTER_MULTISIG_WALLET_DATA, False, 'bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65', None, True, [BUTTON_ENTER]),
        (MULTISIG_12_WORD_KEY, SPECTER_MULTISIG_WALLET_DATA, True, 'bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65', MockPrinter(), True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER]),
        (MULTISIG_12_WORD_KEY, SPECTER_MULTISIG_WALLET_DATA, True, 'bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65', MockPrinter(), True, [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER]),
        
        # Addresses not belonging to the wallet
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, 'bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        (MULTISIG_12_WORD_KEY, SPECTER_MULTISIG_WALLET_DATA, True, 'bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ', None, True, [BUTTON_ENTER, BUTTON_PAGE]),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, 'bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        # No print prompt
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw', None, True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        # Print
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw', MockPrinter(), True, [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),
        # Decline to print
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, '3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw', MockPrinter(), True, [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]),

        # Invalid addresses
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, None, None, False, []),
        (SINGLEKEY_12_WORD_KEY, SPECTER_SINGLEKEY_WALLET_DATA, True, 'invalidaddress', None, False, []),
    ]
    for case in cases:
        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)
            
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(
                side_effect=case[6]
            )),
            wallet=wallet,
            printer=case[4]
        )
        
        home = Home(ctx)
        mocker.patch.object(home, 'capture_qr_code', new=lambda: (case[3], FORMAT_NONE))
        mocker.patch.object(home, 'display_qr_codes', new=lambda data, qr_format, title=None, title_padding=10: ctx.input.wait_for_button())
        mocker.spy(home, 'print_qr_prompt')
        mocker.spy(home, 'capture_qr_code')
        mocker.spy(home, 'display_qr_codes')
        
        home.scan_address()
        
        home.capture_qr_code.assert_called_once()
        if case[5]:
            home.display_qr_codes.assert_called_once()
            if case[4] is not None:
                home.print_qr_prompt.assert_called_once()

        assert ctx.input.wait_for_button.call_count == len(case[6])
