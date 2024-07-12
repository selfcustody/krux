After creating a mnemonic, making a safe backup, and testing to recover your mnemonic, it's time to set up a coordinator.

Krux can work with multiple coordinator wallets. Popular options include:

- [Sparrow Wallet](https://www.sparrowwallet.com/) (desktop)

- [Specter Desktop](https://specter.solutions/) (desktop)

- [Nunchuk](https://nunchuk.io/) (mobile)

- [BlueWallet](https://bluewallet.io/) (mobile)


## Step 1: Install the Coordinator Wallet

Download and install the appropriate version of your chosen coordinator wallet for your device and operating system.

## Step 2: Create a New Wallet with Krux as a Signer

Depending on the coordinator, the steps to add Krux as a signer may vary slightly:

**Specter and Nunchuk Single-sig:** Add Krux as signer device, then create a wallet that uses it.

**Specter and Nunchuk Multisig:** Add Krux as signer device, add other devices, then create a wallet that uses them.

**Sparrow and BlueWallet**: Create a wallet (or vault in Blue Wallet) first, then add signer device(s).

1. Load a mnemonic and wallet in Krux.

<img src="../../../img/maixpy_amigo/load-mnemonic-seq-mnemonic-150.png">
<img src="../../../img/maixpy_amigo/load-mnemonic-seq-overview-150.png">
<img src="../../../img/maixpy_m5stickv/load-mnemonic-seq-mnemonic-125.png">
<img src="../../../img/maixpy_m5stickv/load-mnemonic-seq-overview-125.png">

2. On your coordinator, when presented with possible signer devices to add, choose Krux if available, otherwise choose "other" or even another QR code compatible signer. As Krux is compatible with many QR code formats, most of available alternatives should work.

3. When prompted by your coordinator to import signer's public key, access the "Extended Public Key" on Krux.

<img src="../../../img/maixpy_amigo/extended-public-key-selected-150.png">
<img src="../../../img/maixpy_m5stickv/extended-public-key-selected-125.png">

4. Export an XPUB (or YPUB, ZPUB, etc., based on the script type) as a QR code.

<img src="../../../img/maixpy_amigo/extended-public-key-xpub-qr-menu-selected-150.png">
<img src="../../../img/maixpy_amigo/extended-public-key-wsh-xpub-qr-150.png">
<img src="../../../img/maixpy_m5stickv/extended-public-key-xpub-qr-menu-selected-125.png">
<img src="../../../img/maixpy_m5stickv/extended-public-key-wsh-xpub-qr-125.png">

5. Scan this QR code with your coordinator.

6. Ensure the coordinator’s wallet attributes (policy type, script type, fingerprint, and derivation) match those in Krux.

## Step 3: Load and Backup Wallet Descriptor (Multisig Only)

1. In your coordinator, export the wallet descriptor containing information about the wallet and all cosigners:
    - Sparrow: "Descriptor"
    - Specter: "Export Wallet"
    - Nunchuk: "Export Wallet Configuration"
    - BlueWallet: "Export Coordination Setup"
2. Export the descriptor as a QR code or file.
3. On Krux, go to "Wallet" -> "Wallet Descriptor" to scan the descriptor QR code or load it via SD card.

<img src="../../../img/maixpy_amigo/wallet-load-prompt-150.png">
<img src="../../../img/maixpy_amigo/wallet-wsh-load-prompt-fingerprints-150.png">
<img src="../../../img/maixpy_amigo/wallet-wsh-load-prompt-xpubs-150.png">

<img src="../../../img/maixpy_m5stickv/wallet-load-prompt-125.png">
<img src="../../../img/maixpy_m5stickv/wallet-wsh-load-prompt-fingerprints-125.png">
<img src="../../../img/maixpy_m5stickv/wallet-wsh-load-prompt-xpubs-125.png">

4. If you access "Wallet" -> "Wallet Descriptor" again, you will be able to:
    - Check the wallet cosigners.
    - Save the descriptor on an SD card (useful if you initially loaded it from QR codes).

    It is crucial to have a backup of this descriptor to recover your wallet in case one of the cosigners is lost.

## Step 4: Verify Addresses

For single-sig or multisig (after loading a descriptor):

- Go to "Address" on Krux.

- List "Receive Addresses" and "Change Addresses" or use "Scan Address" to verify if addresses from your coordinator are matched by Krux.

<img src="../../../img/maixpy_m5stickv/list-address-receive-125.png">
<img src="../../../img/maixpy_amigo/list-address-receive-150.png">

## Step 5: Funding your Wallet

Once addresses are verified, send a small test amount to your wallet. Test signing and sending a transaction before adding more funds.

## Step 6: Sign PSBTs and Messages

### PSBTs

1. Create a transaction in your coordinator.

2. Export the transaction as a QR code.

3. On Krux, go to "Sign" -> "PSBT" -> "Load from camera".

4. Scan the animated QR code.

5. Verify the transaction details.

6. If correct, press "Sign to QR code".

7. Scan the signed transaction QR code back into the coordinator to broadcast it.

Alternatively, you can use an SD card:

Save the transaction as a file on an SD card. On Krux, go to "Sign" -> "PSBT" -> "Load from SD card" and "Sign to SD card". Load the signed transaction on the coordinator and broadcast it.

### Messages

Some coordinators, like Sparrow, allow you to sign messages linked to your wallet's addresses. Signing and verifying a message signature attests to the ownership of an address and serves as an additional test for your setup.

<img src="../../../img/maixpy_m5stickv/sign-message-at-address-prompt-125.png">
<img src="../../../img/maixpy_amigo/sign-message-at-address-prompt-150.png">