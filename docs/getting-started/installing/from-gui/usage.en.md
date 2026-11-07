# Usage

Krux Installer bundles one version of the Krux firmware. Once installed, it can
flash your device offline. To use a different firmware version, download an
[installer release](https://github.com/selfcustody/krux-installer/releases) that
bundles it or follow the [manual installation instructions](../from-pre-built-release.md).

## Main menu

Open Krux Installer, read the disclaimer, and click **I understand** to continue.
On Linux, the installer may ask for permission to access the USB serial port.
Follow the on-screen instructions if prompted.

<img width="640" src="../../../../img/krux-installer/main.png" alt="Krux Installer main menu before a device is selected">

**Flash firmware** and **Wipe device** become available after you select a device.
You can open **Settings** and **About** from the main menu at any time.

### Kivy Fatal Error - OpenGL

Krux Installer uses Kivy and requires OpenGL 2.0 or later. On Windows, if the
installer shows an OpenGL error, try installing the
[OpenCL™, OpenGL®, and Vulkan® Compatibility Pack](https://apps.microsoft.com/detail/9nqpsl29bfff)
from Microsoft.

<img src="../../../../img/krux-installer/opengl-error.jpg" style="width: 37%; min-width: 250px;" alt="Kivy OpenGL error on Windows">

## Select device

Click **Device: select a new one**, then choose your device model. The installer
returns to the main menu with the selected model next to **Device**.

<img width="640" src="../../../../img/krux-installer/select_device.png" alt="Krux Installer list of device models">

Models unavailable for the bundled firmware are dimmed.

## Flash device

1. Connect your device to the computer with a USB data cable and turn it on.
2. Confirm that the model shown next to **Device** matches your hardware, then
   click **Flash firmware**.
3. Leave the device connected until the installer displays **DONE**.

<img width="640" src="../../../../img/krux-installer/device_selected.png" alt="Krux Installer with Amigo selected and Flash firmware enabled">

The installer checks the bundled firmware against its build-time SHA256 hash
before flashing.

----8<----
flash-krux-logo.en.txt
----8<----

### Error flashing

If flashing fails or stalls while trying to enter K210 ROM ISP mode, see
[Error when flashing](../../../troubleshooting.md#error-when-flashing).

### Air-gapped update

After the initial USB installation, you can install subsequent updates using
the [microSD card update guide](../../features/sd-card-update.md).

## Settings

Open **Settings** to change **Flash baudrate**, which controls how fast firmware
is written over USB, or **Locale**, which changes the installer language.

<img width="640" src="../../../../img/krux-installer/app_settings.png" alt="Krux Installer settings with flash baudrate and locale options">

## Wipe device

Wiping permanently erases saved data and removes the firmware. Back up any
wallet recovery information you need before proceeding.

1. Connect the device over USB and select its model.
2. Click **Wipe device** and read the warning. Click **Proceed** to start the wipe.
3. Leave the device connected until the installer displays **DONE**. Disconnect
   and reconnect it before flashing the firmware again.

<img width="640" src="../../../../img/krux-installer/wipe_warn.png" alt="Warning that a full wipe permanently erases data and firmware">

----8<----
tips-after-install.en.txt
----8<----
