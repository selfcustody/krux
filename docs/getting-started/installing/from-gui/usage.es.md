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

#### Flashear 

Cuando comienza el flasheo, serás advertidode **no desconectar el dispositivo hasta que el proceso sea completado**
Podrás ver el progreso del flash:

<img width="640" src=" /krux/img/krux-installer/flash.png" alt="Krux-Installer unzip" />
> ⚠️  CONSEJO: Debes conectar y encender tu dispositivo **antes de presionar extraer y comenzar el flasheo!**.

Y también un ícono de bien hecho:

<img width="640" src=" /krux/img/krux-installer/flash_done.png" alt="Krux-Installer unzip" />

> ⚠️  CONSEJO:
----8<----
flash-krux-logo.es.txt
----8<----


##### Error de flasheo
----8<----
error-flashing-windows.es.txt
----8<----



#### Actualización sin conexión a la red

Una vez instalado el firmware inicial en tu dispositivo mediante USB, puedes realizar actualizaciones adicionales mediante una tarjeta SD para mantener el dispositivo aislado.

<img width="640" src=" /krux/img/krux-installer/unzip.png" alt="Krux-Installer unzip" />
> ⚠️ Presiona "Air-gapped update with"

Una vez extraídos los archivos `firmware.bin` y `firmware.bin.sig` verás un mensaje de advertencia.

<img width="640" src=" /krux/img/krux-installer/warn_airgap.png" alt="Krux-Installer warn airgap" />

Inserta la tarjeta SD y haz clic en 'Continuar' para que el instalador la detecte.

<img width="640" src=" /krux/img/krux-installer/list_drivers.png" alt="Krux-Installer warn airgap" />
> ⚠️ Si se inserta una sola tarjeta SD, la pantalla mostrará un botón grande. Si se detectan varias unidades extraíbles, se listarán tanto las tarjetas SD como las demás unidades.

Seleccione la unidad extraíble deseada para copiar `firmware.bin` y `firmware.bin.sig.` El primero es el firmware de Krux y el segundo es un archivo de firma que verifica la integridad y autenticidad del firmware. 

Ahora puede comparar el hash del firmware calculado por el instalador con el hash del firmware calculado por el dispositivo.

<img width="640" src=" /krux/img/krux-installer/airgap_done.png" alt="Krux-Installer warn airgap" />
> ⚠️ Una vez copiados los archivos, retira la tarjeta SD de la computadora, conéctala al dispositivo y compara los hashes.

### Borrar dispositivo

Este proceso consta de dos pasos: **Mensaje de advertencia** y **Proceso de borrado**.

#### Advertencia

Antes de que comienze el borrado, se mostrará un mensaje:

<img width="640" src=" /krux/img/krux-installer/wipe_warn.png" alt="Wipe Warning" />
> ⚠️  CONSEJO: Es útil cuando el dispositivo no funciona o por razones de seguridad.
Para volver a usar Krux, deberás volver a flashear el firmware.

#### Borrar

Una vez iniciado el proceso, la pantalla se congelará y un icono giratorio seguirá moviéndose.
Cuando termine, puedes desplazarte hacia abajo y verás un icono de `verificación.`

<img width="640" src=" /krux/img/krux-installer/wipe.png" alt="Wipe Warning" />
> ⚠️  CONSEJO: No desconectes ni apagues tu dispositivo ni tu computadora. Espera a que finalice el proceso.

----8<----
tips-after-install.es.txt
----8<----
