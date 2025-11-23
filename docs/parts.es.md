<img src="../../img/krux-devices.jpg" style="width: 60%; min-width: 300px;">

### Dispositivos Compatibles (tabla comparativa)

| Dispositivo | [M5StickV](#m5stickv) | [Maix Amigo](#maix-amigo) | [Maix Dock](#maix-dock) | [Yahboom k210 module](#yahboom-k210-module) | [Maix Cube](#maix-cube) | [WonderMV](#wondermv) | [TZT](#tzt) |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| Rango de Precio | US$ 50-55 | US$ 50-85 | US$ 27-35  | US$ 45-61 | US$ 34-49 | US$ 58-86 | US$ 48 |
| Tamaño de Pantalla / resolución | 1.14" / 135*240 | 3.5" / 320*480 | 2.4" / 240*320 | 2" / 240*320 | 1.3" / 240*240 | 2" / 240*320 | 2" / 240*320 |
| Control de Brillo | :white_check_mark: | :x: | :x: | :x: | :white_check_mark: | :white_check_mark: | :x: |
| Tamaño del dispositivo | 48\*24\*22mm | 104\*63\*17mm | 98\*59\*18mm | 57\*41\*17mm | 40\*40\*16mm | 59\*41\*17mm | 57\*41\*16mm |
| Pantalla Táctil | :x: | Capacitive | :x: | Capacitive | :x: | Capacitive | Capacitive |
| Camara | `OV7740` | `OV7740` rear<br>`GC0328` front | `GC0328` | `OV2640` <i style="font-size: 85%">(VER:1.0)</i> or<br>`GC2145` <i style="font-size: 85%">(VER:1.1)</i> | `OV7740` | `GC2145` | `GC2145` or<br>`GC0328` |
| Bateria  | 200mAh | 520mAh | :x: | :x: | 200mAh | :x: | :x: |
| Requisitos | None | None | [Rotary encoder](https://duckduckgo.com/?q=ky-040)<br> [3D printed case](https://github.com/selfcustody/DockEncoderCase)<br> Soldering<br>Assembly | None | None | None | None |
| Advertencias  | [:material-numeric-1-circle:{ title="USB-C recognition" }](#pull-up-resistor-info) | [:material-numeric-2-circle:{ title="Maix Amigo screens" }](#amigo-info) | [:material-numeric-3-circle:{ title="Maix Dock and soldered pin" }](#dock-info) | Micro USB | 3-Way button | [:material-numeric-1-circle:{ title="USB-C recognition" }](#pull-up-resistor-info) [:material-numeric-4-circle:{ title="WonderMV and SD card" }](#wondermv-info) | None |

<i style="font-size: 85%">:material-numeric-1-circle:{id="pull-up-resistor-info"}:
----8<----
usb-c-pull-up-resistor.en.txt
----8<----
</i>

<i style="font-size: 85%">:material-numeric-2-circle:{id="amigo-info"}:
----8<----
amigo-more-info-faq.en.txt:2
----8<----
</i>

<i style="font-size: 85%">:material-numeric-3-circle:{id="dock-info"}:
Algunas unidades Maix Dock son entregadas con conectores de pines soldados, lo que impide que encajen en la [carcasa impresa 3D](https://github.com/selfcustody/DockEncoderCase). Algunas placas también incluyen wifi integrado. 
</i>

<i style="font-size: 85%">:material-numeric-4-circle:{id="wondermv-info"}:
WonderMV puede reiniciarse al insertar algunas tarjetas SD, visita [¿Por qué se reinicia mi WonderMV](troubleshooting.md/#why-does-my-wondermv-reboot-when-i-insert-an-sd-card).
</i>

<i style="font-size: 85%">**Todos los dispositivos cuentan con el chip Kendryte K210:**
proceso de 28nm, RISC-V de doble núcleo de 64bit @400MHz, 8 MB de SRAM de alta velocidad, cámara DVP e interfaz LCD MCU, acelerador AES, aelerador SHA256, aceleradpr FFT.
</i>

### M5StickV
<img src="../img/maixpy_m5stickv/logo-250.png" align="right" style="width: 15%;">

Krux fue adaptado a este dispositivo por primera vez en Marzo de 2022. Cuenta con la pantalla de menor tamaño y resolución, también incluye batería integrada. Consulta la [advertencia de reconocimiento de USB-C <i style="font-size: 85%">:material-numeric-1-circle:{ title="USB-C recognition" }](#pull-up-resistor-info)</i> anterior para información importante. A continuación, se muestra una lista de distribuidores donde se puede encontrar:

- [M5Stack](https://shop.m5stack.com/products/stickv)
- [Mouser](https://www.mouser.com/c/?q=m5stickv)
- [Digi-Key](https://www.digikey.com/en/products/detail/m5stack-technology-co-ltd/K027/10492135)
- [Electromaker](https://www.electromaker.io/shop/product/m5stickv-k210-ai-camera-without-wifi)
- [Lee's Electronic](https://leeselectronic.com/en/product/169940-m5stick-ai-camera-kendryte-k210-risc-v-core-no-wifi.html)
- [AliExpress](https://www.aliexpress.com/w/wholesale-stickv-k210.html)
- [Alibaba](https://www.alibaba.com/trade/search?SearchText=stickv+k210)
- [ABRA](https://abra-electronics.com/sensors/cameras/m5stickv-k210-ai-camera-ideal-for-machine-vision.html)
- [Adafruit](https://www.adafruit.com/product/4321)
- [Cytron](https://www.cytron.io/c-development-tools/c-fpga/p-m5stickv-k210-ai-camera-without-wifi)

<div style="clear: both"></div>

### Maix Amigo
<img src="../img/maixpy_amigo/logo-300.png" align="right" style="width: 16%;">

Krux a sido compatible con este dispositivo desde su segunda versión en Agosto de 2022. Ofrece la pantalla con mayor tamaño y resolución, pantalla táctil y batería integrada. A continuación, se muestra una lista de distribuidores donde está disponible:

- [AliExpress](https://www.aliexpress.com/w/wholesale-sipeed-amigo.html)
- [Seeed Studio](https://www.seeedstudio.com/Sipeed-Maix-Amigo-p-4689.html)
- [Digi-Key](https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/102110463/13168813)
- [Mouser](https://www.mouser.com/c/?q=sipeed)
- [Electromaker](https://www.electromaker.io/shop/search/sipeed)
- [スイッチサイエンス](https://www.switch-science.com/search?q=maix+amigo)

<div style="clear: both"></div>

### Yahboom k210 module
<img src="../img/maixpy_yahboom/logo-312.png" align="right" style="width: 16%;">

Con soporte de Krux desde marzo de 2024, este dispositivo cuenta con pantalla táctil e incluye una tarjeta compatible de 32 GB, un lector de tarjetas USB, un conector PH2.0 macho-a-macho de 4 pines y un adaptador PH2.0 hembra para conectarlo a una [impresora térmica](#optional-ttl-serial-thermal-printer). A continuación, se muestra una lista de distribuidores donde está disponible:

- [AliExpress](https://www.aliexpress.com/w/wholesale-yahboom-k210-module.html)
- [Amazon](https://www.amazon.com/s?k=Yahboom+k210+module)
- [Yahboom Store](https://category.yahboom.net/collections/mb-module/products/k210-module)
- [ETC HK Shop](https://www.etchkshop.com/products/k210-module-ai-camera)

<div style="clear: both"></div>

### Maix Cube
<img src="../img/maixpy_cube/logo-400.png" align="right" style="width: 18%;">

Con soporte de Krux desde julio de 2024, este dispositivo cuenta con la segunda pantalla y resolución más pequeñas, un botón de tres direcciones y batería integrada. A continuación, se muestra una lista de distribuidores donde está disponible:

- [Seeed Studio](https://www.seeedstudio.com/Sipeed-Maix-Cube-p-4553.html)
- [Mouser](https://www.mouser.com/c/?q=sipeed)
- [Electromaker](https://www.electromaker.io/shop/search/sipeed)
- [Digi-Key](https://www.digikey.com.br/en/products/filter/embedded-mcu-dsp-evaluation-boards/786?s=N4IgTCBcDaIM4EsAOBTFATEBdAvkA)
- [AliExpress](https://www.aliexpress.com/w/wholesale-sipeed-cube.html)
- [Amazon](https://www.amazon.com/s?k=k210+cube)

<div style="clear: both"></div>

### WonderMV
<img src="../img/maixpy_wonder_mv/logo-304.png" align="right" style="width: 16%;">

Con soporte de Krux desde septiembre de 2024, este dispositivo de pantalla táctil cuenta con una placa trasera metálica e incluye una tarjeta compatible de 32 GB, un lector de tarjetas USB y dos cables macho a macho con conector 5264 de 4 pines para conectarlo a una [impresora térmica](#optional-ttl-serial-thermal-printer). Consulte la [advertencia de reconocimiento de USB-C <i style="font-size: 85%">:material-numeric-1-circle:{ title="USB-C recognition" }](#pull-up-resistor-info)</i> y la [adverencia de tarjeta SD <i style="font-size: 85%">:material-numeric-4-circle:{ title="WonderMV and SD card" }](#wondermv-info)</i> para obtener información importante. Los siguientes distribuidores ofrecen este dispositivo:

- [AliExpress](https://www.aliexpress.com/w/wholesale-k210-wondermv.html)
- [Amazon](https://www.amazon.com/s?k=k210+WonderMV)
- [Hiwonder Store](https://www.hiwonder.com/products/wondermv)
- [Ruten](https://www.ruten.com.tw/item/show?22351444721094)
- [飆機器人](https://shop.playrobot.com/products/veo0116)

<div style="clear: both"></div>


### TZT
<img src="../img/maixpy_tzt/logo-314.png" align="right" style="width: 16%;">

Con soporte de Krux desde octubre de 2025, este dispositivo de pantalla táctil viene con una carcasa de aluminio fresado de primera calidad y cuenta con cinco botones. Disponible a través de los siguientes distribuidores:

- [AliExpress](https://www.aliexpress.com/w/wholesale-tzt-canmv-k210.html)

<div style="clear: both"></div>



### Maix Dock
<img src="../img/maixpy_dock/logo-302.png" align="right" style="width: 16%;">

Para los aficionados al bricolaje, Krux ofrece soporte para el Maix Dock desde agosto de 2022. Estos kits incluyen una placa y una pantalla, pero requieren que adquieras un codificador rotatorio o botones por separado y que montes el dispositivo tú mismo. Algunas placas Maix Dock también incluyen wifi.

Aquí tienes ejemplos de montaje con instrucciones para recrearlos:

- [https://github.com/selfcustody/DockEncoderCase](https://github.com/selfcustody/DockEncoderCase)

Disponible en los siguientes distribuidores:

- [Mouser](https://www.mouser.com/c/?q=sipeed)
- [Electromaker](https://www.electromaker.io/shop/search/sipeed)
- [Digi-Key](https://www.digikey.com.br/en/products/filter/embedded-mcu-dsp-evaluation-boards/786?s=N4IgTCBcDaIM4EsAOBTFATEBdAvkA)
- [AliExpress](https://www.aliexpress.com/w/wholesale-sipeed-maix.html)
- [Amazon](https://www.amazon.com/s?k=sipeed+k210)

<div style="clear: both"></div>

## Otras Piezas
### Cable de carga USB-C o Micro USB
Este viene con el dispositivo. Es necesario para alimentarlo, cargarlo (si tiene batería) y para instalar ("flashear") el programa inicialmente.

### (Opcional) Tarjeta MicroSD
----8<----
sd-card-info-faq.es.txt
----8<----
Yahboom incluye una tarjeta compatible de 32 GB. El tamaño de la tarjeta no es importante; una tarjeta de más de unos pocos megabytes será suficiente.

### (Opcional) Impresora Térmica Serial TTL
----8<----
warning-printer.es.txt
----8<----

Krux puede imprimir todos los códigos QR que genera, incluyendo los de mnemónicos, xpubs, copias de seguridad de billetera y PSBT firmados, utilizando una impresora térmica conectada localmente a través de su puerto serial.

Muchas impresoras térmicas serie TTL son compatibles, pero actualmente la [Goojprt QR203](https://www.aliexpress.com/w/wholesale-Goojprt-QR203.html) ofrece la mejor compatibilidad (excepto que esta impresora solo admite caracteres ASCII o chinos; los caracteres no ASCII se imprimirán como chinos). El [paquete de inicio de la impresora Adafruit](https://www.adafruit.com/product/600) también es una opción práctica para empezar, ya que incluye todos los componentes necesarios para imprimir (excepto el cable de conversión). Para garantizar un funcionamiento correcto, habilite el controlador de la impresora en [ajustes](getting-started/settings.md/#thermal), configure el pin de transmisión y la velocidad en baudios a 19200 o 9600 (según la impresora), como se explica en este [tutorial de la impresora Adafruit](https://learn.adafruit.com/mini-thermal-receipt-printer/first-test). Necesitará conectar el Tx del dispositivo al Rx de la impresora y la tierra del dispositivo a la tierra de la impresora. No conecte ningún otro pin, ya que una conexión incorrecta podría dañar el dispositivo. La impresora requiere una fuente de alimentación dedicada, generalmente con una salida de 5 a 9 V (o 12 V) y capaz de suministrar al menos 2 A. Para más información, [consulte esta discusión](https://github.com/selfcustody/krux/discussions/312).

#### Cable de Conversión 
Para conectar la impresora a M5StickV, Amigo o Cube, necesitará un [cable de conversión Grove](https://store-usa.arduino.cc/products/grove-4-pin-male-to-grove-4-pin-cable-5-pcs) con un conector Grove macho de 4 pines en un extremo (para conectarlo al dispositivo) y puentes macho de 4 pines en el otro (para conectarlo a la impresora). Compruebe primero la conexión de su dispositivo y modelo de impresora. Yahboom incluye un conector hembra PH2.0 de 4 pines; Dock no tiene conector; WonderMV incluye un conector Molex 51004 de 4 pines (para usar con servo inteligente). Para una conexión más fiable, se recomienda cortar y soldar los cables personalizados en lugar de usar puentes. Aquí tenemos una descripción de algunos [estándares de conectores de circuitos interintegrados (I2C)](https://www.cable-tester.com/i2c-pin-out/).