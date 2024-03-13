### Send coins
Go to the *Send* screen, fill in the recipient address, amount, and any extra information you wish to supply, and click the blue *Create Transaction* button.

<img src="../../../img/sparrow/create-transaction-screen-600.png">

On the next screen, make sure that the *Signing Wallet* is the one you created and that the *Sighash* is set to *All*. Click the blue *Finalize Transaction for Signing* button.

<img src="../../../img/sparrow/finalize-transaction-600.png">

On the next screen, click *Show QR* to make Sparrow display an animated QR code of the PSBT that you can scan with Krux by going to *Sign > PSBT > Load from camera* in its main menu.

<img src="../../../img/sparrow/show-qr-300.png">

After scanning, Krux should display info about the transaction for you to confirm before signing.

<img src="../../../img/maixpy_m5stickv/sign-psbt-sign-prompt-125.png">
<img src="../../../img/maixpy_amigo/sign-psbt-sign-prompt-150.png">

Once you have confirmed, Krux will begin animating a QR code of the signed transaction that you can scan into Sparrow. 

<img src="../../../img/maixpy_m5stickv/sign-psbt-signed-qr-125.png">
<img src="../../../img/maixpy_amigo/sign-psbt-signed-qr-150.png">

In Sparrow, click *Scan QR* and show it the QR. A progress bar will indicate how many parts of the QR have been read.