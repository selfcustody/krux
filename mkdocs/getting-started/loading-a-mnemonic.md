Once you have either a 12 or 24-word mnemonic, choose `Load Mnemonic` on Krux's start menu, and you will be presented with several input methods:

<img src="../../img/pic-input-methods.png" width="150">

## Input Methods
### Via Text
<img src="../../img/pic-text-input.png" width="100" align="right">

Enter each word of your BIP-39 mnemonic one at a time. Krux will attempt to autocomplete your word to speed up the process. 

On your 12th or 24th word, you can enter the special sentinel value `zzzzz` to have Krux generate the final word of your mnemonic for you. This is handy if you chose a manual method to generate your mnemonic and want the final word to be a valid checksum.

<br>

### Via Numbers
<img src="../../img/pic-number-input.png" width="100" align="right">

Enter each word of your BIP-39 mnemonic as a number from 1 to 2048 one at a time. You can use [this list](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt) for reference.

On your 12th or 24th word, you can enter the special sentinel value `99999` to have Krux generate the final word of your mnemonic for you. This is handy if you chose a manual method to generate your mnemonic and want the final word to be a valid checksum.

<br>

### Via Bits
<img src="../../img/pic-bit-input.png" width="100" align="right">

Enter each word of your BIP-39 mnemonic as an [11-bit bitstring](https://github.com/hatgit/BIP39-wordlist-printable-en/blob/master/BIP39-en-printable.txt) one at a time.

<br><br><br><br>

### Via QR
<img src="../../img/pic-qr-input.png" width="100" align="right">

It's unpleasant having to manually enter 12 or 24 words each time you want to use Krux. To remedy this you can instead use the device's camera to read a QR code containing the words (encoded as a single space-separated text string). You can either use an offline QR code generator for this (ideally on an airgapped device), or you can attach a thermal printer to your Krux and print out the mnemonic after opening your wallet via one of the manual methods first. Check out the [Printing section](../printing) for more information.

<br>

## Single-key or Multisig
<img src="../../img/pic-mnemonic.png" width="100" align="right">

Once you have entered your mnemonic, you will be presented with the full list of words to confirm.

<br><br><br><br><br><br>

<img src="../../img/pic-wallet-type.png" width="100" align="right">

After loading your mnemonic, you will be brought to a small menu asking if you want to use it as part of a `Single-key` or `Multisig` wallet.

Your choice here will subtly change the generated xpub that is used to set up your device in your wallet coordinator software. You can learn more about the difference in the following guides for using [single-key](../using-a-single-key-wallet) and [multisig](../using-a-multisig-wallet) wallets.

Now, onto the main menu...