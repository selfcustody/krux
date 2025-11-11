Esta guía explica el uso básico del instalador. El inicio puede variar en algunos sistemas operativos. En los demás, los procedimientos serán similares.

### Menú Principal
Al ejecutar **Krux-Installer**, verá un menú con 4 botones habilitados y dos botones deshabilitados:

<img width="640" src="/krux/img/krux-installer/main.png" alt="Krux-Installer Main Menu" />

* Botones habilitados:
    * `Versión`: selecciona una versión del firmware;
    
    * `Dispositivo`: selecciona un dispotivo compatible con la versión seleccionada;
    
    * `Ajustes`: cambia algunos ajustes de la aplicación;
    
    * `Acerca de`: muestra información sobre la aplicación.

* Botones deshabilitados:

    * `Actualizar firmware`: Este botón iniciará el proceso de actualización del firmware;
        
        * Se habilitará cuando el usuario seleccione **ambos** la versión como el dispositivo;
    
    * `Borrar dispositivo`: Este botón iniciará el proceso de borrado del dispositivo.
    
        * Se habilitará cuando el usuario seleccione el dispostivo.

#### Error fatal de Kivy - OpenGL
Nuestra última versión utiliza Kivy y requiere al menos OpenGL versión 2.0. Si se produce este error, intente instalar el [Paquete de compatibilidad de OpenCL™, OpenGL® y Vulkan®](https://apps.microsoft.com/detail/9nqpsl29bfff) de Microsoft.

<img src="/krux/img/krux-installer/opengl-error.jpg" style="width: 37%; min-width: 250px;">

### Seleccionar versión

Al iniciarse, la aplicación se configurará con la última versión, `{{latest_krux}}`. Pero también puedes seleccionar
una versión beta o versiones anteriores:
    
<img width="640" src="/krux/img/krux-installer/select_version_menu.png" alt="Krux-Installer Select Version Menu" />

* Haz clic en el botón que muestra el texto `Versión: {{latest_krux}}`;

* Para seleccionar una versión beta, haz clic en el botón que muestra el texto `odudex/krux_binaries`;

* Para seleccionar una versión anterior, haz clic en el botón que muestra el texto `Versiones antiguas`;

#### Versión beta

Tras seleccionar `odudex/krux_binaries`, verá la siguiente advertencia:

<img width="640" src=" /krux/img/krux-installer/warn_beta.png" alt="Krux-Installer warning beta version" />

#### Versiones anteriores

* Incluimos esta opción por si le interesa conocer el historial de desarrollo del firmware;

<img width="640" src=" /krux/img/krux-installer/select_old_version_menu.png" alt="Krux-Installer Select Old Version Menu" />

* Cada versión es compatible con un dispositivo u otro;

* Por ejemplo, la versión `v22.03.0` solo es compatible con `m5stickv`.
    

### Ajustes

**Krux-Installer** te ofrece varias opciones para:

* Ajustes de Krux-Installer;

* Ajustes generales;

#### Ajustes específicos de Krux-Installer

Aquí puedes configurar algunos detalles del firmware de Krux, como:

<img width="640" src=" /krux/img/krux-installer/app_settings.png" alt="Krux-Installer App settings Menu" />

* Dónde guardar los archivos descargados;

* La velocidad de transmisión de la memoria flash;

* El idioma que se utilizará en la aplicación ([configuración regional del sistema](https://en.wikipedia.org/wiki/Locale_(computer_software))).

##### Velocidad de transmisión de la memoria flash
La velocidad de transmisión de la memoria flash determina la rapidez con la que se escribirá el firmware en el dispositivo.

<img width="640" src=" /krux/img/krux-installer/baudrate.png" alt="Krux-Installer baudrate" />

Utilice una de las siguientes velocidades (m5StickV no admite 2000000): 9600, 19200, 28800, 38400, 57600, 76800, 115200, 230400, 460800, 576000, 921600, 1500000, 2000000.

##### Configuración regional del sistema

Al iniciarse, **Krux-Installer** reconoce la configuración regional de su sistema. Si su idioma no es compatible, se utilizará `en_US` por defecto.

<img width="640" src=" /krux/img/krux-installer/locale_menu.png" alt="Krux-Installer locale menu" />


### Seleccionar dispotivo

Cada vez que seleccione una nueva versión, verá que el botón del dispositivo se
restablece al estado `Dispositivo: seleccione uno nuevo` Una vez seleccionada la versión, puede elegir el dispositivo
en ​​el que se escribirá el firmware.

Primero, seleccione el dispositivo que desea actualizar. A continuación, el menú mostrará tres opciones:

<img width="640" src=" /krux/img/krux-installer/select_device.png" alt="Select Device Menu" />

Tenga en cuenta que algunos dispositivos pueden estar deshabilitados si no son compatibles con la versión seleccionada.

### Actualizar dispositivo

Una vez que seleccione el dispositivo y la versión, se habilitará el botón «Actualizar dispositivo». Se iniciará un proceso **automático** de:

* Para versiones oficiales de firmware:

    * Advertencia;

    * Descarga;

    * Verificación:
    
    * Descomprimir el firmware correcto;

    * Flasheo:
        
        * Flasheo mediante USB;

        * Actualización sin conexión a la red mediante tarjeta SD;
        

* Para versiones beta:

    * Descarga de recursos;

    * Flasheo;

#### Advertencia

Si ya ha descargado los recursos, recibirá una advertencia y se le ofrecerá la posibilidad de
descargarlos de nuevo o continuar sin descargarlos:

<img width="640" src=" /krux/img/krux-installer/warn_already_downloaded.png" alt="Krux-Installer already downloaded" />

#### Descarga

**Krux-Installer** puede descargar cuatro recursos para versiones oficiales o uno para versiones beta.

##### Versiones oficiales

* Un archivo `zip` con todos los firmwares para cada dispositivo;

* Descargar un archivo `zip.sha256.txt` con la huella digital del archivo `zip`;

* Descargar un archivo `zip.sig` con la firma digital del archivo `zip`;

* Descargar el archivo `selfcustody.pem` con un certificado de clave pública, firmado por `odudex`;

<img width="640" src=" /krux/img/krux-installer/download_assets.png" alt="Krux-Installer downloading assets" />

##### Versiones beta

* Un archivo `kfpkg` con el firmware específico para el dispositivo seleccionado;

#### Verificación

* La verificación de integridad compara el hash calculado de `zip` con el archivo `zip.sha256.txt` proporcionado.

* La verificación de autenticidad comprueba si el archivo `zip` fue firmado realmente por `odudex`, utilizando
los archivos `zip.sig` y `selfcustody.pem`.

<img width="640" src=" /krux/img/krux-installer/verification.png" alt="Krux-Installer verification process" />


#### Descomprimir

Ahora podrá seleccionar si desea realizar un proceso de flasheo o una actualización sin conexión a la red:

<img width="640" src=" /krux/img/krux-installer/unzip.png" alt="Krux-Installer unzip" />

Haga clic en [Flashear con](#flash-with) para instalar mediante USB o en [Actualización sin conexión a la red](#air-gapped-update-with) para realizar actualizaciones mediante una tarjeta SD.

#### Flash with

When flash starts, it will warn you to **not disconnect the device until the process is complete**.
You'll be able to see the flash progress:

<img width="640" src=" /krux/img/krux-installer/flash.png" alt="Krux-Installer unzip" />
> ⚠️  TIP: You must connect and turn on your device **before click extract and flashing starts!**.

As well a done icon:

<img width="640" src=" /krux/img/krux-installer/flash_done.png" alt="Krux-Installer unzip" />

> ⚠️  TIP:
----8<----
flash-krux-logo.en.txt
----8<----


##### Error flashing
----8<----
error-flashing-windows.en.txt
----8<----



#### Air-gapped update with

Once you've installed the initial firmware on your device via USB, you can perform further firmware upgrades via SD card to keep the device airgapped.

<img width="640" src=" /krux/img/krux-installer/unzip.png" alt="Krux-Installer unzip" />
> ⚠️ Click on "Air-gapped update with"

Once the `firmware.bin` and `firmware.bin.sig` are extracted, you'll see a warning message.

<img width="640" src=" /krux/img/krux-installer/warn_airgap.png" alt="Krux-Installer warn airgap" />

Insert the SD card and click 'Proceed' to allow the installer to detect it.

<img width="640" src=" /krux/img/krux-installer/list_drivers.png" alt="Krux-Installer warn airgap" />
> ⚠️ If a single SD card is inserted, the screen will display a large button. If multiple removable drives are detected, both SD cards and other drives will be listed.

Select the desired removable drive to copy both `firmware.bin` and `firmware.bin.sig.` The first is the Krux firmware, and the second is a signature file that verifies the firmware’s integrity and authenticity. 

Now you can compare the firmware's hash computed by installer with  the firmware's hash computed by the device. 

<img width="640" src=" /krux/img/krux-installer/airgap_done.png" alt="Krux-Installer warn airgap" />
> ⚠️ Once files are copied, remove the SD card from computer, connect to device and compare the hashes

### Wipe device

This is a two step process, **Warning msg** and **Wipe process**.

#### Warning

Before the wipe starts, it will show to you a message:

<img width="640" src=" /krux/img/krux-installer/wipe_warn.png" alt="Wipe Warning" />
> ⚠️  TIP: It's useful when your device is not working or for security reasons.
To use Krux again, you'll need to re-flash the firmware.

#### Wipe

Once the process starts, the screen will appear frozen and a spinner will keep moving.
When it's done, you can scroll down you will see a `check` icon.

<img width="640" src=" /krux/img/krux-installer/wipe.png" alt="Wipe Warning" />
> ⚠️  TIP: Do not unplug or poweroff your device or computer. Wait until the process finishes.

----8<----
tips-after-install.en.txt
----8<----
