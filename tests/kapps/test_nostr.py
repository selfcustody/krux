import pytest
from . import create_ctx


def data():
    from kapps.nostr import MNEMONIC, HEX, NSEC, NPUB, PUB_HEX

    # Test vectors from NIP-06: https://github.com/nostr-protocol/nips/blob/master/06.md
    return [
        {
            MNEMONIC: "leader monkey parrot ring guide accident before fence cannon height naive bean",
            HEX: "7f7ff03d123792d6ac594bfa67bf6d0c0ab55b6b1fdb6249303fe861f1ccba9a",
            NSEC: "nsec10allq0gjx7fddtzef0ax00mdps9t2kmtrldkyjfs8l5xruwvh2dq0lhhkp",
            PUB_HEX: "17162c921dc4d2518f9a101db33695df1afb56ab82f5ff3e5da6eec3ca5cd917",
            NPUB: "npub1zutzeysacnf9rru6zqwmxd54mud0k44tst6l70ja5mhv8jjumytsd2x7nu",
        },
        {
            MNEMONIC: "what bleak badge arrange retreat wolf trade produce cricket blur garlic valid proud rude strong choose busy staff weather area salt hollow arm fade",
            HEX: "c15d739894c81a2fcfd3a2df85a0d2c0dbc47a280d092799f144d73d7ae78add",
            NSEC: "nsec1c9wh8xy5eqdzln7n5t0ctgxjcrdug73gp5yj0x03gntn67h83twssdfhel",
            PUB_HEX: "d41b22899549e1f3d335a31002cfd382174006e166d3e658e3a5eecdb6463573",
            NPUB: "npub16sdj9zv4f8sl85e45vgq9n7nsgt5qphpvmf7vk8r5hhvmdjxx4es8rq74h",
        },
    ]


def test_nostrkey(mocker, m5stickv):
    from kapps.nostr import NostrKey, MNEMONIC, HEX, NSEC, NPUB, PUB_HEX

    for n, t in enumerate(data()):
        print(n, t)
        for version in (MNEMONIC, HEX, NSEC):
            nkey = NostrKey()
            assert not nkey.is_loaded()
            if version == MNEMONIC:
                nkey.load_mnemonic(t[MNEMONIC])
            elif version == HEX:
                nkey.load_hex(t[HEX])
            elif version == NSEC:
                nkey.load_nsec(t[NSEC])

            assert nkey.is_loaded()

            if version in (HEX, NSEC):
                assert nkey.is_mnemonic() == False
            else:
                assert nkey.is_mnemonic()

            assert nkey.get_hex() == t[HEX]
            assert nkey.get_nsec() == t[NSEC]
            assert nkey.get_pub_hex() == t[PUB_HEX]
            assert nkey.get_npub() == t[NPUB]

        with pytest.raises(ValueError):
            nkey.load_hex(t[HEX][:-1])

        with pytest.raises(ValueError):
            nkey.load_nsec(t[NSEC][:-1])

        with pytest.raises(ValueError):
            nkey.load_nsec(t[NSEC].replace(NSEC, NPUB))


def test_nostrevent(mocker, m5stickv):
    from kapps.nostr import NostrEvent, NostrKey, MNEMONIC, HEX, NSEC
    import json

    event = r"""{
        "id": "a2d1bc19ed2bc8e09de9485d641fa53b89df75eecc042127dd2272d46afd6c8f",
        "pubkey": "17162c921dc4d2518f9a101db33695df1afb56ab82f5ff3e5da6eec3ca5cd917",
        "created_at": 1760632896,
        "kind": 1,
        "tags": [],
        "content": "t \" \\\r\n\r\nkkk",
        "sig": "17f972991755d25ec8d132b93fd1c0f59abba4c5fabd56274210e2bded9fe131ad294d73904f680bc18511a4e3a40660b2a67086179b332b0d2f670bed1c3c96"
    }"""

    event_dict = json.loads(event)

    # Remove the 'id' field
    event_dict.pop("id", None)

    # Dump back to JSON string
    event_without_id = json.dumps(event_dict, ensure_ascii=False)

    # Error event without necessary attribute
    pe = None
    with pytest.raises(ValueError):
        pe = NostrEvent.parse_event(event_without_id)
    assert pe is None

    pe = NostrEvent.parse_event(event)
    assert pe[NostrEvent.KIND] == 1

    se = NostrEvent.serialize_event(pe)

    # Event and its serialization OK
    assert NostrEvent.validate_id(pe, se)

    # signature tests
    data1 = data()[0]
    nkey = NostrKey()
    # with mnemonic
    nkey.load_mnemonic(data1[MNEMONIC])
    sig = NostrEvent.sign_event(nkey.get_private_key(), se)
    assert sig == pe["sig"]

    # with hex
    nkey.load_hex(data1[HEX])
    sig = NostrEvent.sign_event(nkey.get_private_key(), se)
    assert sig == pe["sig"]

    # with nsec
    nkey.load_nsec(data1[NSEC])
    sig = NostrEvent.sign_event(nkey.get_private_key(), se)
    assert sig == pe["sig"]

    # Mess with id
    pe[NostrEvent.ID] = pe[NostrEvent.ID].replace("1", "2")

    # Error comparing serialized_event with its id
    with pytest.raises(ValueError):
        NostrEvent.validate_id(pe, se)

    # other tests
    assert NostrEvent.get_kind_type(1) == NostrEvent.KIND_REGULAR
    assert NostrEvent.get_kind_desc(1) == NostrEvent.KIND_DESC[1]
    assert NostrEvent.get_tag(999999) == NostrEvent.UNKNOWN
