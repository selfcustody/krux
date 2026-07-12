from .. import create_ctx

MNEMONIC_24 = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon art"
)


def _wallet():
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from embit.networks import NETWORKS

    return Wallet(Key(MNEMONIC_24, TYPE_SINGLESIG, NETWORKS["test"]))


def _page(mocker, wallet=None):
    """ThresholdBackup with a context whose buttons never run out."""
    from krux.pages.home_pages.threshold_backup import ThresholdBackup
    from krux.input import BUTTON_ENTER

    ctx = create_ctx(mocker, [], wallet=wallet)
    ctx.input.wait_for_button = mocker.MagicMock(return_value=BUTTON_ENTER)
    return ThresholdBackup(ctx), ctx


def test_deterministic_randfunc(mocker, m5stickv):
    from krux.pages.home_pages.threshold_backup import ThresholdBackup

    rf = ThresholdBackup._deterministic_randfunc(b"\x01" * 32)
    first = rf(8)
    # reproducible across fresh instances with the same entropy
    again = ThresholdBackup._deterministic_randfunc(b"\x01" * 32)(8)
    assert first == again
    # different entropy -> different stream
    assert ThresholdBackup._deterministic_randfunc(b"\x02" * 32)(8) != first
    # asking for more than one digest worth of bytes refills the stream
    assert len(ThresholdBackup._deterministic_randfunc(b"\x03" * 32)(40)) == 40


def test_split_generates_and_browses(mocker, m5stickv):
    from krux.pages import MENU_CONTINUE

    page, _ = _page(mocker, _wallet())
    # m=3 then n=2
    mocker.patch.object(page, "capture_from_keypad", side_effect=["3", "2"])
    mocker.patch.object(page, "prompt", return_value=True)
    browse = mocker.patch.object(page, "_browse_shares")

    assert page.split() == MENU_CONTINUE
    # _browse_shares received 3 shares
    shares = browse.call_args[0][0]
    assert len(shares) == 3
    assert browse.call_args[0][1] == 3


def test_split_cancel_at_params(mocker, m5stickv):
    from krux.pages import MENU_CONTINUE

    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", return_value="")  # cancel
    browse = mocker.patch.object(page, "_browse_shares")
    assert page.split() == MENU_CONTINUE
    browse.assert_not_called()


def test_split_decline_confirmation(mocker, m5stickv):
    from krux.pages import MENU_CONTINUE

    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", side_effect=["3", "2"])
    mocker.patch.object(page, "prompt", return_value=False)
    browse = mocker.patch.object(page, "_browse_shares")
    assert page.split() == MENU_CONTINUE
    browse.assert_not_called()


def test_choose_scheme_invalid_then_valid(mocker, m5stickv):
    page, _ = _page(mocker, _wallet())
    # m=9 (invalid) -> guidance -> m=3, n=2 (valid)
    mocker.patch.object(page, "capture_from_keypad", side_effect=["9", "2", "3", "2"])
    info = mocker.patch.object(page, "_info")
    scheme = page._choose_scheme(256)
    assert (scheme.n, scheme.m) == (2, 3)
    info.assert_called_once()


def test_browse_shares_saved_confirms(mocker, m5stickv):
    from krux.pages.home_pages.threshold_backup import ThresholdBackup
    from krux.pages import Menu, MENU_EXIT
    from krux.kurihara import KuriharaScheme

    page, _ = _page(mocker, _wallet())
    entropy = bytes(32)
    shares = KuriharaScheme(2, 3, 256).generate(
        entropy, ThresholdBackup._deterministic_randfunc(entropy)
    )
    mocker.patch.object(page, "display_mnemonic")
    # select the "I saved all shares" item (index == number of shares)
    mocker.patch.object(Menu, "run_loop", return_value=(len(shares), MENU_EXIT))
    confirm = mocker.patch.object(page, "prompt", return_value=True)
    page._browse_shares(shares, 3)
    confirm.assert_called_once()


def test_browse_shares_back_exits(mocker, m5stickv):
    from krux.pages.home_pages.threshold_backup import ThresholdBackup
    from krux.pages import Menu, MENU_EXIT
    from krux.kurihara import KuriharaScheme

    page, _ = _page(mocker, _wallet())
    entropy = bytes(32)
    shares = KuriharaScheme(2, 3, 256).generate(
        entropy, ThresholdBackup._deterministic_randfunc(entropy)
    )
    mocker.patch.object(page, "display_mnemonic")
    # autospec so the side effect can read the menu's own back_index
    mocker.patch.object(
        Menu,
        "run_loop",
        autospec=True,
        side_effect=lambda self, **kw: (self.back_index, MENU_EXIT),
    )
    prompt = mocker.patch.object(page, "prompt")
    page._browse_shares(shares, 3)
    prompt.assert_not_called()


def test_show_share_displays(mocker, m5stickv):
    from krux.pages.home_pages.threshold_backup import ThresholdBackup
    from krux.kurihara import KuriharaScheme
    from krux.pages import MENU_CONTINUE

    page, _ = _page(mocker, _wallet())
    entropy = bytes(32)
    shares = KuriharaScheme(2, 3, 256).generate(
        entropy, ThresholdBackup._deterministic_randfunc(entropy)
    )
    disp = mocker.patch.object(page, "display_mnemonic")
    assert page._show_share(shares[0], 3) == MENU_CONTINUE
    disp.assert_called_once()


def _make_shares(n, m):
    from krux.pages.home_pages.threshold_backup import ThresholdBackup
    from krux.kurihara import KuriharaScheme
    from embit.bip39 import mnemonic_to_bytes

    entropy = mnemonic_to_bytes(MNEMONIC_24)
    shares = KuriharaScheme(n, m, 256).generate(
        entropy, ThresholdBackup._deterministic_randfunc(entropy)
    )
    return shares, entropy


def _wire_recover(mocker, page, share_words, part_ids, m, n):
    """Drive capture_from_keypad (m, n, part_ids) and load_key (share words)."""
    mocker.patch.object(
        page, "capture_from_keypad", side_effect=[str(m), str(n)] + part_ids
    )
    pending = list(share_words)

    def fake_load_key():
        page.captured_words = pending.pop(0)

    mocker.patch.object(page, "load_key", side_effect=fake_load_key)


def test_restore_returns_mnemonic(mocker, m5stickv):
    from krux.kurihara import share_to_mnemonic

    page, _ = _page(mocker, _wallet())
    shares, _ = _make_shares(2, 3)
    words = [
        share_to_mnemonic(shares[0]).split(),
        share_to_mnemonic(shares[1]).split(),
    ]
    _wire_recover(mocker, page, words, ["1", "2"], m=3, n=2)
    assert page.restore() == MNEMONIC_24


def test_restore_cancel_params(mocker, m5stickv):
    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", return_value="")
    assert page.restore() is None


def test_restore_cancel_n(mocker, m5stickv):
    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", side_effect=["3", ""])
    assert page.restore() is None


def test_restore_invalid_params(mocker, m5stickv):
    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", side_effect=["9", "2"])
    info = mocker.patch.object(page, "_info")
    assert page.restore() is None
    info.assert_called_once()


def test_restore_cancel_part_id(mocker, m5stickv):
    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", side_effect=["3", "2", ""])
    assert page.restore() is None


def test_restore_cancel_word_entry(mocker, m5stickv):
    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", side_effect=["3", "2", "1"])

    def empty_load_key():
        page.captured_words = None

    mocker.patch.object(page, "load_key", side_effect=empty_load_key)
    assert page.restore() is None


def test_restore_length_mismatch(mocker, m5stickv):
    from krux.kurihara import share_to_mnemonic

    page, _ = _page(mocker, _wallet())
    shares, _ = _make_shares(2, 3)
    # second share is a 12-word mnemonic -> size mismatch
    twelve = (
        "abandon abandon abandon abandon abandon abandon "
        "abandon abandon abandon abandon abandon about"
    ).split()
    words = [share_to_mnemonic(shares[0]).split(), twelve]
    _wire_recover(mocker, page, words, ["1", "2"], m=3, n=2)
    info = mocker.patch.object(page, "_info")
    assert page.restore() is None
    info.assert_called_once()


def test_restore_reconstruct_failure(mocker, m5stickv):
    from krux.kurihara import share_to_mnemonic

    page, _ = _page(mocker, _wallet())
    shares, _ = _make_shares(2, 3)
    # same share twice -> rank-deficient -> reconstruct raises
    words = [
        share_to_mnemonic(shares[0]).split(),
        share_to_mnemonic(shares[0]).split(),
    ]
    _wire_recover(mocker, page, words, ["1", "1"], m=3, n=2)
    info = mocker.patch.object(page, "_info")
    assert page.restore() is None
    info.assert_called_once()


def test_load_key_from_words_hook(mocker, m5stickv):
    from krux.pages import MENU_EXIT

    page, _ = _page(mocker, _wallet())
    assert page._load_key_from_words(["a", "b"]) == MENU_EXIT
    assert page.captured_words == ["a", "b"]


def test_info_shows_message(mocker, m5stickv):
    page, ctx = _page(mocker, _wallet())
    page._info("hello")
    ctx.display.clear.assert_called()
    ctx.display.draw_centered_text.assert_called_once()


def test_choose_scheme_cancel_n(mocker, m5stickv):
    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", side_effect=["3", ""])
    assert page._choose_scheme(256) is None


# ----- integration wrappers -----


def test_backup_menu_threshold_split(mocker, m5stickv):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.pages.home_pages import threshold_backup as tb_mod
    from krux.pages import MENU_CONTINUE

    ctx = create_ctx(mocker, [], wallet=_wallet())
    split = mocker.patch.object(
        tb_mod.ThresholdBackup, "split", return_value=MENU_CONTINUE
    )
    assert MnemonicsView(ctx).threshold_split() == MENU_CONTINUE
    split.assert_called_once()


def test_login_restore_loads_recovered(mocker, m5stickv):
    from krux.pages.login import Login
    from krux.pages.home_pages import threshold_backup as tb_mod

    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    mocker.patch.object(tb_mod.ThresholdBackup, "restore", return_value=MNEMONIC_24)
    loaded = mocker.patch.object(login, "_load_key_from_words", return_value="LOADED")
    assert login.restore_from_threshold() == "LOADED"
    loaded.assert_called_once_with(MNEMONIC_24.split())


def test_login_restore_cancelled(mocker, m5stickv):
    from krux.pages.login import Login
    from krux.pages.home_pages import threshold_backup as tb_mod
    from krux.pages import MENU_CONTINUE

    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    mocker.patch.object(tb_mod.ThresholdBackup, "restore", return_value=None)
    assert login.restore_from_threshold() == MENU_CONTINUE


def test_login_load_key_returns_status(mocker, m5stickv):
    from krux.pages.login import Login
    from krux.pages import Menu

    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    # select a load source (index 0, not Back) -> load_key returns its status
    mocker.patch.object(Menu, "run_loop", return_value=(0, "STATUS"))
    assert login.load_key() == "STATUS"


def test_login_load_key_back(mocker, m5stickv):
    from krux.pages.login import Login
    from krux.pages import Menu, MENU_CONTINUE

    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    mocker.patch.object(
        Menu,
        "run_loop",
        autospec=True,
        side_effect=lambda self, **kw: (self.back_index, MENU_CONTINUE),
    )
    assert login.load_key() == MENU_CONTINUE


def test_e2e_split_3of5_then_restore(mocker, m5stickv):
    """End-to-end: split a seed 3-of-5, then rebuild it from any 3 shares."""
    from krux.kurihara import share_to_mnemonic
    from krux.key import Key, TYPE_SINGLESIG
    from embit.networks import NETWORKS

    # 1) SPLIT the wallet's mnemonic into 5 shares, threshold 3
    page, _ = _page(mocker, _wallet())
    mocker.patch.object(page, "capture_from_keypad", side_effect=["5", "3"])
    mocker.patch.object(page, "prompt", return_value=True)
    captured = {}
    mocker.patch.object(
        page,
        "_browse_shares",
        side_effect=lambda shares, m: captured.update(shares=shares, m=m),
    )
    page.split()
    assert captured["m"] == 5 and len(captured["shares"]) == 5

    # the 5 mnemonics the user would write down, one per share
    saved = {s.part_id: share_to_mnemonic(s) for s in captured["shares"]}

    # 2) RESTORE from ANY 3 of the 5 (here parts 1, 3 and 5), as if at login
    fresh, _ = _page(mocker, _wallet())
    chosen = [1, 3, 5]
    _wire_recover(
        mocker,
        fresh,
        [saved[i].split() for i in chosen],
        [str(i) for i in chosen],
        m=5,
        n=3,
    )
    recovered = fresh.restore()

    # 3) It is exactly the original wallet (same mnemonic AND same fingerprint)
    assert recovered == MNEMONIC_24
    original_fp = Key(MNEMONIC_24, TYPE_SINGLESIG, NETWORKS["test"]).fingerprint
    rebuilt_fp = Key(recovered, TYPE_SINGLESIG, NETWORKS["test"]).fingerprint
    assert rebuilt_fp == original_fp
