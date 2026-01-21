Krux permite crear frases semilla [mnemónicas BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) de 12 y 24 palabras mediante bits aleatorios, también conocido como [entropía](https://en.wikipedia.org/wiki/Entropy_(computing)). Generar entropía real es complicado, especialmente en un dispositivo integrado, por lo que recomendamos externalizar la generación de entropía mediante tiradas de dados. Sin embargo, también es posible seleccionar palabras al azar (por ejemplo, SeedPicker) o usar la cámara como fuente de entropía para crear rápidamente una mnemónica.

En la pantalla de inicio, seleccione **Nueva mnemónica**, y elija entre cámara, palabras, tiradas de un D6 (dado estándar de seis caras) o un D20 (dado de 20 caras).

<img src="/krux/img/maixpy_amigo/new-mnemonic-options-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-options-250.png" class="m5stickv">

## Cámara
(¡Experimental!) Elije entre 12, 24 palabras o una mnemotecnia doble. Luego, toma una foto al azar y Krux generará una mnemotecnia a partir del hash de los bytes de la imagen.

<img src="/krux/img/maixpy_amigo/new-mnemonic-via-snapshot-prompt-300.png" class="amigo">
<img src="/krux/img/maixpy_amigo/new-mnemonic-via-snapshot-capturing-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-snapshot-prompt-250.png" class="m5stickv">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-snapshot-capturing-250.png" class="m5stickv">

#### Estimación de la calidad de la entropía de la imagen
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-snapshot-entropy-estimation-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/new-mnemonic-via-snapshot-entropy-estimation-300.png" align="right" class="amigo">

Durante la captura de la imagen, se muestra la estimación de la calidad de la entropía para ayudarle a obtener una imagen de calidad para su clave. Tras tomar la instantánea, se presentan los índices de [Entropía de Shannon](https://en.wikipedia.org/wiki/Entropy_(information_theory)) y desviación de píxeles. Se establecen umbrales mínimos para evitar el uso de imágenes de baja calidad y baja entropía para la generación de claves.

**Nota**: Estos valores sirven solo como indicadores o estimaciones de la calidad de la entropía, pero no son valores absolutos de entropía en un contexto criptográfico.

<div style="clear: both"></div>

#### Doble mnemónico

Es la combinación de dos mnemónicos de 12 palabras que también forman un mnemónico BIP39 válido de 24 palabras. Esto se logra utilizando los primeros 16 bytes (128 bits) de la entropía de la imagen para generar las primeras 12 palabras, luego utilizando los siguientes 16 bytes para generar las segundas 12 palabras y verificando si estas dos mnemónicas juntas forman un mnemónico válido de 24 palabras. De lo contrario, iteramos sobre las segundas 12 palabras incrementando sus bytes de entropía hasta que las dos mnemónicas formen un mnemónico válido de 24 palabras.

Stepan Snigirev definió por primera vez la doble mnemotecnia en su [Generador de Doble Mnemotecnia](https://stepansnigirev.github.io/seed-tools/double_mnemonic.html). Puede usarse para una negación plausible o, como dijo Stepan, para divertirse y confundir a todos.

## Palabras
Imprime la [lista de palabras BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt) en 3D o en papel, luego recorta las palabras y colócalas en un cubo. Extrae manualmente 11 o 23 palabras del cubo.
Para la última palabra, Krux te ayudará a elegir una duodécima o vigesimocuarta palabra válida ajustando su teclado inteligente para que solo permita escribir palabras con una suma de comprobación válida. También puedes dejarlo vacío y Krux seleccionará una última palabra con una suma de comprobación válida.

## Tiradas de dados
### Mediante D6
Elige entre 12 o 24 palabras. La entropía en una sola tirada de un D6 es de 2,585 bits ( log<sub>2</sub>(6) ); por lo tanto, se requieren un mínimo de 50 tiradas para obtener 128 bits de entropía, suficiente para generar una regla mnemotécnica de 12 palabras. Para 24 palabras, se requieren un mínimo de 99 tiradas para obtener 256 bits de entropía.

<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d6-roll-1-300.png" class="amigo">
<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d6-last-n-rolls-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d6-roll-1-250.png" class="m5stickv">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d6-last-n-rolls-250.png" class="m5stickv">

### Mediante D20
La entropía en una sola tirada de un D20 es de 4,322 bits ( log<sub>2</sub>(20) ); por lo tanto, se requiere un mínimo de 30 tiradas para generar un mnemónico de 12 palabras y 60 tiradas para generar uno de 24 palabras.

<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d20-roll-1-300.png" class="amigo">
<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d20-last-n-rolls-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d20-roll-1-250.png" class="m5stickv">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d20-last-n-rolls-250.png" class="m5stickv">

### Estimación de la calidad de la entropía de las tiradas de dados
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d6-roll-string-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d6-roll-string-300.png" align="right" class="amigo">

Al introducir tus tiradas de dados, verás cómo se llenan dos barras de progreso. La barra superior muestra cuántas tiradas has realizado en comparación con el mínimo requerido. La barra inferior muestra un cálculo en tiempo real de la [entropía de Shannon](https://en.wikipedia.org/wiki/Entropy_(information_theory)) cen comparación con el mínimo requerido (128 bits para 12 palabras y 256 bits para 24 palabras). Cuando la estimación de la entropía de Shannon alcance el nivel recomendado, la barra de progreso se llenará y su marco cambiará de color. Si has alcanzado el número mínimo de tiradas, pero la estimación de la entropía sigue estando por debajo del nivel recomendado, aparecerá una advertencia que te sugerirá que añadas más tiradas para aumentar la entropía.

**Nota**: Al igual que la estimación de la calidad de la entropía de la imagen, la entropía de Shannon en las tiradas de dados sirve como indicador y no debe considerarse una medida absoluta de la entropía criptográfica.

Más información sobre la [Estimación de la Calidad de la Entropía de Krux](../features/entropy.md).

<div style="clear: both"></div>

### Estadísticas para Nerds
Un valor bajo de entropía de Shannon podría indicar que tus dados están sesgados o que hay un problema con la forma en que estás recolectando entropía. Para investigar más, consulta la sección "Estadísticas para Nerds" para comprobar la distribución de tus tiradas y buscar cualquier anomalía.

<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d6-roll-nerd-stats-300.png" class="amigo">
<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d20-roll-nerd-stats-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d6-roll-nerd-stats-250.png" class="m5stickv">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d20-roll-nerd-stats-250.png" class="m5stickv">


## (Opcional) Editar Mnemónico
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-edited-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/new-mnemonic-edited-300.png" align="right" class="amigo">

Una vez que se haya asignado suficiente entropía, puede agregar manualmente una entropía personalizada editando algunas palabras. Simplemente toque o navegue hasta la palabra que desea cambiar y reemplácela. Las palabras editadas se resaltarán y la última palabra se actualizará automáticamente para garantizar una suma de comprobación válida. Sin embargo, tenga cuidado, ya que modificar palabras puede afectar negativamente la entropía natural capturada previamente.

En la siguiente pantalla, cargará una billetera. Puede leer más sobre esto en [Cargar una billetera mnemónica -> Confirmar atributos de la billetera](./loading-a-mnemonic.md/#confirm-wallet-attributes).

<div style="clear: both"></div>

## Cómo funciona la entropía en Krux
Para las tiradas de dados, Krux registra cada tirada que introduces y muestra la cadena acumulada de resultados después de cada tirada.

Una vez introducida la tirada final, Krux generará un hash de esta cadena usando [SHA256](https://en.bitcoin.it/wiki/SHA-256) y mostrará el hash resultante en la pantalla para que puedas verificarlo.

Si se utiliza una instantánea de la cámara como fuente, los bytes de la imagen, que contienen datos de píxeles en formato RGB565, se generarán de la misma manera que las tiradas de dados.

<img src="/krux/img/maixpy_amigo/new-mnemonic-via-snapshot-sha256-300.png" class="amigo">
<img src="/krux/img/maixpy_amigo/new-mnemonic-via-d6-roll-sha256-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-snapshot-sha256-250.png" class="m5stickv">
<img src="/krux/img/maixpy_m5stickv/new-mnemonic-via-d6-roll-sha256-250.png" class="m5stickv">

Krux toma este hash y ejecuta [`unhexlify`](https://docs.python.org/3/library/binascii.html#binascii.unhexlify) en el para codificarlo como bytes y lo convierte de forma determinista en un mnemónico según la [Implementación de referencia BIP39](https://github.com/trezor/python-mnemonic/blob/6b7ebdb3624bbcae1a7b3c5485427a5587795120/src/mnemonic/mnemonic.py#L189-L207).

**Nota**: Para mnemónicos de 12 palabras, solo se utiliza la primera mitad del hash SHA256 (128 bits), mientras que para mnemónicos de 24 palabras se utiliza el hash completo (256 bits).

### Cómo verificar
No confíes, verifica. Le recomendamos que desconfíe de cualquier afirmación que no pueda verificar usted mismo. Por lo tanto, existen billeteras que utilizan algoritmos compatibles para calcular la entropía derivada de las tiradas de dados. Puede usar las billeteras de hardware [SeedSigner](https://seedsigner.com/) o [Coldcard](https://coldcard.com/), o incluso el [Sitio web de la Guía Bitcoiner](https://bitcoiner.guide/seed/), comparten la misma lógica que Krux y ofrecen la misma mnemotecnia para el método de tirada de dados.
