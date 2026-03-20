Esta pagina explica como instalar Krux desde nuestra última versión de prueba (beta) precompilada.

### Advertencia
Tenga en cuenta que estos son archivos binarios sin firma.

### Descarga
Descargue el firmware experimental compilado en el [repositorio de prueba (beta)](https://github.com/odudex/krux_binaries) o la aplicación de Android `apk` en [KruxMobileApp](https://github.com/selfcustody/KruxMobileApp).

#### Móvil - Android
La [aplicación móvil para android de Krux](../../faq.md#what-is-krux-mobile-android-app) está diseñada para aprender sobre Krux y las transacciones sin conexión a internet en Bitcoin. Debido a las numerosas vulnerabilidades potenciales inherentes a los smartphones, como la falta de control sobre el sistema operativo, los paquetes externos y los accesorios de hardware, la aplicación Krux NO debe usarse para administrar billeteras que contengan ahorros o claves y mnemónicos importantes. Para una gestión segura de sus claves, se recomienda un dispositivo dedicado.

#### Firmware compilado para dispositivos Kendryte K210
#### M5StickV
Para instalar en M5StickV, ejecute lo siguiente.

##### Linux
```bash
./ktool-linux -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_m5stickv\kboot.kfpkg
```

#### Sipeed Maix Amigo
Para instalar en Maix Amigo, ejecute lo siguiente.

##### Linux
```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B goE -b 1500000 maixpy_amigo/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_amigo\kboot.kfpkg
```

----8<----
amigo-more-info-faq.es.txt
----8<----

#### Sipeed Maix Cube
Para instalar en Maix Cube, ejecute lo siguiente.

##### Linux
```bash
./ktool-linux -B goE -b 1500000 maixpy_cube/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B goE -b 1500000 maixpy_cube/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_cube\kboot.kfpkg
```

#### Sipeed Maix Dock
Para instalar en Maix Dock necesitas pasar el parametro `-B dan`.

##### Linux
```bash
./ktool-linux -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B dan -b 1500000 maixpy_dock\kboot.kfpkg
```

#### Aimotion Yahboom k210 module
Para instalar el módulo Yahboom K210, tendrás que especificar el puerto manualmente.

##### Linux
Consulte el puerto correcto ejecutando `ls /dev/ttyUSB*`, en el siguiente ejemplo usamos `/dev/ttyUSB0`:
```bash
./ktool-linux -B goE -b 1500000 -p /dev/ttyUSB0 maixpy_yahboom/kboot.kfpkg
```

##### Mac
Consulte el puerto correcto usando la linea de comandos: `ls /dev/cu.usbserial*`, en el siguiente ejemplo usamos `/dev/cu.usbserial-10`:
```bash
./ktool-mac -B goE -b 1500000 -p /dev/cu.usbserial-10 maixpy_yahboom/kboot.kfpkg
```

##### Windows
Consulte el puerto correcto en **Administrador de dispositivos -> Puertos (COM y LPT)**, en el siguiente ejemplo usamos `COM6`:
```pwsh
.\ktool-win.exe -B goE -b 1500000 -p COM6 maixpy_yahboom\kboot.kfpkg
```

#### Módulo de reconocimiento visual Hiwonder WonderMV
Para instalar en WonderMV tendrás que especificar el parámetro `-B dan`.

##### Linux
```bash
./ktool-linux -B dan -b 1500000 maixpy_wonder_mv/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B dan -b 1500000 maixpy_wonder_mv/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B dan -b 1500000 maixpy_wonder_mv\kboot.kfpkg
```

#### TZT
Para instalar en TZT tendrás que pasar el parámetro `-B dan`.

##### Linux
```bash
./ktool-linux -B dan -b 1500000 maixpy_tzt/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B dan -b 1500000 maixpy_tzt/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B dan -b 1500000 maixpy_tzt\kboot.kfpkg
```

#### Embed Fire
Para instalar en Embed Fire tendrás que pasar el parámetro `-B dan` y `-b 400000` (velocidad de transmisión máxima admitida).

##### Linux
```bash
./ktool-linux -B dan -b 400000 maixpy_embed_fire/kboot.kfpkg
```

##### Mac
```bash
./ktool-mac -B dan -b 400000 maixpy_embed_fire/kboot.kfpkg
```

##### Windows
```pwsh
.\ktool-win.exe -B dan -b 400000 maixpy_embed_fire\kboot.kfpkg
```
