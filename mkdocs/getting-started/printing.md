Krux has the ability to print all QR codes it generates, including mnemonic, xpub, wallet backup, and signed PSBT, via a locally-connected thermal printer over its serial port. Consult the [part list](../../parts) page for supported printers.

Note: Printers can come with different baudrates from the manufacturer. By default, Krux assumes the connected printer will have a baudrate of `9600`. If yours is different, you can override this by adding a `printer.baudrate.txt` file under `src/settings` with the correct rate, for example `19200`.

Once connected and powered on, all screens that display a QR code will begin showing a follow-up screen asking if you want to `Print to QR?`. You can use the middle button to confirm or the right-side button to cancel.

Originally, the idea was to print out a QR code of the BIP-39 mnemonic to enable faster wallet opening over the manual method of having to input each word. Then, we realized it would be useful to backup a wallet's multisig configuration on paper as well since you need knowledge of all xpubs in a multisig wallet in order to spend from it. After that, we decided to just make it a feature across the board. Want to make a "multisig paper wallet" with codes for your mnemonic, xpub, and multisig wallet on one sheet? You can! Want to print out a signed PSBT and send it in the mail? You can!

Just be careful what you do with the codes, since most smartphones can now quickly and easily read QR codes. Treat your QR mnemonic the same way you would treat a plaintext copy of it.