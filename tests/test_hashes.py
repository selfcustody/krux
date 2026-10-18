def test_sha256_uses_software_backend(mocker):
    from krux import hashes

    expected = object()
    sha256 = mocker.patch.object(hashes.hashlib, "sha256", return_value=expected)

    assert hashes.sha256(b"data") is expected
    sha256.assert_called_once_with(b"data")


def test_sha256d_uses_software_backend(mocker):
    from krux import hashes

    first_hash = mocker.Mock()
    first_hash.digest.return_value = b"first digest"
    second_hash = mocker.Mock()
    second_hash.digest.return_value = b"second digest"
    sha256 = mocker.patch.object(
        hashes.hashlib, "sha256", side_effect=[first_hash, second_hash]
    )

    assert hashes.sha256d(b"data") == b"second digest"
    assert sha256.call_args_list == [mocker.call(b"data"), mocker.call(b"first digest")]


def test_pbkdf2_hmac_sha256_uses_software_backend(mocker):
    from krux import hashes

    pbkdf2 = mocker.patch.object(
        hashes.hashlib, "pbkdf2_hmac", return_value=b"derived key"
    )

    assert hashes.pbkdf2_hmac_sha256(b"secret", b"salt", 1000) == b"derived key"
    pbkdf2.assert_called_once_with("sha256", b"secret", b"salt", 1000)


def test_sha256_hw_uses_hardware_backend(mocker, mp_modules):
    import sys
    from krux import hashes

    uhashlib_hw = sys.modules["uhashlib_hw"]
    expected = object()
    sha256 = mocker.patch.object(uhashlib_hw, "sha256", return_value=expected)

    assert hashes.sha256_hw(b"data") is expected
    sha256.assert_called_once_with(b"data")


def test_pbkdf2_hmac_sha256_hw_uses_hardware_backend(mocker, mp_modules):
    import sys
    from krux import hashes

    uhashlib_hw = sys.modules["uhashlib_hw"]
    pbkdf2 = mocker.patch.object(
        uhashlib_hw, "pbkdf2_hmac_sha256", return_value=b"derived key"
    )

    assert hashes.pbkdf2_hmac_sha256_hw(b"secret", b"salt", 1000) == b"derived key"
    pbkdf2.assert_called_once_with(b"secret", b"salt", 1000)
