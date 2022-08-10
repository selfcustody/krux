def test_vars_exist(mocker, m5stickv):
    from krux import metadata

    getattr(metadata, "VERSION")
    getattr(metadata, "SIGNER_PUBKEY")
