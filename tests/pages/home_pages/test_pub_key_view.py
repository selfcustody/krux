from .. import create_ctx
from .test_home import tdata
import pytest

# Legacy
PBM_XPUB_SINGLESIG_LEGACY_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f2\xfa\xe1\x9f\xc0AD\xa3\x8eP@]y%\xd3\x17@]=\x1b]\xd7@]F\xf0\xa7\x97@AB\xdd,\x90@\x7fUUU_\xc0\x00`zV\xc0\x00i\x8f\xd36]\x80b\xd0]\xe5\x18\x80\x11\xaf\x1bD\xb9\x804S\x8a\xf9=@M\xec\xe2C\xb4\x00,|&QR\x00/F$\xc2p@\x12\xe6\xe7\xf7\xe0\x00y\x8c/\x86\xc2\x80\x08\x1eZ\xb1Q\x80Mwg\x10D\xc04Xz\x160\x00\x19\xd9\xec\xd4\xdb@Hh\xe4\xcdR@\x11\xf3\\E\xe5\x00\x18\xf2\x13$-@!\xe3\xe7\xa6q\x00\x1a\xb5\x06{\xe1\x00e\\%\xd5\x04\xc0b7\xbb\xa6\xa0\x00!\xb4;$\x86\x00\x00\x87zq\x19\x00G\r2QK\xc0\x1c%\xfb\x8a\xb2\x00Ac#\x10}@\x00vgcD\x80\x7fuz#V\x80A;\xd6\xf1\xc5@]$*\x04|\xc0]x{\xe3\xf5\xc0]\x19\x01\x86\xcc\x00A\x7f\xaf\xa7\xf4\x80\x7fT-BG\x80\x00\x00\x00\x00\x00\x00"
)

PBM_XPUB_SINGLESIG_LEGACY_QRCODE_86 = bytearray()

PBM_XPUB_MULTISIG_LEGACY_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fg\xc6$\x9f\xc0A*w\xd0P@]t\xc8\xb4\x17@]e\xad\xdcW@]A\x0fz\x17@A;kw\x90@\x7fUUU_\xc0\x00\x05\xe5J@\x00yh6\x92\xa7@|\xc5\xc8\x84\xd6@i\xb5`\xe77\x004\x83\x18\xa5\xcc\xc0%t\xbc|a\x80&\x0cyY3\xc0iKJd\xb7@Xi\x9bU\xe6\x00\x19v\x89\xc3\x0e\x80p\x1c\x94\xab`@9\xf7\xa095\x00&k\xa8\x96a\xc0\x03O8\xb3\xb1\x00\x0cv\x1c\x97\xfc@C.\x12\xb6k\x00\x06R\xd9d\xb8\x80\x1d\x15\xfd\x17\xc0\xc0\x10\xec\xdc\xd7\x90@#2?a\xba\xc0@\x1d\x07\x95\x0e\xc0;9\x95\xe9\xa4\x80\x02G\x17\x9b`\xc0CN\xa1y}\x00\x18U\xb4\x1f\x8b\x809\xe8\x7f\x17\xfe\x80\x00k\xd9\x85\xc6\x00\x7f.V\xd0\xd4\x80A\x14\xd5-D@]!\x0f\xda}\x80]y\xdb\xfe\xe4\xc0]g)Rq\xc0Ae\xda\x15\xe8\x80\x7f_5s\xea\x80\x00\x00\x00\x00\x00\x00"
)

# Nested
PBM_XPUB_SINGLESIG_NESTED_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7flI\xad\xdf\xc0A(&\x86\x10@]s\x1d\xa4\x97@]E\xc4\x9aW@]jQ\xe4\x17@A#J\x04\xd0@\x7fUUU_\xc0\x00(\xad\x9e\x00\x00ya\x1e\xb1\xe7@4\x11_\x82\x96@\x1b\x81G\x84'\x80~N\xcc\xb4L@\x17\xadC\xbe\xcd\x00\x14\x1c\xb0\xdc \xc0)X(Q\xfc@jhV\x9cf\x00\x13\x97\x03\xa1O\x80B_\x10\xe9 @\x15\xc6\xb1/%\x00t\x01`Zq\x80\x15\xb5>Q5\x00\x1a\x14\xfa\xef\xcd@\x19\x7f!\xe6S\x00*#\xdc\xa0\xb4\x80SSe\x92\x82\xc0Z7O\x05\x90\xc0%\xc0-4\x9a\xc0t\x0c\x83\xc5\x0e\x00\x0b\xa8\x8f!$\x80\x1e\xa4\xb5aK\xc0K}\xb4m6\x00\x10\xe4\xb8N\x8d\xc0%\t\xdcs\xfd@\x00Zz\"\xc6\x80\x7f\tf\xa2\xd4\x80A&\x85\xfd\xc4\xc0]\x05\xec\x9c}\xc0]xa\xdb\x84\x00]Bl\x15@\x00AI\x13\x08*\x80\x7f|\x1f\x89\xea\x80\x00\x00\x00\x00\x00\x00"
)

PBM_XPUB_MULTISIG_NESTED_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fyI\xf5\x1f\xc0As_B\x90@]l\xa2S\x17@]N\x9d\xad\x17@]\x16S'\x97@AxHA\xd0@\x7fUUU_\xc0\x00\x0c\xab\x8a\x80\x00g\x19\xcb\x9f\x8b\xc08\x1eD)u@-\xef\x83\x9cf@\x04\xc9\xfeG\xe6@\x0b\xee\x03\x10\"\x804W\xe4\xe6]\xc0{\x18\x86\xd9_\xc0:\xe9'Cz@!\xacM#A\x80\x1c\xea@\x1eu\xc0o\xbd\xc6\xca\x19@lHn\xda0\x80\x15\xd6/\xa0d\x80p\xe2\xca%=\xc0O[\x95\xfab\xc0x\xd8\xa2\x8f\xb2\x00I\x94\x05\xce\xe2@z\xd1\xd0-\x1e\x00\x03\x0e\xf2\xac\x10@\x00 \xe6\x1e\x02@S\xb2\xefd\xee@DSA\xaa\xad\x80\r\xd9\xf0\x8e`@\x04\xe1*^6\x80g`i,\xfe\x80\x00i\xc4\x9eE@\x7f\x1d\xd2\x8e\xd5@AHn\xdfF\x80]J9.\xfe\xc0]\n\xc8\xcb\t\x00]\x0e\xb4\xbf\xea\x80Aa\xeb\x07\xa6\xc0\x7fQ\xfd\xc6W\x80\x00\x00\x00\x00\x00\x00"
)

PBM_YPUB_SINGLESIG_NESTED_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f6\xd7\xc7\xdf\xc0Al\xd1\x1fP@]\t\x82\xc5\x17@]~\xf7|\x17@]+-\x16W@AN\xb6mP@\x7fUUU_\xc0\x00<\x1b\x85@\x00}\xce\xf48j\x80,\x05\x05\xdc\x96\xc0g3\x96}z\x00\x1c\xc9B\xd9\xfa@a\xbf\xc7\\\xed\xc0,\x91\xfe\x0e_@cm\xd28M\x80T8\x83\x98n\x00#\xbf\x01V!\x00.A\xf6\x9c\x96\x80A\x81\x85z\x05\x00:]\x93\xc8<\xc0[sOv\x87\x80*\xf5%\x97O@a0\xf4Y>\x80\x1au_\x84\xc2@A\x91G^\x01\xc0t\x88z\xae\xfd@[a\xb5i<\x80:\x15\x97\x85\x0e\x80G\xfd-\x1eM\xc0f\xd0W\xa1\xff\x00Q\xac\xb7\x195\x00V\t\x8e\x15b@_y0\x9e\x7f\x80\x00YG\xf0\xc6@\x7fU\xb6[\xd5\x80A\x11\x02\x10F\x00]^%n}@]e\xeb\x95\xe8\x80]E\xd4H\xf4\xc0Aa\x12\x9c\xa8\x80\x7fe\x87*\xb7\x00\x00\x00\x00\x00\x00\x00"
)

PBM_YPUB_MULTISIG_NESTED_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f\x158\x99\x9f\xc0An\xa4\xdcP@]@q\xcb\x17@]5\x7f\xcd\x97@]U\xca\x0f\x97@AR\xaa\\\x90@\x7fUUU_\xc0\x00X\xba\x92\xc0\x00i\x81\n\xf1]\x80~\"=b\x18@\x11\x0e=B\x99\x80\x02\x83\x8e!-@w\x94F\xe3\xb4\xc0T\xf8\x87e\xd1\x00M\xebP\xb4z@(*#o\xa2\x00\r&i\x03\xc0\x80<\xc7\xca\x95Q@}g\x020t@&\r\x7f\xdb\x10\x00ub\x86\xa2\xbf@T-B\xffs@}\x81*\x11\x91\x00t\xe7\x96e)@)&\xf2\x82r\x00b\xcd\x1f\x00\xe1\x00+\xfcu\xf74@B+\x7f\xfa\x80\x00\x05<i@\xee\x80\x00\x8e[\xef\xb9\x00_\x85'!@\xc0\x02\xec>\x9a\xf0\x80I\tN\xda\x7f\xc0\x00Ob\xe7D\x00\x7fG\r'V\x80A\x1b\xd7\xb8\xc5\x80]3\x04\x0c|\xc0]a5q\xf4\xc0]?g\xc2\xcd\x00Af\xfb+t\x80\x7f@\n\x14U\x80\x00\x00\x00\x00\x00\x00"
)

# Native
PBM_XPUB_SINGLESIG_NATIVE_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fHs\xa7\x1f\xc0Ak^&\xd0@]M\xee\xda\x17@]S\xb2\x13\x17@]\x18P7\x97@AkOa\x90@\x7fUUU_\xc0\x00!n\xca\xc0\x00g\x1e\xe3\xe0\x8b\xc0l\x02\xeb$u\x00Y8\xd5\xbev@|\x89b\x0f\xc6\x00a\xf4\r\xc2*\x80 \xc2h7~\xc0O\xd2\xa7\xcb,\xc0\x10U\xff\xc7~@\x19\x18o\x06\xc2\x800\xa9\x91\xa6u\xc0k\xfe\xa7\xbd\x19\xc0 @\xa2\xda0\x00\x0f\xa0\xb9\x06D\x00\x06\xd6\xc8\xc7\xbe\xc0\x13\\\xa3\x8a\x1b\xc0\x16\xd9\xf2\x02>\x00!\x82\x01\xa2c@l;\xd9\xb6\x1e\x80e\x18\x82\x8e0@f\xc4\xa7\xc3\x12@!\\JB\xae\x80|q\xd1\xbdL\x80\x05B\xf6\xfe-@\x18d\xb3Zz\x00\x7fm&\xe6\xfc\x00\x00pI\x9aE\x00\x7f\x1c\xe2\xcc\xd5@Ax\xf6\x86F@]f+P\xfe\x80]'@\x8c\n\x00]\x1f\xa7\xdb\xe9\x80Ay\xae\x9bV\xc0\x7fvo\x02d\x80\x00\x00\x00\x00\x00\x00"
)

PBM_ZPUB_SINGLESIG_NATIVE_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fY\xe2)\x1f\xc0AE\x1cS\xd0@]h\xbe\x8a\x17@]I\xf5\x1f\x17@]:\xeb\xbe\x97@AW\x19%\x90@\x7fUUU_\xc0\x00\x197\xce\xc0\x00g\x00b\x84\x8b\xc0\n\xf4\xab\xbcu\xc0w\xf8\xa7\xebv@D\x9dvG\xd6\x80\tuEV*@\\b\x90\x87E\xc0U\x91\xb2\xef-\xc0(\xc4{\x0f>@-}mf\xc3\x80lh\xc1\xb8u\x00/\xe8\x85\x8b9@(|s\x16\x00@\x19r\xefd,@\x12D\xd8\x06\x8f\xc0)\xdc\xc0\xacS\xc0@)\xf2\x86\xb2\x00+\xf1\xb5\x96\xe0@\x06\x18\xc2\x8e\x1e\x80c\x08\xd0\xce @R\x99\xa6\x832\x80\x13,}\x83\xa2@v\x03\xe1\xb4M\x80\x15\xb1\xe3\xbel@\x00%*B\xba\x00a\x18/\xc6\xff\x00\x00Nr\x98E\xc0\x7f\x0e\xe5\xfe\xd5@AU\xbb\x07F@]T\x0eB\xfe\x80]\x16\xe95\n\x00]-\xa3\xbb\xeb\x80AdvO\xe6\xc0\x7fp{\xea\xc7\x80\x00\x00\x00\x00\x00\x00"
)

PBM_XPUB_MULTISIG_NATIVE_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f@\xcf\x0f\xdf\xc0A22\xd2P@]^\xc0\xe8\x97@]w\xed\x1cW@]H\xeaT\x17@A%-4\xd0@\x7fUUU_\xc0\x00\x15\xb9\x86@\x00yA\xdb\xf2g@\x16\x0cM\x01\x96@A\x01\x02\xf3\x17\x80Z\x0f\xc1=\\\x00yE%8\xc9\x00@\xc8}\xed\xa0\xc0mVjG\xba@\x0c5R\\\xe2\x00##C\xe0N\x80\x18\x97\x1c\x8b \xc0)r\xb5\r%\x00\x1aH5\x16q\x00MoTR}\x00$\x88v\xe0\x8d@1\x1a!\xc4\x11\x00 \xc6\x89\xf0V\x80\x03\x17\xe4^\x03\xc0N\x84m^\x90\xc0k\xf6\x0bf\x8a\xc0~\x99\x87X.\x80#\xcaSg@\x80\x1c\xaf'\xce\xeb\xc0U%\xf6mp\x00\x16Ey\xce\x8b@-Y\xf2q\xff\xc0\x00A\\\x14\xc6@\x7f\x1cq\xd0\xd4\x00A\x0b\xd0\xf5\xc4@]\x16\xa1r}\xc0]tx\xe4\x87\x00]B\x18!B\x00Aa\x8e\\\x88\x80\x7f~r\x8d\xfa\x80\x00\x00\x00\x00\x00\x00"
)

PBM_ZPUB_MULTISIG_NATIVE_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fKI\xb1\xdf\xc0A+0\xf6P@]g\x888\x97@]o\xa5\xfaW@]D`]\x17@A\x16;t\x90@\x7fUUU_\xc0\x00$\xfdV\x80\x00yItR\xe7@|\xe2\xea\xf1\x96@o\xcfA\xb3'\x004FU|L\x00w/\xc5\xeb\xc1\x00j\xdbh\xc5\xf0\xc0Q\xf2xw\xb2@6)K\x04\"\x00]\xda\x16\x88\xcc\x80J|4Y \x80y\xc3\xa1\x0c%\x80\x04\xfc\xec\xc7a\xc0?\xef\x1eUu\x00X\x98\x0f\x9d\xde@+\xcfV\x90Z\x00\n\x16\x14$\xd0\x80\x7f?\xe9\xae\x02\xc0.\xb5p\xcc\x90@\x15\xa5m$\x9a\xc0&\xed\x12I>@} \xf7\xc5$\x00*\xee\x07z\xd8\xc0_\x90\x96\x19w\x00\x06Td\x1a\x8b@3\xe1T\xc9\xfd\xc0\x00SX\x96\xc6\x80\x7f\x0fv\x90\xd4\x80A\x06\x14l\xc4\x00]-u\xd0}\x80]~P\xd5\x85\x00]F|QB\x00AT\xd7\x14Z\x80\x7f@\x17\x07\xeb\x80\x00\x00\x00\x00\x00\x00"
)

# Taproot
PBM_XPUB_SINGLESIG_TAPROOT_QRCODE_43 = bytearray(
    b'P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f(~\xb5\xdf\xc0A{\xa5LP@]\x01\xd3\xc5\x17@]\x7f\xe1\x9fW@]\x17\\\x06\xd7@AL\xa0}\x10@\x7fUUU_\xc0\x00\x18\xde\x91\xc0\x00}\xdf\xe1Xj\x804\xace,\x96\x80;-\xa2\nJ\x00p\x19\x0e\xc4\xca@g\x15\xc57\x89\x00"r\x06"\xf4@A\x9f\xa3,2\x80Vh\xde\x08\xee\x00M\xe9\xc9:!\x00\x04\xea\xf7\x8c\x96@Y6\x93\x1d5\x00v]\x0bP,\x80sCc:\x8b\x80r\x97W\xcfo@I\xd0\x81)\x0e\x80\x1c\xc4S\x814@-q\xef\x1a\x83\xc0 \xc1V>\xfd\x00u\x05\xb6\x1a\x1c\x00\x0em\x96\xd4.\x00!\x96l8\t\x80|\xc1\x15\x05\xf4\x00O\xbf\xd3=5\x00L\xa9B\xc1\xac@[\xed\xe9\x1e\xff\x80\x00X>\xa0\xc6@\x7fA\xa68\xd5\x80A5\xc7@F\xc0]Wg\xd8}\xc0]gL\x9d\xe9\x80]C\xe28\xf4\xc0Ad\x9b\xdc\x1a\x80\x7fQ\x01*\x86\x00\x00\x00\x00\x00\x00\x00'
)

# Miniscript
PBM_XPUB_MINISCRIPT_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f@\xcf\x0f\xdf\xc0A22\xd2P@]^\xc0\xe8\x97@]w\xed\x1cW@]H\xeaT\x17@A%-4\xd0@\x7fUUU_\xc0\x00\x15\xb9\x86@\x00yA\xdb\xf2g@\x16\x0cM\x01\x96@A\x01\x02\xf3\x17\x80Z\x0f\xc1=\\\x00yE%8\xc9\x00@\xc8}\xed\xa0\xc0mVjG\xba@\x0c5R\\\xe2\x00##C\xe0N\x80\x18\x97\x1c\x8b \xc0)r\xb5\r%\x00\x1aH5\x16q\x00MoTR}\x00$\x88v\xe0\x8d@1\x1a!\xc4\x11\x00 \xc6\x89\xf0V\x80\x03\x17\xe4^\x03\xc0N\x84m^\x90\xc0k\xf6\x0bf\x8a\xc0~\x99\x87X.\x80#\xcaSg@\x80\x1c\xaf'\xce\xeb\xc0U%\xf6mp\x00\x16Ey\xce\x8b@-Y\xf2q\xff\xc0\x00A\\\x14\xc6@\x7f\x1cq\xd0\xd4\x00A\x0b\xd0\xf5\xc4@]\x16\xa1r}\xc0]tx\xe4\x87\x00]B\x18!B\x00Aa\x8e\\\x88\x80\x7f~r\x8d\xfa\x80\x00\x00\x00\x00\x00\x00"
)


@pytest.fixture
def mock_save_file(mocker):
    mocker.patch(
        "krux.pages.qr_view.SeedQRView.has_sd_card",
        return_value=True,
    )
    mocker.patch(
        "krux.pages.home_pages.pub_key_view.PubkeyView.has_sd_card", return_value=True
    )
    return mocker.patch("krux.pages.file_operations.SaveFile.save_file")


@pytest.fixture
def mock_seed_qr_view(mocker):
    return mocker.patch("krux.pages.qr_view.SeedQRView")


def test_public_key_show_text(mocker, m5stickv, tdata):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    cases = [
        # Case parameters: [Wallet, Button Sequence]
        # 0 - Singlesig - P2PKH - Show all text
        (
            Wallet(tdata.LEGACY1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 1 - Multisig - P2SH - Show all text
        (
            # Wallet(tdata.MULTISIG_12_WORD_KEY),
            Wallet(tdata.LEGACY1_MULTISIG_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 2 - Singlesig - P2SH_P2WPKH - Show all text
        (
            Wallet(tdata.NESTEDSW1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter to ZPUB/YPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 3 - Multisig - P2SH_P2WSH - Show all text
        (
            Wallet(tdata.NESTEDSW1_MULTISIG_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter to ZPUB/YPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 4 - Singlesig - P2WPKH - Show all text
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter to ZPUB/YPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 5 - Multisig - P2WSH - Show all text
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter to ZPUB/YPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 6 - Singlesig - P2TR - Show all text
        (
            Wallet(tdata.TAPROOT1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 7 - Miniscript - P2WSH - Show all text
        (
            Wallet(tdata.MINISCRIPT_NATIVESW1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 8 - Miniscript - P2TR - Show all text
        (
            Wallet(tdata.MINISCRIPT_TAPROOT1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - text
                BUTTON_PAGE,  # Move to Back
                BUTTON_ENTER,  # Press Back
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case: {n}")
        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        mocker.patch.object(ctx.display, "FONT_HEIGHT", 14)
        mocker.spy(ctx.display, "clear")
        mocker.spy(ctx.display, "draw_hcentered_text")

        pub_key_viewer.public_key()

        # Build expected `clear` and `draw_hcentered_text` calls
        clear_calls = []
        draw_text_calls = []

        clear_calls.append(mocker.call())
        draw_text_calls.append(
            mocker.call(
                "\n\n"
                + ctx.wallet.key.derivation_str(pretty=True)
                + "\n\n"
                + ctx.wallet.key.account_pubkey_str(None),
                offset_y=ctx.display.FONT_HEIGHT,
                info_box=True,
            ),
        )

        # Be sure that the display was cleared and show correct master pubkeys
        ctx.display.clear.assert_has_calls(clear_calls, any_order=True)
        ctx.display.draw_hcentered_text.assert_has_calls(
            draw_text_calls, any_order=True
        )

        assert ctx.input.wait_for_button.call_count == len(case[1])
        n += 1


def test_public_key_show_qrcode(
    mocker,
    m5stickv,
    tdata,
    mock_seed_qr_view,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.key import P2PKH, P2SH, P2SH_P2WPKH, P2SH_P2WSH, P2WPKH, P2WSH, P2TR
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import TYPE_MULTISIG, TYPE_MINISCRIPT

    cases = [
        # Case parameters: [Wallet, Button Sequence, Show XPUB, Show ZPUB, Show YPUB]
        # 0 - Singlesig - P2PKH - Show all QR codes
        (
            Wallet(tdata.LEGACY1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu,
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 1 - Singlesig - P2SH - Show all QR codes
        (
            Wallet(tdata.LEGACY1_MULTISIG_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu,
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 2 - Singlesig - P2SH_P2WPKH - Show all QR codes
        (
            Wallet(tdata.NESTEDSW1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 3 - Multisig - P2SH_P2WSH - Show all QR codes
        (
            Wallet(tdata.NESTEDSW1_MULTISIG_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 4 - Singlesig - P2WPKH - Show all QR codes
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 5 - Multisig - P2WSH - Show all QR codes
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR Code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 6 - Singlesig - P2TR - Show all QR codes
        (
            Wallet(tdata.TAPROOT1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu,
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 7 - Miniscript - P2WSH - Show all QR codes
        (
            Wallet(tdata.MINISCRIPT_NATIVESW1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu,
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
        # 8 - Miniscript - P2TR - Show all QR codes
        (
            Wallet(tdata.MINISCRIPT_TAPROOT1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR Code
                BUTTON_ENTER,  # Enter XPUB - QR Code
                BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
                BUTTON_PAGE_PREV,  # Move to Back to Menu,
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Leave the page
            ],
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case: {n}")
        n += 1
        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        pub_key_viewer.public_key()

        # Build expected QR view calls
        qr_view_calls = []

        # Show XPUB
        if case[0].key.script_type in (
            P2PKH,
            P2SH,
            P2SH_P2WPKH,
            P2SH_P2WSH,
            P2WPKH,
            P2WSH,
            P2TR,
        ):
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=ctx.wallet.key.key_expression(None),
                    title="XPUB",
                ),
            )

        # Show ZPUB
        if (
            case[0].key.script_type in (P2WPKH, P2WSH)
            and case[0].key.policy_type != TYPE_MINISCRIPT
        ):
            version = "Zpub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "zpub"
            zpub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=zpub,
                    title="ZPUB",
                ),
            )

        # Show YPUB
        if case[0].key.script_type in (P2SH_P2WPKH, P2SH_P2WSH):
            version = "Ypub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "ypub"
            ypub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=ypub,
                    title="YPUB",
                ),
            )

        mock_seed_qr_view.assert_has_calls(qr_view_calls, any_order=True)
        assert ctx.input.wait_for_button.call_count == len(case[1])


def test_public_key_save_text(
    mocker,
    m5stickv,
    tdata,
    mock_save_file,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.key import P2PKH, P2SH, P2SH_P2WPKH, P2SH_P2WSH, P2WPKH, P2WSH, P2TR
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import TYPE_MULTISIG, TYPE_MINISCRIPT

    cases = [
        # Case parameters: [Wallet, Button Sequence, Show XPUB, Show ZPUB, Show YPUB]
        # 0 - Singlesig - P2PKH - Save XPUB to SD card
        (
            Wallet(tdata.LEGACY1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 1 - Multisig - P2SH - Save XPUB to SD card
        (
            Wallet(tdata.LEGACY1_MULTISIG_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 2 - Singlesig - P2SH_P2WPKH - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.NESTEDSW1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter Save to SD card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 3 - Multisig - P2SH_P2WSH - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.NESTEDSW1_MULTISIG_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter Save to SD card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 4 - Singlesig - P2WPKH - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter Save to SD card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 5 - Multisig - P2WSH - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter ZPUB/YPUB - text
                BUTTON_ENTER,  # Enter Save to SD card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 6 - Singlesig - P2TR - Save XPUB to SD card
        (
            Wallet(tdata.TAPROOT1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 7 - Miniscript - P2WSH - Save XPUB to SD card
        (
            Wallet(tdata.MINISCRIPT_NATIVESW1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
        # 8 - Miniscript - P2TR - Save XPUB to SD card
        (
            Wallet(tdata.MINISCRIPT_TAPROOT1_KEY),
            [
                BUTTON_ENTER,  # Enter XPUB - Text
                BUTTON_ENTER,  # Enter Save to SD Card
                BUTTON_ENTER,  # Accept Save to SD Card
                BUTTON_PAGE_PREV,  # Move to Go
                BUTTON_ENTER,  # Press Go
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
        ),
    ]

    for case in cases:
        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        mocker.patch.object(ctx.display, "FONT_HEIGHT", 14)
        mocker.spy(ctx.display, "clear")
        mocker.spy(ctx.display, "draw_hcentered_text")

        pub_key_viewer.public_key()

        # Build expected QR view calls
        clear_calls = []
        draw_text_calls = []
        sd_card_save_calls = []

        clear_calls.append(mocker.call())

        # Show XPUB
        if case[0].key.script_type in (
            P2PKH,
            P2SH,
            P2SH_P2WPKH,
            P2SH_P2WSH,
            P2WPKH,
            P2WSH,
        ):
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(None),
                    "XPUB",
                    "XPUB",
                    "XPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        # Show ZPUB
        if (
            case[0].key.script_type in (P2WPKH, P2WSH)
            and case[0].key.policy_type != TYPE_MINISCRIPT
        ):
            version = "Zpub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "zpub"
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                    "ZPUB",
                    "ZPUB",
                    "ZPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        # Show YPUB
        if case[0].key.script_type in (P2SH_P2WPKH, P2SH_P2WSH):
            version = "Ypub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "ypub"
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                    "YPUB",
                    "YPUB",
                    "YPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        draw_text_calls.append(
            mocker.call(
                "\n\n"
                + ctx.wallet.key.derivation_str(pretty=True)
                + "\n\n"
                + ctx.wallet.key.account_pubkey_str(None),
                offset_y=ctx.display.FONT_HEIGHT,
                info_box=True,
            ),
        )

        mock_save_file.assert_has_calls(sd_card_save_calls, any_order=True)
        ctx.display.clear.assert_has_calls(clear_calls, any_order=True)
        ctx.display.draw_hcentered_text.assert_has_calls(
            draw_text_calls, any_order=True
        )
        assert ctx.input.wait_for_button.call_count == len(case[1])


def test_public_key_save_qr_codes_pbm_43(
    mocker,
    m5stickv,
    tdata,
    mock_save_file,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import (
        TYPE_SINGLESIG,
        TYPE_MULTISIG,
        TYPE_MINISCRIPT,
        P2PKH,
        P2SH,
        P2SH_P2WPKH,
        P2SH_P2WSH,
        P2WPKH,
        P2WSH,
        P2TR,
    )
    from krux.sd_card import PBM_IMAGE_EXTENSION

    cases = [
        # Case parameters: [Wallet, Button Sequence, XPUB, YPUB, ZPUB]
        # 0 - Singlesig - P2PKH - Save XPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.LEGACY1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press save QR Image,
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Press Back
            ],
            PBM_XPUB_SINGLESIG_LEGACY_QRCODE_43,
            None,
        ),
        # 1 - Multisig - P2SH - Save XPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.LEGACY1_MULTISIG_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press save QR Image,
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Press Back
            ],
            PBM_XPUB_MULTISIG_LEGACY_QRCODE_43,
            None,
        ),
        # 2 - Singlesig - P2SH_P2WPKH - Save XPUB/YPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.NESTEDSW1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            PBM_XPUB_SINGLESIG_NESTED_QRCODE_43,
            PBM_YPUB_SINGLESIG_NESTED_QRCODE_43,
        ),
        # 3 - Multisig - P2SH_P2WSH - Save XPUB/YPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.NESTEDSW1_MULTISIG_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            PBM_XPUB_MULTISIG_NESTED_QRCODE_43,
            PBM_YPUB_MULTISIG_NESTED_QRCODE_43,
        ),
        # 4 - Singlesig - P2WPKH - Save XPUB/YPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            PBM_XPUB_SINGLESIG_NATIVE_QRCODE_43,
            PBM_ZPUB_SINGLESIG_NATIVE_QRCODE_43,
        ),
        # 5 - Multisig - P2WSH - Save XPUB/YPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press Save QR Image
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move Back
                BUTTON_ENTER,  # Press Back to leave
            ],
            PBM_XPUB_MULTISIG_NATIVE_QRCODE_43,
            PBM_ZPUB_MULTISIG_NATIVE_QRCODE_43,
        ),
        # 6 - Singlesig - P2TR - Save XPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.TAPROOT1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press save QR Image,
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Press Back
            ],
            PBM_XPUB_SINGLESIG_TAPROOT_QRCODE_43,
            None,
        ),
        # 7 - Miniscript - P2WSH - Save XPUB to SD card in 43x43 PBM format
        (
            Wallet(tdata.MINISCRIPT_NATIVESW1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press save QR Image,
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Press Back
            ],
            PBM_XPUB_MINISCRIPT_QRCODE_43,
            None,
        ),
        # 8 - Miniscript - P2TR - Save XPUB to SD card in 43x43 PBM format
        # (it's equal to previous P2WSH Miniscript)
        (
            Wallet(tdata.MINISCRIPT_TAPROOT1_KEY),
            [
                BUTTON_PAGE,  # Move to XPUB - QR code
                BUTTON_ENTER,  # Enter XPUB - QR code
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 2),  # Move to Save QR Image
                BUTTON_ENTER,  # Press save QR Image,
                BUTTON_ENTER,  # Press 43x43 PBM
                *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
                BUTTON_ENTER,  # Press Back to Menu
                BUTTON_PAGE_PREV,  # Move to Back
                BUTTON_ENTER,  # Press Back
            ],
            PBM_XPUB_MINISCRIPT_QRCODE_43,
            None,
        ),
    ]

    n = 0
    for case in cases:
        print(f"Case: {n}")
        n += 1
        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)
        pub_key_viewer.public_key()

        # Build expected QR save calls
        sd_card_save_calls = []

        # Show XPUB for singlesig, multisig and Miniscript
        sd_card_save_calls.append(
            mocker.call(
                case[2],
                "XPUB",
                file_extension=PBM_IMAGE_EXTENSION,
                save_as_binary=True,
                prompt=False,
            )
        )

        # Show YPUB for singlesig/multisig nested segwit
        if (
            case[0].key.script_type in (P2SH_P2WPKH, P2SH_P2WSH)
            and case[0].key.policy_type != TYPE_MINISCRIPT
        ):
            sd_card_save_calls.append(
                mocker.call(
                    case[3],
                    "YPUB",
                    file_extension=PBM_IMAGE_EXTENSION,
                    save_as_binary=True,
                    prompt=False,
                )
            )

        # Show ZPUB for single and  multisig
        if (
            case[0].key.script_type in (P2WPKH, P2WSH)
            and case[0].key.policy_type != TYPE_MINISCRIPT
        ):
            sd_card_save_calls.append(
                mocker.call(
                    case[3],
                    "ZPUB",
                    file_extension=PBM_IMAGE_EXTENSION,
                    save_as_binary=True,
                    prompt=False,
                )
            )

        mock_save_file.assert_has_calls(sd_card_save_calls, any_order=True)
        assert ctx.input.wait_for_button.call_count == len(case[1])
