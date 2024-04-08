### Installing from a GUI

You can install Krux onto your K210-based device using our official desktop application,
[KruxInstaller](https://github.com/selfcustody/krux-installer), available for Linux and Windows.

Under the hood the GUI uses the same methods described in
[Installing from pre-build release](../installing/from-pre-built-release.md),
i.e., download, verify and flash the latest official release,
but you won't need to type any command.
Additionally you will be able to install the
[pre-built test or beta release](../installing/from-test-release.md) too.

#### Download the latest release

The primary way to download the installer is via
[releases page on Github](https://github.com/selfcustody/krux-installer/releases),

<div>
    <img src="/krux/img/krux-installer/download_release.png" alt="KruxInstaller download release page"/>
    <br/>
    <em> Figure 1: KruxInstaller download release page</em>
</div>

##### Archlinux users

There is a package named [`krux-installer-bin`](https://aur.archlinux.org/packages/krux-installer-bin)
for Archlinux in the [AUR](https://aur.archlinux.org/). To install `krux-installer-bin`,
you will need to have some [pacman wrapper](https://wiki.archlinux.org/title/AUR_helpers#Pacman_wrappers)

Then run on your terminal:

```bash
yay -Sy krux-installer-bin
```

##### Other Linux distros and Windows

###### Choose files according to your operating system

At the moment we support some Operational Systems with `x86`/`x86_64`/`amd64` architetures.
Above we list some of them with a `*` (wildcard), where it can be followed with `.sha256.txt`
(integrity extension) and `.sig` (authenticity extension) files.

| **File**                           | **Operational System**             |
|------------------------------------|:----------------------------------:|
| `krux-installer-0.0.13.AppImage*`  | Any linux distribution             |
| `krux-installer-0.0.13.x86_64.rpm*`| RedHat-based: Fedora, etc...       |
| `krux-installer_0.0.13_amd64.deb*` | Debian-based: Ubuntu, PopOS, etc...| 
| `krux-installer_0.0.13.exe*`       | Windows                            | 


###### Verify the integrity

If you trust the developer, you can skip to [Usage](./#usage). But we encourage you to follow this
ethos to detect if any unauthorized modification was made between the site an your local computer.

<table>
    <thead>
        <tr>
            <th><strong>System</strong></th>
            <th style="text-align: center;"><strong>Commands</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Any Linux distribution</td>
            <td>
                ```bash
                sha256sum --check krux-installer-0.0.13.AppImage.sha256.txt
                ``` 
            </td>
        </tr>
        <tr>
            <td>RedHat-based</td>        
            <td>
                ```bash
                sha256txt --check ./krux-installer-0.0.13.x86_64.rpm.sha256.txt
                ``` 
            </td>
        </tr>
        <tr>
            <td>Debian-based</td>        
            <td>
                ```bash
                sha256sum --check ./krux-installer_0.0.13_amd64.sha256.txt
                ``` 
            </td>
        </tr>
        <tr>
            <td>Windows (powershell)</td>        
            <td>
                ```pwsh
                (Get-FileHash '.\krux-installer_0.0.13.exe').Hash -eq (Get-Content '.\krux-installer_0.0.13.exe.sha256.txt')
                ``` 
            </td>
        </tr>
    </tbody>
</table>
            
###### Verify the authenticity

To do this, you will need have [GPG](https://gnupg.org/) installed. In Linux systems, it's common to already have it installed by default.
In Windows, we recommend install [GPG4Win](https://www.gpg4win.org/).

Once installed, run this command to retrieve the developer's key:

```bash
gpg --keyserver hkps://keys.openpgp.org --recv-keys B4281DDDFBBD207BFA4113138974C90299326322
```

<table>
    <thead>
        <tr>
            <th><strong>System</strong></th>
            <th style="text-align: center;"><strong>Commands</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Any Linux distribution</td>
            <td>
                ```bash
                gpg --verify ./krux-installer-0.0.13.AppImage.sig
                ``` 
            </td>
        </tr>
        <tr>
            <td>RedHat-based</td>        
            <td>
                ```bash
                gpg --verify ./krux-installer-0.0.13.x86_64.rpm.sig
                ``` 
            </td>
        </tr>
        <tr>
            <td>Debian-based</td>        
            <td>
                ```bash
                gpg --verify ./krux-installer_0.0.13_amd64.deb.sig
                ``` 
            </td>
        </tr>
        <tr>
            <td>Windows (powershell)</td>        
            <td>
                ```pwsh
                gpg --verify .\krux-installer_0.0.13_exe.sig
                ``` 
            </td>
        </tr>
    </tbody>
</table>


##### Install

<table>
    <thead>
        <tr>
            <td><strong>System</strong></td>
            <td style="text-align: center"><strong>Steps</strong></td>
        </tr>
    </thead>
    <tbody>
        <tr>            
            <td>Any Linux distribution</td>
            <td>
                <ul>
                    <li>Place the <code>krux-installer-0.0.13.AppImage</code> where you want;</li>
                    <li>Modify permision to execute: <code>chmod +x krux-installer-0.0.13.AppImage</code>;</li>
                    <li>Run it: <code>./krux-installer-0.0.13.AppImage</code>.</li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>RedHat-based</td>                
            <td>
                <ul>
                    <li>Fedora: <code>sudo  dnf install krux-installer-0.0.13.x86_64.rpm</code>;</li>
                    <li>Other RedHat based distros: <code>sudo yum localinstall krux-installer-0.0.13.x86_64.rpm</code>.</li>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Debian-based</td>
            <td>
                <ul>
                    <li>Install with dpkg: <code>sudo dpkg -i krux-installer_0.0.13_amd64.deb</code>;</li>
                    <li>Update it with apt-get: <code>sudo apt-get install -f</code>.</li>
                </ul>
            </td>             
        </tr>
        <tr>
            <td>Windows</td>
            <td>
                The `krux-installer_0.0.13.exe` is a <a href="https://nsis.sourceforge.io/Main_Page)">NSIS</a> installer.
                If you use Windows, the first time you run the `.exe` file the system will ask you if you
                trust the application.
            </td>             
        </tr>
    </tbody>   
</table>

#### Usage

##### Main Menu 
When running Krux Installer, you will be presented with a menu of two items:

<div>
    <img src="/krux/img/krux-installer/main.png" alt="KruxInstaller Main Menu" />
    <br/>
    <em>Figure 2: Main menu with two items</em>
</div>


##### Select Device
This is the first step, to select the device we want to flash.

<div>
    <img src="/krux/img/krux-installer/select_device.png" alt="Select Device Menu with choosen device" />
    <br/>
    <em>Figure 3: Select Device Menu with choosen device</em>
</div>

##### Returned to main menu

Now you will be faced with a menu with three items:

<div>
    <img src="../../../img/krux-installer/main2.png" alt=" Menu with three items" />
    <br/>
    <em>Figure 4: Main menu with three items</em>
</div>

##### Wipe device

This option will give the oportunity to **erase ALL data in device's flash memory**.
It's useful when your device is bricked or as a security approach. To use Krux again, you'll need
to re-flash it. You will be warned (use it on your own risk):

<div>
    <img src="../../../img/krux-installer/wipe_warn.png" alt="Wipe Warning" />
    <br/>
    <em>Figure 5: Wipe warning before execution</em>
</div>

Once selected, the system will prompt for your password. Once typed the `Wipe` process will start and the 
screen will appear to be freeze. Do not touch, unplug or poweroff your device/computer and wait until be done.

<div>
    <img src="../../../img/krux-installer/wipe_run.png" alt="Wipe running" />
    <br/>
    <em>Figure 6: Wipe process running</em>
</div>

Once done, you can scroll down the window to see all events that occured:

<div>
    <img src="../../../img/krux-installer/wipe_finished.png" alt="Wipe done" />
    <br/>
    <em>Figure 7: Wipe done</em>
</div>

Now select which firmware you want to flash, i.e. the [latest official release](https://github.com/selfcustody/krux/releases) or the [test (beta) release](https://github.com/odudex/krux_binaries). While in the official release we can [verify its integrity and authenticity](from-pre-built-release.md/#verify-the-files), in the second one we will have no means of verifying it, because it is not signed. However, the test or beta firmware will contain the newest features that are being developed and discussed on our social media.

#### Official release
The software will display the latest officially released version in the form `selfcustody/tags/vXX.YY.Z`, where XX means the year of release, YY the month of release and Z a subversion of this release.

Once selected, the application will check if the entry exists in the system. If not, it will download the following files: the firmware as a `.zip`, the sha256 of the zip as `sha256.txt`, the signature of the zip as `.sig` and the `selfcustody.pem`.

- `krux-vXX.YY.Z.zip`: contains all the necessary binaries and signature files to install the firmware on each of the supported devices;

- `krux-vXX.YY.Z.zip.sha256.txt`: contains a hash to verify the integrity of the downloaded `zip` file;

- `krux.vXX.YY.Z.zip.sig`: is the public digital signature for authenticity verification of the downloaded `zip` file;

- `selfcustody.pem`: is the public digital certificate that attests to the veracity of the public digital signature.

![select-version-not-downloaded-selfcustody](../../img/krux-installer/select_version_not_downloaded_selfcustody.gif "KruxInstaller Select Selfcustody Version not downloaded Menu")

If they are already present on your computer, the application will give you the option to download them again or continue with the files already downloaded.

![select-version-downloaded-selfcustody](../../img/krux-installer/select_version_downloaded_selfcustody.gif "KruxInstaller Select Selfcustody version downloaded Menu")

##### Test or beta binaries
As the name suggests, these binaries are intended for test purposes, contain experimental features, and are more likely to contain bugs. Use only for experimentation and to provide feedback.

The installer will present the latest test (beta) release.
![select-version-not-downloaded-odudex](../../img/krux-installer/select_version_not_downloaded_odudex.gif "KruxInstaller Select Odudex version Menu")

- `<device>/firmware.bin`: is the unsigned firmware's binary of the choosen device;
- `<device>/kboot.kfpkg`: is the unsigned and compressed firmware bootloader of the choosen device;
- `<device>/ktool-<os>`: is the k210 tool "flasher" specific to Operational system:
    - `ktool-linux`: for linux machines;
    - `ktool-win.exe`: for windows machines;

If they are already present on your computer, the application will give you the option to download them again or continue with the files already downloaded.

![select-version-downloaded-odudex](../../img/krux-installer/select_version_downloaded_odudex.gif "KruxInstaller Select Odudex version downloaded Menu")

#### Flash
Once we choose the device and firmware, we can flash. Before start the flash process itself, you be warned that you must plug and power on your device.

![flash-device](../../img/krux-installer/flash-device.gif "KruxInstaller Flash to device")

----8<----
flash-krux-logo.md
----8<----

----8<----
amigo-more-info-faq.md
----8<----

### Multilingual support
Prefer a different language? Krux has support for multiple languages. Once at the start screen, go to `Settings`, followed by `Locale`, and select the locale you wish to use.

### Upgrade via microSD card
Once you've installed the initial firmware on your device via USB, you can either continue updating the device by flashing or you can perform upgrades [via microSD](../features/sd-card-update.md) card to keep the device airgapped.
