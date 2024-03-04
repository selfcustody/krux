This guide assumes you have already created a mnemonic. If that is not the case, head over to the [Generating a Mnemonic](generating-a-mnemonic.md) page and complete those steps first.

When entering your mnemonic into Krux, make sure to select `Single-sig` before proceeding. The choice of `Single-sig` vs. `Multisig` at this point will change the derivation path used to generate your master extended public key (xpub) which will affect how wallet software handles it.

<img src="../../../img/maixpy_m5stickv/load-mnemonic-seq-single-multi-125.png">
<img src="../../../img/maixpy_amigo/load-mnemonic-seq-single-multi-150.png">

Selecting `Single-sig` will derive an xpub using the derivation path `m/84'/0'/0'` on mainnet and `m/84'/1'/0'` on testnet, which indicates to wallet software that a [Segregated Witness (Segwit) script type](https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki) should be used. For single-sig wallets, this script is `P2WPKH`, or just `wpkh`.

**Note:** The load of the `Wallet Descriptor` step is unnecessary for signing PSBTs with Single-sig wallets since the script type (`wpkh`) and key are already known. However, this can be useful if you wish to [print a backup](../features/printing.md) of the wallet or want an additional sanity check.

## Specter Desktop
### Create the wallet
In Specter Desktop, you will need to import your public key by adding a new device. Press the *Add new device* button on the left side of the app.

<img src="../../../img/specter/add-new-device-button-400.png">

Krux is not listed as one of the available device types on the *Add Device* screen, so you will need to select the *Other* option.

<img src="../../../img/specter/select-device-type-screen-600.png">

You will be taken to the *Upload Keys* screen where you can choose to *Scan QR code*.

<img src="../../../img/specter/upload-keys-screen-600.png">

On your Krux, navigate to the *Extended Public Key* option under the main menu and show the **first** QR code to Specter Desktop.

<img src="../../../img/maixpy_m5stickv/extended-public-key-wpkh-xpub-qr-125.png">
<img src="../../../img/maixpy_amigo/extended-public-key-wpkh-xpub-qr-150.png">

It should import the xpub and display the *Purpose* as *#0 Single Sig (Segwit)*.

<img src="../../../img/specter/single-sig-segwit-key-600.png">

Give the device a name and press *Continue*. You should see the new device in the devices list on the left side of the app.

<img src="../../../img/specter/single-sig-demo-device-400.png">

After you've added a device with your key to Specter Desktop, you can make a wallet using it. Press the *Add new wallet* button on the left side of the app.

<img src="../../../img/specter/add-new-wallet-button-400.png">

Choose to create a *Single key wallet* when it asks which type of wallet you want on the following screen.

<img src="../../../img/specter/select-wallet-type-screen-singlesig-400.png">

Select the device you just added.

<img src="../../../img/specter/pick-device-screen-singlesig-400.png">

Give your wallet a name and make sure to select *Segwit* for the wallet type, then press *Create wallet*.

<img src="../../../img/specter/create-singlesig-wallet-screen-600.png">

Congrats, you just created a single-sig wallet with your key!

### Load the wallet into Krux
Load the wallet into Krux by going to the *Settings* page in Specter Desktop, then click the *Export* tab. There, press the *Export* button to display a QR code of your wallet.

<img src="../../../img/specter/export-wallet-screen-600.png">

----8<----
single-multi-wallet-descriptor.md
----8<----

<img src="../../../img/maixpy_m5stickv/wallet-wpkh-load-prompt-125.png">
<img src="../../../img/maixpy_amigo/wallet-wpkh-load-prompt-150.png">

### Receive coins
Navigate to the *Receive* screen where you should see a receive address that you can send funds to.

<img src="../../../img/specter/receive-address-screen-400.png">

### Send coins
Go to *Send* in Specter Desktop, fill in the recipient address, amount, and any extra information you wish to supply, and click *Create unsigned transaction*.

<img src="../../../img/specter/create-transaction-screen-600.png">

You will now see a screen listing the devices in your wallet. Select the device you want to sign the transaction (PSBT) with.

Specter Desktop will display an animated QR code of the PSBT that you can scan with Krux by going to *Sign > PSBT* in its main menu. After scanning, Krux should display info about the transaction for you to confirm before signing.

<img src="../../../img/maixpy_m5stickv/sign-psbt-sign-prompt-125.png">
<img src="../../../img/maixpy_amigo/sign-psbt-sign-prompt-150.png">

Once you have confirmed, Krux will begin animating a QR code of the signed transaction that you can scan into Specter Desktop. 

<img src="../../../img/maixpy_m5stickv/sign-psbt-signed-qr-125.png">
<img src="../../../img/maixpy_amigo/sign-psbt-signed-qr-150.png">

In Specter Desktop, click *Scan signed transaction* and show it the QR. Each part of the QR code that is read will receive a ghost icon to indicate progress.

<img src="../../../img/specter/scan-signed-transaction-button-400.png">

Once all parts of the QR code have been read, you should see a window popup asking you to broadcast the transaction. Click *Send transaction* and your transaction should be broadcasted to the network!

<img src="../../../img/specter/broadcast-transaction-screen-400.png">

Congratulations, you have learned how to send a transaction using Specter Desktop 🎉

## Sparrow
### Create the wallet
In Sparrow, create a new wallet by going to *File > New Wallet* and give it a name.

<img src="../../../img/sparrow/new-singlesig-wallet-400.png">

On the wallet screen, make sure to select a *Single Signature* policy type with the *Native Segwit (P2WPKH)* script type.

<img src="../../../img/sparrow/singlesig-wallet-settings-400.png">

----8<----
sparrow/import-xpub-sparrow.md
----8<----

<img src="../../../img/sparrow/keystore-singlesig-key-settings-600.png">

If everything looks right, click the blue *Apply* button to create your wallet.

Congrats, you just created a single-sig wallet with your key!

### Load the wallet output descriptor into Krux (optional)
Single-sig wallets don't need to perform this step, it is optional!
Load the wallet output descriptor into Krux by going to the *Settings* screen of the wallet in Sparrow, then click the :fontawesome-solid-qrcode: (QR code symbol) button at *Script Policy* section to the right of the *Descriptor:* to display a QR code that you can scan with Krux.

<img src="../../../img/sparrow/descriptor-singlesig-key-settings-600.png">

----8<----
sparrow/load-wallet-output-sparrow.md
----8<----

<img src="../../../img/maixpy_m5stickv/wallet-wpkh-load-prompt-125.png">
<img src="../../../img/maixpy_amigo/wallet-wpkh-load-prompt-150.png">

### Receive coins
Navigate to the *Receive* screen where you should see a receive address that you can send funds to.

<img src="../../../img/sparrow/singlesig-receive-address-600.png">

----8<----
sparrow/send-coins-sparrow.md
----8<----

Once all parts of the QR code have been read, you should see the signature bar fill and two new buttons appear. 
----8<----
sparrow/broadcast-sparrow.md
----8<----

## BlueWallet
### Create the wallet
In BlueWallet, create a new wallet by either pressing the *+* button or scrolling to the right until you see the *Add now* button.

<img src="../../../img/blue/add-wallet-button-400.png" style="border: 1px solid;">

On the screen that pops up, tap *Import wallet* to import your public key. 

<img src="../../../img/blue/add-wallet-400.png" style="border: 1px solid;">

On the following screen, tap *Scan or import a file* and it will begin trying to scan a QR code. 

<img src="../../../img/blue/import-wallet-400.png" style="border: 1px solid;">

On your Krux, navigate to the *Extended Public Key* option under the main menu and **make sure to show the second, zpub QR code** to BlueWallet.

<img src="../../../img/maixpy_m5stickv/extended-public-key-wpkh-zpub-qr-125.png">
<img src="../../../img/maixpy_amigo/extended-public-key-wpkh-zpub-qr-150.png">

It should import the key and create a watch-only wallet. From here, you can send or receive.

<img src="../../../img/blue/singlesig-wallet-home-400.png" style="border: 1px solid;">

Congrats, you just created a single-sig wallet with your key!

### Load the wallet into Krux
Load the wallet into Krux by tapping the ellipsis in the top-right to see the wallet settings.

<img src="../../../img/blue/singlesig-wallet-home-400.png" style="border: 1px solid;">

From here, tap *Export/Backup* in order to display a QR code of your wallet.

<img src="../../../img/blue/export-singlesig-wallet-400.png" style="border: 1px solid;">

----8<----
single-multi-wallet-descriptor.md
----8<----

<img src="../../../img/maixpy_m5stickv/wallet-wpkh-load-prompt-125.png">
<img src="../../../img/maixpy_amigo/wallet-wpkh-load-prompt-150.png">

### Receive coins
Navigate to the *Receive* screen where you should see a receive address that you can send funds to.

<img src="../../../img/blue/receive-address-400.png" style="border: 1px solid;">

Note that you can verify the receive address belongs to your wallet by using the [Scan Address](navigating-the-main-menu.md/#scan-address) option.

### Send coins
Go to the *Send* screen, fill in the recipient address, amount, and any extra information you wish to supply, and tap *Next*.

<img src="../../../img/blue/send-400.png" style="border: 1px solid;">

You should see an animated QR code of the PSBT that you can scan with Krux by going to *Sign > PSBT* in its main menu.

After scanning, Krux should display info about the transaction for you to confirm before signing.

<img src="../../../img/maixpy_m5stickv/sign-psbt-sign-prompt-125.png">
<img src="../../../img/maixpy_amigo/sign-psbt-sign-prompt-150.png">

Once you have confirmed, Krux will begin animating a QR code of the signed transaction that you can scan into BlueWallet. 

<img src="../../../img/maixpy_m5stickv/sign-psbt-signed-qr-125.png">
<img src="../../../img/maixpy_amigo/sign-psbt-signed-qr-150.png">

Once all parts of the QR code have been read, you can then choose to broadcast the transaction, sending it to the network!

Congratulations, you have learned how to send a transaction using BlueWallet 🎉
