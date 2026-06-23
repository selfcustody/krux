import pytest
from io import BytesIO

TEST_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


def build_v2_psbtx():
    from embit.psbt import PSBT

    P2WPKH_PSBT = b'psbt\xff\x01\x00q\x02\x00\x00\x00\x01\xcf<X\xc3)\x82\xae P\x88\xd9\xbdI\xeb\x9b\x02\xac\xdfM=\xaev\xa5\x16\xc6\xb3\x06\xb1]\xe3\xa1N\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x02|?]\x05\x00\x00\x00\x00\x16\x00\x14/4\xaa\x1c\xf0\nS\xb0U\xa2\x91\xa0:}E\xf0\xa6\x98\x8bR\x80\x96\x98\x00\x00\x00\x00\x00\x16\x00\x14\xe6j\xfe\xff\xc3\x83\x8eq\xf0\xa2{\x07\xe3\xb0\x0e\xdej\xe8\xe1`\x00\x00\x00\x00\x00\x01\x01\x1f\x00\xe1\xf5\x05\x00\x00\x00\x00\x16\x00\x14\xd0\xc4\xa3\xef\t\xe9\x97\xb6\xe9\x9e9~Q\x8f\xe3\xe4\x1a\x11\x8c\xa1"\x06\x02\xe7\xab%7\xb5\xd4\x9e\x97\x03\t\xaa\xe0n\x9eI\xf3l\xe1\xc9\xfe\xbb\xd4N\xc8\xe0\xd1\xcc\xa0\xb4\xf9\xc3\x19\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00"\x02\x03]I\xec\xcdT\xd0\t\x9eCgbw\xc7\xa6\xd4b]a\x1d\xa8\x8a]\xf4\x9b\xf9Qzw\x91\xa7w\xa5\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    psbt_v0 = PSBT.read_from(BytesIO(P2WPKH_PSBT))
    psbt_v0.version = 2
    return psbt_v0.serialize()


def test_psbtv2_parse():
    from embit.psbt import PSBT

    v2_data = build_v2_psbtx()
    psbt = PSBT.read_from(BytesIO(v2_data))

    assert psbt.version == 2
    assert psbt.tx_version is not None
    assert len(psbt.inputs) == 1
    assert len(psbt.outputs) == 2
    assert psbt.inputs[0].txid is not None
    assert psbt.inputs[0].vout == 0
    assert psbt.inputs[0].sequence is not None
    assert psbt.outputs[0].value is not None
    assert psbt.outputs[0].script_pubkey is not None
    assert psbt.outputs[1].value is not None
    assert psbt.outputs[1].script_pubkey is not None


def test_psbtv2_serialize_roundtrip():
    from embit.psbt import PSBT

    v2_data = build_v2_psbtx()
    psbt = PSBT.read_from(BytesIO(v2_data))

    serialized = psbt.serialize()
    psbt2 = PSBT.read_from(BytesIO(serialized))

    assert psbt2.version == 2
    assert psbt2.tx_version == psbt.tx_version
    assert psbt2.locktime == psbt.locktime
    assert len(psbt2.inputs) == len(psbt.inputs)
    assert len(psbt2.outputs) == len(psbt.outputs)
    assert psbt2.inputs[0].txid == psbt.inputs[0].txid
    assert psbt2.inputs[0].vout == psbt.inputs[0].vout
    assert psbt2.inputs[0].sequence == psbt.inputs[0].sequence
    assert psbt2.outputs[0].value == psbt.outputs[0].value
    assert psbt2.outputs[0].script_pubkey.serialize() == psbt.outputs[0].script_pubkey.serialize()


def test_psbtv2_tx_property():
    from embit.psbt import PSBT

    v2_data = build_v2_psbtx()
    psbt = PSBT.read_from(BytesIO(v2_data))

    tx = psbt.tx
    assert tx.version == psbt.tx_version
    assert tx.locktime == psbt.locktime
    assert len(tx.vin) == 1
    assert len(tx.vout) == 2
    assert tx.vin[0].txid == psbt.inputs[0].txid
    assert tx.vin[0].vout == psbt.inputs[0].vout
    assert tx.vin[0].sequence == psbt.inputs[0].sequence
    assert tx.vout[0].value == psbt.outputs[0].value


def test_psbtv2_trim_preserves_version(m5stickv):
    from embit.psbt import PSBT
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE
    from embit.networks import NETWORKS

    v2_data = build_v2_psbtx()
    wallet = Wallet(Key(
        TEST_MNEMONIC,
        TYPE_SINGLESIG,
        NETWORKS["test"],
    ))

    signer = PSBTSigner(wallet, v2_data, FORMAT_NONE)
    assert signer.psbt.version == 2

    signer.sign(trim=True)

    assert signer.psbt.version == 2
    assert signer.psbt.tx_version is not None
    assert signer.psbt.locktime is not None
    assert signer.psbt.inputs[0].txid is not None
    assert signer.psbt.inputs[0].vout is not None
    assert signer.psbt.inputs[0].sequence is not None
    assert signer.psbt.outputs[0].value is not None
    assert signer.psbt.outputs[0].script_pubkey is not None
    assert signer.psbt.outputs[1].value is not None
    assert signer.psbt.outputs[1].script_pubkey is not None


def test_psbtv2_trim_serializes_v2(m5stickv):
    from embit.psbt import PSBT
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE
    from embit.networks import NETWORKS

    v2_data = build_v2_psbtx()
    wallet = Wallet(Key(
        TEST_MNEMONIC,
        TYPE_SINGLESIG,
        NETWORKS["test"],
    ))

    signer = PSBTSigner(wallet, v2_data, FORMAT_NONE)
    signer.sign(trim=True)

    serialized = signer.psbt.serialize()
    psbt_reparsed = PSBT.read_from(BytesIO(serialized))

    assert psbt_reparsed.version == 2
    assert psbt_reparsed.inputs[0].txid == signer.psbt.inputs[0].txid
    assert psbt_reparsed.outputs[0].value == signer.psbt.outputs[0].value


def test_psbtv0_trim_unchanged(m5stickv):
    from embit.psbt import PSBT
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE
    from embit.networks import NETWORKS

    P2WPKH_PSBT = b'psbt\xff\x01\x00q\x02\x00\x00\x00\x01\xcf<X\xc3)\x82\xae P\x88\xd9\xbdI\xeb\x9b\x02\xac\xdfM=\xaev\xa5\x16\xc6\xb3\x06\xb1]\xe3\xa1N\x00\x00\x00\x00\x00\xfd\xff\xff\xff\x02|?]\x05\x00\x00\x00\x00\x16\x00\x14/4\xaa\x1c\xf0\nS\xb0U\xa2\x91\xa0:}E\xf0\xa6\x98\x8bR\x80\x96\x98\x00\x00\x00\x00\x00\x16\x00\x14\xe6j\xfe\xff\xc3\x83\x8eq\xf0\xa2{\x07\xe3\xb0\x0e\xdej\xe8\xe1`\x00\x00\x00\x00\x00\x01\x01\x1f\x00\xe1\xf5\x05\x00\x00\x00\x00\x16\x00\x14\xd0\xc4\xa3\xef\t\xe9\x97\xb6\xe9\x9e9~Q\x8f\xe3\xe4\x1a\x11\x8c\xa1"\x06\x02\xe7\xab%7\xb5\xd4\x9e\x97\x03\t\xaa\xe0n\x9eI\xf3l\xe1\xc9\xfe\xbb\xd4N\xc8\xe0\xd1\xcc\xa0\xb4\xf9\xc3\x19\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00"\x02\x03]I\xec\xcdT\xd0\t\x9eCgbw\xc7\xa6\xd4b]a\x1d\xa8\x8a]\xf4\x9b\xf9Qzw\x91\xa7w\xa5\x18s\xc5\xda\nT\x00\x00\x80\x01\x00\x00\x80\x00\x00\x00\x80\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    wallet = Wallet(Key(
        TEST_MNEMONIC,
        TYPE_SINGLESIG,
        NETWORKS["test"],
    ))

    signer = PSBTSigner(wallet, P2WPKH_PSBT, FORMAT_NONE)
    assert signer.psbt.version is None

    signer.sign(trim=True)

    assert signer.psbt.version is None

    serialized = signer.psbt.serialize()
    psbt_reparsed = PSBT.read_from(BytesIO(serialized))
    assert psbt_reparsed.version is None
