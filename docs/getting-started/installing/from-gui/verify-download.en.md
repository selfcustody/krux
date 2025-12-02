Before start using the GUI, it's **strongly recommended** to verify the authenticity of the [{{latest_installer_sha}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sha}}) file.
It attest the integrity of all variants ([{{latest_installer_deb}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}}), [{{latest_installer_rpm}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}}), [{{latest_installer_mac_arm}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}}), [{{latest_installer_win}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}})).

To do this, download two files:

* [`{{latest_installer_sha}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sha}});
* [`{{latest_installer_sig}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sig}}).

## Verify the authenticity

**Linux/MacOS**

The next step is import the developer's key:

```bash
gpg --keyserver {{latest_installer_keyserver}} --recv-keys {{latest_installer_key}}
```

Then, to verify yourself, run this:

```bash
gpg --verify {{latest_installer_sig}}
```

**Windows**

* You'll need have [GPG](https://gnupg.org/) installed;
* We recommend installing [GPG4Win](https://www.gpg4win.org/).

After install, you can proceed with **Linux/MacOS** steps in the terminal.

> ⚠️  TIP: If the verification was successful, you may get a message similar to: `Good signature from "qlrddev <qlrddev@gmail.com>"`.
Also, you can ignore a WARNING message if it says that the key isn't a trusted one (you need to do it manually).

## Verify the integrity

After verify that the [`{{latest_installer_sha}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sha}})
is authentic, we can proceed with the integrity check in your `bash`/`zsh` terminal:

**Linux / MacOS**

```bash
sha256sum --check {{latest_installer_sha}}
```

**Windows**

You can verify the integrity with this command in a `powershell` terminal:

```pwsh
$exe = '.\{{latest_installer_win}}'
$file = Split-Path $exe -Leaf

(Get-FileHash $exe -Algorithm SHA256).Hash -eq
(Select-String $file '.\{{latest_installer_sha}}').Line.Split()[0].ToUpper()
```

> 🛡️  TIP: If you followed the authenticity/integrity checks steps presented, you already
have the assurance that the software is from a verified and genuine software publisher.
This will also help establish a chain of trust when you perform the firmware verification
step before flashing.


