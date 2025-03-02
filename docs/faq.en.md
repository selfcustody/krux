## Is Krux a hardware wallet?
The term "hardware wallet" typically refers to devices dedicated to storing private keys and signing transactions. These devices often feature specific security components like secure element chips.

Krux was initially developed as a signer, operating exclusively in amnesic mode, which requires users to load their keys each time the device is powered on. However, Krux has evolved and now offers the option to store mnemonics, similar to traditional hardware wallets. These mnemonics can be stored in the device's internal memory or on SD cards.

Krux does not include hardware secure elements. The security of stored data relies on encryption. Read more about [Krux Encrypted Mnemonics](./getting-started/features/encrypted-mnemonics.md).

**Note**: Due to the inherent fragility of electronic components, never use your Krux device or SD card encrypted storage as your sole backup method. Always maintain a physical backup for added security.

## What is Beta version?
The Beta version includes the latest and most experimental features, which we occasionally share on our social media. These can be found exclusively in the [test (beta) repository](https://github.com/odudex/krux_binaries/). Use and flash the beta firmware if you are curious about new features or want to participate in the development process by hunting bugs, providing feedback, and sharing ideas in our Telegram groups or other social media platforms.

For regular use, flash the official releases, which are signed, thoroughly tested, and well-documented.

## What is Krux Android app?

### How can I find it?
The Krux Android app is available as an APK in the [test (beta) repository](https://github.com/odudex/krux_binaries/tree/main/Android). It requires Android 6.0 or above.

### How can I install it?
The APK is not available on the Play Store. You can download the APK directly or transfer it to your Android device via SD card or USB cable. To install it, you may need to configure your Android device to allow installations from unknown sources.

### Is it safe to use?
The Krux Android app is designed for learning about Krux and Bitcoin air-gapped transactions. Due to the numerous potential vulnerabilities inherent in smartphones, such as the lack of control over the operating system, libraries, and hardware peripherals, the Krux app **should NOT be used** to manage wallets containing savings or **important keys and mnemonics**. For secure management of your keys, **a dedicated device** is recommended.
