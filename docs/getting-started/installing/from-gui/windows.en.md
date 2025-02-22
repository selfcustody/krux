# :material-microsoft-windows: Download assets
 
* [`{{latest_installer_win}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}})
* [`{{latest_installer_win}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}}.sha256.txt)
* [`{{latest_installer_win}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}}.sig)

## Verify the integrity

----8<----
verify-the-integrity-explain.en.txt
----8<----

```pwsh
(Get-FileHash '.\{{latest_installer_win}}').Hash.ToLower() -eq (Get-Content '.\{{latest_installer_win}}.sha256.txt').split(" ")[0]
```

The result in prompt should be `True`.

Alternatively, you can check more closely in two steps:

* Compute the binary sha256sum hash:

```pwsh
# Option 1: Compute in default way
Get-FileHash '.\{{latest_installer_win}}'

# Option 2: Compute and filter the necessary information
(Get-FileHash '.\{{latest_installer_win}}').Hash

# Option 3: Compute, filter and process the Hash for lowercase letters
(Get-FileHash '.\{{latest_installer_win}}').Hash.ToLower()
```

* Compare with provided hash:

```pwsh
# Option 1: Get content 
Get-Content '.\{{latest_installer_win}}.sha256.txt'

# Option 2: Get content and filter the necessary information
(Get-Content '.\{{latest_installer_win}}.sha256.txt').split(" ")[0]
```

## Verify the authenticity
    
* You'll need have [GPG](https://gnupg.org/) installed;
* We recommend installing [GPG4Win](https://www.gpg4win.org/).

----8<----
verify-the-signature-explain.en.txt
----8<----
 
```pwsh
gpg --verify ./{{latest_installer_win}}.sig
```

----8<----
verify-the-signature-tip.en.txt
----8<----

## Install

Execute the `{{latest_installer_win}}`. You'll be faced with a blue window saying
"Windows protected your PC". This occurs because we don't have a
[code signing certificate](https://signmycode.com/resources/how-to-sign-an-exe-or-windows-application):

<img width="450" src="/krux/img/krux-installer/windows_warn0.jpg" alt="Windows protected your computer" />

----8<----
verify-the-signature-trust-tip.en.txt
----8<----

Follow the installer's instructions to complete the installation. At the end, click on 
"Create desktop icon":

## After install

----8<----
after-install-installer.en.txt
----8<----
