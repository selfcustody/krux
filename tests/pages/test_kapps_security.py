"""Generic security tests for the Kapps framework.

Encode the hardening requirements raised in the PR #485 review:
1. execute_flash_kapp re-verifies the app signature on every execution
   (menu path AND startup path) - flash content is never trusted from an
   earlier check.
2. Boot runs the startup kapp only after TC code / flash-hash verification,
   and never skips the SD firmware-update check.
3. Every kapp execution ends in a device restart, including startup kapps.
4. The kapp module is removed from sys.modules after execution.
5. A cryptographic failure during signature verification is an error, not an
   "unsigned app" (which would silently prompt for deletion).
6. Kapps are verified against dedicated trusted kapp signer keys (multiple
   supported, one per kapp maintainer), never the firmware signer key.
7. SD->flash install verifies the bytes actually written to flash (TOCTOU).
8. Oversized .mpy files are refused before being copied to flash.
9. Deleting an unsigned app also drops it from the startup apps file.
"""

import os
import sys

import pytest
from . import create_ctx

FILES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "files")


@pytest.fixture
def device(multiple_devices):
    """Generic device under test: parametrizes over all supported devices."""
    return multiple_devices


def _kapps(mocker, btn_seq=None):
    from krux.pages.kapps import Kapps

    mocker.patch("os.listdir", new=mocker.MagicMock(return_value=[]))
    ctx = create_ctx(mocker, btn_seq)
    return Kapps(ctx), ctx


def _allow_exec(mocker):
    mocker.patch("os.chdir", new=mocker.MagicMock())
    mocker.patch("sys.exit", new=mocker.MagicMock())


def test_execute_reverifies_signature_menu_path(device, mocker):
    """A bad signature at execution time must block the import (menu path)."""
    from krux.pages import MENU_CONTINUE
    from krux.input import BUTTON_ENTER

    kapps, ctx = _kapps(mocker, [BUTTON_ENTER, BUTTON_ENTER])
    _allow_exec(mocker)
    mocker.patch.object(kapps, "_verify_flash_kapp", return_value=False)
    import_spy = mocker.patch("builtins.__import__", side_effect=AssertionError)

    result = kapps.execute_flash_kapp("evil")

    assert result == MENU_CONTINUE
    assert not import_spy.called


def test_execute_reverifies_signature_startup_path(device, mocker):
    """The startup path (prompt=False) gets the same signature gate."""
    kapps, ctx = _kapps(mocker, [])
    _allow_exec(mocker)
    mocker.patch.object(kapps, "_verify_flash_kapp", return_value=False)
    import_spy = mocker.patch("builtins.__import__", side_effect=AssertionError)

    kapps.execute_flash_kapp("evil", prompt=False)

    assert not import_spy.called


def test_verify_flash_kapp_checks_sig_of_flash_file(device, mocker):
    """_verify_flash_kapp hashes the flash copy and checks its signature."""
    from krux.settings import FLASH_PATH

    kapps, ctx = _kapps(mocker, [])
    mocker.patch(
        "krux.firmware.sha256", new=mocker.MagicMock(return_value=b"\xab" * 32)
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"sigbytes"))
    valid = mocker.patch.object(kapps, "valid_signature", return_value=True)

    assert kapps._verify_flash_kapp("myapp")
    valid.assert_called_once_with(b"sigbytes", b"\xab" * 32)

    # missing signature file -> not valid, no crash
    mocker.patch("builtins.open", side_effect=OSError)
    assert not kapps._verify_flash_kapp("myapp")


def test_execute_forces_restart_even_on_startup(device, mocker):
    """After any kapp execution the device restarts (poisoned-state defense)."""
    kapps, ctx = _kapps(mocker, [])
    _allow_exec(mocker)
    mocker.patch.object(kapps, "_verify_flash_kapp", return_value=True)
    sys.path.append(FILES_DIR)
    shutdown = mocker.patch("krux.power.power_manager.shutdown")
    try:
        kapps.execute_flash_kapp("kapp", prompt=False)
    finally:
        sys.path.remove(FILES_DIR)

    assert shutdown.called


def test_execute_cleans_sys_modules(device, mocker):
    """The kapp module must not stay importable/patched after execution."""
    kapps, ctx = _kapps(mocker, [])
    _allow_exec(mocker)
    mocker.patch.object(kapps, "_verify_flash_kapp", return_value=True)
    mocker.patch("krux.power.power_manager.shutdown")
    sys.path.append(FILES_DIR)
    try:
        kapps.execute_flash_kapp("kapp", prompt=False)
    finally:
        sys.path.remove(FILES_DIR)

    assert "kapp" not in sys.modules


def test_crypto_error_is_not_unsigned(device, mocker):
    """Unexpected errors during verification must surface, not classify the
    app as unsigned (which would prompt the user to delete it)."""
    from krux.sd_card import MPY_FILE_EXTENSION

    kapps, ctx = _kapps(mocker, [])
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["app" + MPY_FILE_EXTENSION]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"sig"))
    mocker.patch.object(
        kapps, "valid_signature", side_effect=ValueError("Invalid public key")
    )

    with pytest.raises(ValueError, match="Invalid public key"):
        kapps.parse_all_flash_apps()


def test_missing_sig_file_is_unsigned(device, mocker):
    """A missing/unreadable signature file still counts as unsigned."""
    from krux.sd_card import MPY_FILE_EXTENSION
    from krux.input import BUTTON_ENTER

    kapps, ctx = _kapps(mocker, [BUTTON_ENTER])
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["app" + MPY_FILE_EXTENSION]),
    )
    mocker.patch("builtins.open", side_effect=OSError)
    mocker.patch("os.remove", new=mocker.MagicMock())
    removed = mocker.patch.object(kapps, "_remove_from_startup", new=mocker.MagicMock())

    assert kapps.parse_all_flash_apps() == []
    assert os.remove.called
    removed.assert_called_once_with("app")


def test_kapp_signer_keys_are_distinct(device, mocker):
    """Kapps verify against dedicated keys, never the firmware signer key.
    Multiple trusted keys are supported so different kapps can be signed by
    different maintainers; none of them may be the firmware key."""
    from krux.metadata import SIGNER_PUBKEY, KAPP_SIGNER_PUBKEYS

    assert SIGNER_PUBKEY not in KAPP_SIGNER_PUBKEYS

    kapps, ctx = _kapps(mocker, [])
    get_kapp_pubkeys = mocker.patch(
        "krux.firmware.get_kapp_pubkeys",
        return_value=[mocker.MagicMock(), mocker.MagicMock()],
    )
    # accepted when ANY trusted key signed it
    mocker.patch("krux.firmware.check_signature", side_effect=[False, True])
    assert kapps.valid_signature(b"sig", b"\x00" * 32)
    assert get_kapp_pubkeys.called

    # no keys provisioned: fail closed as an error, not "unsigned"
    mocker.patch("krux.firmware.get_kapp_pubkeys", return_value=[])
    with pytest.raises(ValueError, match="Invalid public key"):
        kapps.valid_signature(b"sig", b"\x00" * 32)


def test_sd_install_verifies_flash_copy(device, mocker):
    """TOCTOU: the bytes written to flash are re-hashed; a mismatch with the
    approved SD hash aborts the install before anything executes."""
    kapps, ctx = _kapps(mocker, [])

    assert kapps._flash_copy_matches(b"\x01" * 32, b"\x01" * 32)
    assert not kapps._flash_copy_matches(b"\x01" * 32, b"\x02" * 32)


def test_sd_load_size_cap(device, mocker):
    """An oversized .mpy is refused before any copy to flash."""
    from krux.pages.kapps import MAX_KAPP_SIZE
    from krux.pages import MENU_CONTINUE

    kapps, ctx = _kapps(mocker, [])
    mocker.patch(
        "krux.pages.utils.Utils.load_file",
        return_value=("big.mpy", None),
    )
    mocker.patch("os.stat", return_value=(0,) * 6 + (MAX_KAPP_SIZE + 1,) + (0,) * 3)
    flash_error = mocker.patch.object(kapps, "flash_error")

    assert kapps.load_sd_kapp() == MENU_CONTINUE
    assert flash_error.called


def test_sandbox_teardown_on_kapp_error(device, mocker):
    """The flash-import sandbox is always torn down (vfs closed, chdir /,
    module dropped) even when the kapp raises, so nothing it loaded survives."""
    import sys

    kapps, ctx = _kapps(mocker, [])
    fake_vfs = mocker.MagicMock()
    mocker.patch.dict("sys.modules", {"vfs": fake_vfs, "boomkapp": mocker.MagicMock()})
    chdir = mocker.patch("os.chdir")

    def boom(_module):
        raise RuntimeError("kapp exploded")

    with pytest.raises(RuntimeError, match="kapp exploded"):
        kapps._with_flash_kapp("boomkapp", boom)

    fake_vfs.exec_allowed.assert_any_call(False)  # import sandbox closed
    chdir.assert_any_call("/")  # back out of flash
    assert "boomkapp" not in sys.modules  # module dropped


def test_execute_rejects_non_kapp(device, mocker):
    """A signed .mpy without a callable run() is refused with a clear error,
    and the device still reboots afterwards."""
    from krux.input import BUTTON_ENTER

    kapps, ctx = _kapps(mocker, [BUTTON_ENTER])  # dismiss the error screen
    mocker.patch.object(kapps, "_verify_flash_kapp", return_value=True)
    mocker.patch("os.chdir")
    mocker.patch("sys.exit")
    shutdown = mocker.patch("krux.power.power_manager.shutdown")

    not_a_kapp = mocker.MagicMock()
    not_a_kapp.run = "not callable"
    mocker.patch.dict(
        "sys.modules", {"vfs": mocker.MagicMock(), "notakapp": not_a_kapp}
    )
    draw = mocker.spy(ctx.display, "draw_centered_text")

    kapps.execute_flash_kapp("notakapp", prompt=False)

    assert draw.called  # error surfaced to the user
    assert shutdown.called  # reboot still enforced


def test_add_to_startup_registers(device, mocker):
    """_add_to_startup adds the app to startup.json without dropping others."""
    import json

    kapps, ctx = _kapps(mocker, [])
    written = []
    handle = mocker.mock_open(read_data=json.dumps(["appa"]))
    handle.return_value.write.side_effect = lambda data: written.append(data)
    mocker.patch("builtins.open", handle)

    kapps._add_to_startup("appb")

    assert set(json.loads("".join(written))) == {"appa", "appb"}


def test_boot_order_startup_kapp_after_integrity_checks(device):
    """Startup kapp must run after TC/flash-hash verification, and the SD
    firmware-update check must not be skippable by a startup kapp."""
    boot_src = ""
    for candidate in ("src/boot.py", "../src/boot.py", "../../src/boot.py"):
        path = os.path.join(os.path.dirname(__file__), "..", "..", "src", "boot.py")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                boot_src = f.read()
            break
    assert boot_src, "src/boot.py not found"

    # Only look at the boot sequence, not the function definitions
    boot_seq = boot_src.split("# Boot initialization")[-1]
    update_pos = boot_seq.index("check_for_updates()")
    tc_pos = boot_seq.index("tc_code_verification(ctx)")
    kapp_pos = boot_seq.index("startup_kapp(ctx)")

    assert update_pos < kapp_pos, "firmware update check must precede startup kapp"
    assert tc_pos < kapp_pos, "TC verification must precede startup kapp"


def test_startup_cleanup_helper(device, mocker):
    """_remove_from_startup drops the app from startup.json."""
    import json

    kapps, ctx = _kapps(mocker, [])
    written = []

    handle = mocker.mock_open(read_data=json.dumps(["appa", "appb"]))
    handle.return_value.write.side_effect = lambda data: written.append(data)
    mocker.patch("builtins.open", handle)

    kapps._remove_from_startup("appa")

    assert written, "startup.json was not rewritten"
    assert json.loads("".join(written)) == ["appb"]


def test_invalid_signature_marks_flash_app_unsigned(device, mocker):
    """A present but invalid .mpy.sig goes through unsigned cleanup."""
    from krux.input import BUTTON_ENTER
    from krux.sd_card import MPY_FILE_EXTENSION
    from krux.settings import FLASH_PATH

    filename = "badapp" + MPY_FILE_EXTENSION
    kapps, ctx = _kapps(mocker, [BUTTON_ENTER])
    mocker.patch("os.listdir", return_value=[filename])
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"sig"))
    mocker.patch("krux.firmware.sha256", return_value=b"hash")
    mocker.patch.object(kapps, "valid_signature", return_value=False)
    remove = mocker.patch("os.remove")
    remove_startup = mocker.patch.object(kapps, "_remove_from_startup")

    assert kapps.parse_all_flash_apps() == []
    remove.assert_called_once_with("/%s/%s" % (FLASH_PATH, filename))
    remove_startup.assert_called_once_with("badapp")


def test_valid_signature_returns_false_when_no_key_matches(device, mocker):
    """valid_signature returns False after every trusted key rejects."""
    kapps, ctx = _kapps(mocker, [])
    mocker.patch("krux.firmware.get_kapp_pubkeys", return_value=["key1", "key2"])
    check = mocker.patch("krux.firmware.check_signature", return_value=False)

    assert kapps.valid_signature(b"sig", b"hash") is False
    assert check.call_count == 2


def test_sd_load_removes_flash_copy_when_written_hash_mismatches(device, mocker):
    """If the flash copy hash differs from the approved SD hash, delete it."""
    from krux.input import BUTTON_ENTER
    from krux.pages import MENU_CONTINUE
    from krux.pages.utils import Utils
    from krux.settings import FLASH_PATH

    filename = "newapp.mpy"
    kapps, ctx = _kapps(mocker, [BUTTON_ENTER, BUTTON_ENTER])
    mocker.patch.object(
        Utils,
        "load_file",
        new=lambda self, file_ext, prompt, only_get_filename: (filename, None),
    )
    mocker.patch("os.stat", return_value=(0,) * 10)
    mocker.patch("krux.firmware.sha256", side_effect=[b"approved", b"written"])
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"sig"))
    mocker.patch.object(kapps, "valid_signature", return_value=True)
    mocker.patch.object(kapps, "_flash_copy_matches", return_value=False)
    remove = mocker.patch("os.remove")
    flash_error = mocker.patch.object(kapps, "flash_error")
    execute = mocker.patch.object(kapps, "execute_flash_kapp")

    assert kapps.load_sd_kapp() == MENU_CONTINUE
    remove.assert_called_once_with("/%s/%s" % (FLASH_PATH, filename))
    flash_error.assert_called_once_with("Bad signature")
    execute.assert_not_called()


def test_register_startup_flag_only_registers_opted_in_kapp(device, mocker):
    """_register_startup_flag only persists apps with ALLOW_STARTUP."""
    kapps, ctx = _kapps(mocker, [])
    add = mocker.patch.object(kapps, "_add_to_startup")

    module = type("KappModule", (), {})()
    kapps._register_startup_flag(module, "app")
    add.assert_not_called()

    module.ALLOW_STARTUP = True
    kapps._register_startup_flag(module, "app")
    add.assert_called_once_with("app")
