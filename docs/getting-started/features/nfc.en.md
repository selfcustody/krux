# NFC Card Storage

!!! danger "Proof of concept. Do not put real seeds on these cards."
    Not reviewed, not audited, no security review by anyone. Anything built for
    real use should start from the established practice for this problem — NFC
    tag security, key diversification instead of factory keys, replay and
    cloning resistance, and the physical threat model of a backup that answers
    any reader that comes near it. None of that is settled here.

Keeps [KEF-encrypted](encryption/encryption.md) seed backups and wallet output
descriptors on NFC cards, read and written through an external WS1850S module
(M5Stack RFID Unit 2). The card is a third destination alongside flash and SD:
same envelope, same password prompt, different medium.

**Off by default.** Nothing happens until **Settings → Hardware → NFC →
Enabled** is switched on.

## The air-gap question

Krux is an air-gapped signer and NFC is a radio, so the exposure is kept as
small as it can be made:

- The RF field is energized only inside the "hold a card to the reader" page,
  and drops on every exit path.
- The reader is attached to the I2C bus lazily, in that same page. With the
  toggle off the bus is never opened, so a module left plugged in is untouched
  rather than merely unused.
- Only the KEF envelope crosses the antenna. The payload is sealed before the
  reader is attached, and the reader is detached again before the decryption
  password is asked for.
- The module is external. Unplugged, the feature reports "NFC reader not found".

## Wiring

An [M5Stack RFID Unit 2 (WS1850S)](https://shop.m5stack.com/products/rfid-unit-2-ws1850s)
at I2C address `0x28`. Supply is **3.3 V**, not the 5 V the Grove connector is
nominally rated for — if a card reads unreliably, suspect the supply first.

`SDA Pin` and `SCL Pin` are settings, so no board file has to change. They
default to the board's TX and RX header pins (8 and 6 on Yahboom), which are
also the [thermal printer](printing/printing.md) pins — **a printer and a
reader cannot share them.** On those pins the reader gets its own I2C
controller; wired instead to the board's own `I2C_SDA`/`I2C_SCL`, it reuses the
existing bus, where `0x28` does not collide with the touch controller or PMU.

Check the wiring with **Tools → Device Tests → NFC Reader**, which probes the
bus and detaches again without energizing the antenna.

## What a card can hold

| Record | Written from | Read from |
|--------|--------------|-----------|
| Encrypted mnemonic | Backup → Encrypted → Store on NFC Card | Load Mnemonic → From NFC Card |
| Wallet output descriptor | Wallet Descriptor → Plaintext or Encrypted | Wallet Descriptor → Load from NFC card |
| Datum | Tools → Datum Tool → Store on NFC Card | Tools → Datum Tool → From NFC Card |
| Extended public key | Extended Public Key → *version* → Text → Store on NFC Card | Tools → Datum Tool |

Each record carries a type byte, and a reader asks for the type it can parse, so
a descriptor card offered to the mnemonic loader — or a seed card offered to the
wallet — reads as an empty card. Overwriting still warns for either, because the
question "is something already here" is asked without a type.

A descriptor record holds either a sealed envelope or a bare descriptor, exactly
as a `.txt` on an SD card may; Krux tells them apart on read. **A mnemonic
record is always sealed.** The mnemonic loader accepts nothing else, and no part
of Krux writes a seed to a card in the clear.

An extended public key card carries the same key expression the `.pub` file and
the QR code from that page carry, and carries it in the clear as they do. It
needs no checksum because nothing consumes it automatically — a descriptor card
is read straight into a wallet, so a flipped bit there has to be caught, while
an xpub card is read by a person. It is also not a descriptor: `parse_wallet`
refuses a bare key expression, so the separate type keeps it out of the wallet
loader rather than letting it fail deeper in. The privacy cost is the usual one
— an xpub is the account's whole history to anyone who waves a reader past it.

The [Datum Tool](../usage/tools.md) is the exception to the type discipline on
the read side: it opens any record Krux knows how to write, as the bytes it is,
because it is the inspection tool and refusing to show what is on a card its
owner is holding would be theatre. What it writes is still tagged as a datum, so
a datum card loads in neither the wallet nor the mnemonic loader. Its card
option sits behind the same gate as its SD card option — content that looks like
a mnemonic reaches neither.

### What a plaintext descriptor record costs

Two things the envelope was doing for free:

- **Privacy.** A descriptor holds every xpub in the wallet, which is its whole
  history, and an unsealed card gives it to any reader brought near it. Choose
  plaintext for a card the way you would choose it for a sheet of paper.
- **Authentication.** The on-card format has no checksum, by design: a sealed
  record is authenticated by its envelope, so a half-written or decaying card
  fails to decrypt rather than returning damaged bytes. An unsealed record has
  to bring its own, so Krux writes it with its **BIP-380 checksum and refuses a
  card without a matching one**.

  The checksum is verified by Krux, not by the descriptor parser: embit accepts
  a descriptor whether or not its checksum agrees. That matters more than it
  sounds. Only the xpubs carry integrity of their own, being base58check — a
  flipped bit in a fingerprint, a derivation path, the threshold or the script
  wrapper is accepted in silence and points the wallet at different addresses.

Size is the remaining limit either way. A 2-of-3 is about 450 bytes plaintext
and a taproot miniscript can pass 880, against a payload ceiling of 704. Sealing
deflates before it encrypts — roughly 345 and 470 — so a large descriptor may
fit encrypted and not fit plaintext. A card that cannot hold it says so.

## Erasing a card

**Tools → Erase NFC Card** zeroes every data block on the card, after asking to
see the card, confirming, and asking to see it again.

It wipes the whole data area rather than just the record header, and the
difference matters. A card whose header is gone reads as blank to Krux, but the
KEF envelope is still lying on it — and an envelope carried off a discarded
backup can be attacked offline for as long as its password holds. Erasing the
header is reuse, not destruction.

The wipe reaches past the record ceiling too. No record can occupy the last two
data blocks, but the ceiling bounds what Krux will allocate for a stranger's
card, not what is written on this one.

Sector trailers and block 0 are never written, so this cannot brick a sector —
and for the same reason it **cannot rescue an NDEF-formatted card**. Those use
different sector keys, so Krux cannot authenticate to them at all; restoring one
means rewriting its trailers, which any tag tool will do.

## Supported tags

| Family | SAK | Usable bytes |
|--------|-----|--------------|
| MIFARE Classic 1K | `0x08`, `0x88` | 752, capped at 720 |

A KEF-wrapped 24-word seed is under 100 bytes, so every supported tag has room
to spare. Any other SAK reads as an empty field.

Classic sectors use the factory key A (`FF FF FF FF FF FF`). The protection is
the KEF password, not the sector key — the card stays readable by any reader,
and what a reader finds is ciphertext. A tag that has been **NDEF-formatted no
longer uses the factory key** and will read as if it held no backup; erasing it
with any tag tool restores it, destroying whatever NDEF content it shipped with.

## Interoperability with Kern

The record magic tags the format, not the device, so a card written by Krux
reads on the [Kern](https://github.com/sandman21vs/Kern) NFC branch and vice
versa. Every layer that matters is shared: the 16-byte record header, the tag
addressing, the KEF envelope and its version numbers, and a plaintext of raw
BIP39 entropy. `tests/test_nfc.py` pins the header bytes with a golden vector —
without it a refactor could split the two firmwares silently, since both would
stay self-consistent and only a card handed between devices would show it.

## The card is treated as hostile

Every byte comes from whoever handed the user the card, so parsing is an
allowlist and nothing is allocated before the header passes. The reader refuses
a reply that does not fit rather than truncating it (the classic MFRC522
overflow); selection allowlists SAK and checks BCC, and capacity comes from that
allowlist rather than from anything the card claims; writes to block 0 and
sector trailers are refused, because a corrupted trailer bricks its sector
permanently.

Decryption is not acceptance. A KEF version with a 16-bit hidden auth lets a
wrong password through about once in 65536 tries, and a planted card can carry
a password its author chose, so what comes out still has to get past a gate —
and it is the same gate the same data faces arriving by QR code or SD card. For
a mnemonic that is raw BIP39 entropy, 16 or 32 bytes. For a descriptor it is the
descriptor parser, which also decides whether the loaded key is a cosigner. NFC
adds a medium, never a parser and never a shortcut past one.

**What this does not protect against:** a planted card the user accepts, with a
password they get right, loads the attacker's seed. That is the same exposure as
a malicious QR code, and the same defence applies — the fingerprint confirmation
screen before the key is used.
