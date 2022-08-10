Krux has support for creating 12- and 24-word mnemonics. Because true entropy is difficult to produce, especially with an embedded device, Krux outsources entropy generation to the user.

# Dice Rolls
At the start screen, once you select `New Mnemonic`, you will be taken to a second menu where you can choose to create a mnemonic via rolls of a D6 (standard six-sided die) or D20 (20-sided die). The number of dice rolls you choose determines the amount of words in the final mnemonic.

<img src="../../img/maixpy_m5stickv/new-mnemonic-options-125.png">
<img src="../../img/maixpy_amigo_tft/new-mnemonic-options-150.png">

## Via D6

<img src="../../img/maixpy_m5stickv/new-mnemonic-via-d6-roll-1-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/new-mnemonic-via-d6-roll-1-150.png" align="right">

The entropy in a single roll of a D6 is 2.585 bits ( log<sub>2</sub>(6) ); therefore 50 rolls will result in 128 bits of entropy, enough to generate a 12-word mnemonic. Doubling the amount of rolls doubles the entropy to 256 bits, resulting in a 24-word mnemonic.

<br><br><br><br>

## Via D20

<img src="../../img/maixpy_m5stickv/new-mnemonic-via-d20-roll-1-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/new-mnemonic-via-d20-roll-1-150.png" align="right">

Since a D20 has more possible outcomes, the entropy is increased per roll to 4.322 bits ( log<sub>2</sub>(20) ). This means that only 30 rolls are necessary to create a 12-word mnemonic and 60 rolls for a 24-word mnemonic.

<br><br><br><br>

## How it works

<img src="../../img/maixpy_m5stickv/new-mnemonic-via-d6-roll-string-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/new-mnemonic-via-d6-roll-string-150.png" align="right">

Krux keeps track of every roll you enter and displays the cumulative string of outcomes after each roll. 

<br><br><br><br>
<br><br><br><br>

<img src="../../img/maixpy_m5stickv/new-mnemonic-via-d6-roll-sha256-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/new-mnemonic-via-d6-roll-sha256-150.png" align="right">

When you have entered your final roll, Krux will hash this string using SHA256 and output the resulting hash to the screen so that you can verify it for yourself.

Krux then takes this hash, runs [`unhexlify`](https://docs.python.org/3/library/binascii.html#binascii.unhexlify) on it to encode it as bytes, and deterministically converts it into a mnemonic according to the [BIP-39 Reference Implementation](https://github.com/trezor/python-mnemonic/blob/6b7ebdb3624bbcae1a7b3c5485427a5587795120/src/mnemonic/mnemonic.py#L189-L207).

Note: For 12-word mnemonics, only the first half of the SHA256 hash is used (128 bits), while 24-word mnemonics use the full hash (256 bits).

<br><br><br><br>

# Alternatives
See [here](https://vault12.rebelmouse.com/seed-phrase-generation-2650084084.html) for a good method to generate a mnemonic manually, or visit [Ian Coleman's BIP-39 Tool](https://iancoleman.io/bip39/) offline or on an airgapped device to generate one automatically. 

It's worth noting that Ian's tool is able to take a mnemonic and generate a QR code that Krux can read in via the QR input method mentioned on the next page.

