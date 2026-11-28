
## ¿Por qué Krux dice que la entropía de mis cincuenta tiradas de dados no contiene 128 bits de entropía?
Queremos que Krux ayude a los usuarios a comprender los conceptos relacionados en el proceso, presente estadisticas e indicadores, y anime a los usuarios a experimentar y evaluar los resultados. De esta forma, los usuarios aprenden las mejores prácticas en la generación de llaves. A continuación, profundizamos en los conceptos de entropía para reforzar los conocimientos de los usuarios sobre la autocustodia soberana.

## Entropía en las tiradas de dados

Tirar los dados y recopilar los valores resultantes puede ser un método eficaz para generar claves criptográficas debido a la aleatoriedad y la imprevisibilidad inherentes a cada tirada. Cada tirada de un dado produce un número aleatorio dentro de un rango específico y, cuando se combinan varias tiradas, se crea una secuencia difícil de predecir o reproducir. Esta secuencia puede utilizarse para generar claves criptográficas que sean resistentes a los ataques. Al garantizar que las tiradas de dados se realicen en un entorno controlado y seguro, y al utilizar un número suficiente de tiradas para alcanzar el nivel deseado de aleatoriedad, se pueden crear claves criptográficas altamente seguras y resistentes a los ataques de fuerza bruta u otras formas de criptoanálisis.

### Definiciones de Entropía

La entropía, un concepto fundamental en diversas disciplinas científicas, se asocia más comúnmente con un estado de desorden, aleatoriedad o incertidumbre dentro de un sistema. Utilizamos los conceptos de la [entropía termodinámica](https://en.wikipedia.org/wiki/Entropy_(classical_thermodynamics)), [entropía de Shannon](https://en.wikipedia.org/wiki/Entropy_(information_theory)), y [entropía criptográfica](https://en.wikipedia.org/wiki/Entropy_(computing)).

- **Entropía Termodinámica** se ocupa del calor y el trabajo. Describe cómo se distribuye la energía entre las partículas de un sistema, reflejando su tendencia hacia el equilibrio y el máximo desorden.

- **Entropía de Shannon**, de la teoría de la información, mide la incertidumbre o el contenido informativo de un mensaje o fuente de datos. Cuantifica la cantidad promedio de información producida por una fuente de datos estocástica, indicando la imprevisibilidad de los datos.

- **Entropía Criptográfica**, crucial en seguridad, se refiere a la imprevisibilidad y aleatoriedad necesarias para las claves y procesos criptográficos seguros. Una alta entropía criptográfica garantiza que las claves sean difíciles de predecir o reproducir, proporcionando robustez frente a ataques.

Mientras que la entropía termodinámica se ocupa de los sistemas físicos, la entropía de Shannon se centra en el contenido informativo, y la entropía criptográfica enfatiza la seguridad mediante la aleatoriedad.

### Medición de la entropía de los tiros de dados
La entropía es una medida teórica y no se puede medir directamente a partir de un solo tiro, sino a partir de la distribución de probabilidad de los resultados en muchos lanzamientos. Podemos utilizar la fórmula de Shannon para cálculos teóricos y empíricos. La entropía $S$ se puede cuantificar con:

$$
S = -\sum_{i=1}^{n} p_i \log(p_i)
$$

1. **Medición empírica:**

    - Tira los dados un gran número de veces para observar la frecuencia de cada resultado.
    - Estima las probabilidades $p_i$ basándote en las frecuencias observadas.

2. **Cálculo teórico:**

    - Utiliza la suposición de distribución uniforme (igual probabilidad para todos los resultados).

Donde:

- $p_i$ es la probabilidad de cada posible resultado (o estado) del sistema.
- $n$ es el número de posibles resultados.

## Entropía empírica (real) vs. Teórica en tiro de dados

Al calcular la entropía de los tiros de dados, la diferencia entre los resultados reales y teóricos surge de la suposición de imparcialidad y uniformidad perfectas frente a las imperfecciones inherentes a los experimentos del mundo real.

### Entropía teórica

El cálculo de la entropía teórica supone que los dados son perfectamente imparciales, lo que significa que cada cara tiene la misma probabilidad de caer boca arriba.

Considera un dado imparcial de seis caras. Los posibles resultados al lanzar un dado son {1, 2, 3, 4, 5, 6}, cada uno con una probabilidad igual de $\frac{1}{6}$.

1. **Tirar un solo dado:**

    - Cada resultado tiene una probabilidad $p_i = \frac{1}{6}$.
    - La entropía $S$ para una tirada de dado se calcula como:
$$
S = - \sum_{i=1}^{6} \left( \frac{1}{6} \log_2 \left( \frac{1}{6} \right) \right)
$$
Dado que $\log_2(1/6) = -\log_2(6)$ :
$$
S = -6 \left( \frac{1}{6} \times -\log_2(6) \right) = \log_2(6) \approx 2.585 \text{ bits}
$$

2. **Múltiples tiradas de dados:**

    - Para múltiples tiradas de dados, la entropía aumenta a medida que aumenta el número de resultados posibles. Para $k$ dados iguales, el número de resultados posibles es $6^k$.
    - La entropía $S$ para $k$ dados es:
$$
S = \log_2(6^k) = k \log_2(6) \approx 2.585k \text{ bits}
$$
    - Por ejemplo, la entropía para el lanzamiento de 50 dados iguales se calcula como:
$$
S = \log_2(6^{50}) = 50 \log_2(6) \approx 2.585 \times 50 \approx 129.25 \text{ bits}
$$

   Este cálculo asume que cada resultado (cada cara del dado) tiene la misma probabilidad, lo que resulta en una distribución uniforme.

### Entropía empírica

En una prueba real de tiros de dados, varios factores pueden causar desviaciones de la distribución uniforme perfecta:

1. **Dados imperfectos**: Los dados reales pueden no estar perfectamente equilibrados. Pequeños defectos de fabricación pueden hacer que ciertas caras sean ligeramente más pesadas o más ligeras, lo que provoca desviaciones.
2. **Condiciones de tiro**: La forma en que se lanzan los dados, la superficie sobre la que caen e incluso las corrientes de aire pueden introducir desviaciones ligeras.
3. **Tamaño de muestra finito**: Al lanzar los dados un número finito de veces, las frecuencias observadas de cada cara se desviarán naturalmente de la distribución uniforme esperada debido a variaciones aleatorias. Este fenómeno es más pronunciado con tamaños de muestra más pequeños.

Al lanzar un dado varias veces y observar los resultados, se pueden calcular las probabilidades empíricas $p_i$ de cada cara. Utilizando estas probabilidades, la entropía se calcula como:

$$
S = - \sum_{i=1}^{6} p_i \log_2(p_i)
$$

### Ejemplo


Supongamos que lanzas un dado de seis caras 50 veces y obtienes los siguientes resultados:

- 1: 4 veces
- 2: 9 veces
- 3: 7 veces
- 4: 10 veces
- 5: 12 veces
- 6: 8 veces

Podemos calcular la entropía de Shannon de la siguiente manera:

#### Paso 1: Calcular probabilidades

- Número total de tiradas:
$$
N = 4 + 9 + 7 + 10 + 12 + 8 = 50
$$
- Probabilidades para cada resultado:
$$
p_1 = \frac{4}{50} = 0.08 
$$
$$
p_2 = \frac{9}{50} = 0.18 
$$
$$
p_3 = \frac{7}{50} = 0.14 
$$
$$
p_4 = \frac{10}{50} = 0.2 
$$
$$
p_5 = \frac{12}{50} = 0.24 
$$
$$
p_6 = \frac{8}{50} = 0.16 
$$

#### Paso 2: Calcular la entropía

- Usando la fórmula de entropía de Shannon:
$$
S = -\sum_{i=1}^{n} p_i \log_2(p_i)
$$
- Calcular cada término:
$$
S_1 = -p_1 \log_2(p_1) = -0.08 \log_2(0.08) = -0.08 \times (-3.64386) = 0.291509
$$
$$
S_2 = -p_2 \log_2(p_2) = -0.18 \log_2(0.18) = -0.18 \times (-2.47393) = 0.445307
$$
$$
S_3 = -p_3 \log_2(p_3) = -0.14 \log_2(0.14) = -0.14 \times (-2.8365) = 0.39711
$$
$$
S_4 = -p_4 \log_2(p_4) = -0.2 \log_2(0.2) = -0.2 \times (-2.32193) = 0.464386
$$
$$
S_5 = -p_5 \log_2(p_5) = -0.24 \log_2(0.24) = -0.24 \times (-2.05889) = 0.494132
$$
$$
S_6 = -p_6 \log_2(p_6) = -0.16 \log_2(0.16) = -0.16 \times (-2.64386) = 0.423018
$$
- Suma de las contribuciones:
$$
S = S_1 + S_2 + S_3 + S_4 + S_5 + S_6 
$$
$$
S = 0.291509 + 0.445307 + 0.39711 + 0.464386 + 0.494132 + 0.423018 = 2.515462
$$
Por lo tanto, la entropía de Shannon para la distribución dada de tiradas de dados es de aproximadamente $2.52$ bits por tirada. Esto dará un valor diferente a $\log_2(6)$ debido a las desviaciones en las probabilidades empíricas.

- La entropía total para $N = 50$ tiradas es:
$$
S_{total} = S \times N = 2.515 + 50 \approx 125.8 \text{ bits}
$$

#### Entropía de Shannon en la práctica

El cálculo de la entropía de Shannon en una muestra real de tiradas de dados proporciona información sobre la aleatoriedad y la imparcialidad reales de los dados y las condiciones de lanzamiento. Las desviaciones de la entropía teórica reflejan las imperfecciones y varianzas naturales inherentes a los escenarios del mundo real. Esta comprensión ayuda a evaluar y mejorar la imparcialidad y la aleatoriedad de los dados o sistemas similares.

La entropía de Shannon evalúa la distribución de probabilidad estadística de muestras de un lanzamiento de dado. Una distribución uniforme resulta en una entropía mayor, más cercana a la entropía máxima teórica, que supone lanzamientos perfectamente distribuidos. Una distribución desigual, creada, por ejemplo, por un dado manipulado, resultará en una entropía de Shannon menor. En un caso extremo, con un dado terriblemente manipulado que siempre cae en la misma cara, la entropía de Shannon será cero.

## Entropía criptográfica

Si bien la entropía de Shannon es una medida potente del contenido de información y la incertidumbre en una distribución estadística para muestras naturales, no se considera entropía criptográfica debido a su incapacidad para detectar patrones u otras fuentes de predictibilidad dentro de los datos. La fórmula de Shannon cuantifica la información promedio producida por un proceso estocástico, midiendo esencialmente la sorpresa esperada en una secuencia de símbolos en función de sus probabilidades. Sin embargo, no tiene en cuenta la posible estructura, correlaciones o regularidades dentro de los datos que un usuario podría insertar y que un atacante podría explotar.

Por otro lado, la entropía criptográfica requiere un estándar de imprevisibilidad más elevado. Debe garantizar que cada bit de la clave criptográfica sea lo más aleatorio e independiente posible, lo que la hace resistente a cualquier tipo de análisis que pueda revelar patrones o reducir la aleatoriedad efectiva. Si bien la entropía de Shannon puede evaluar la distribución estadística de los símbolos, no garantiza la ausencia de patrones o dependencias, cruciales para mantener la seguridad de los sistemas criptográficos. Por lo tanto, la entropía criptográfica abarca un concepto más amplio de aleatoriedad, asegurando que las llaves generadas no solo sean estadísticamente aleatorias, sino también libres de cualquier estructura o predictibilidad detectable.

### Detección de patrones

Es posible obtener tiradas de dados con una distribución uniforme, pero con una entropía criptográfica deficiente. Este problema surge cuando existen patrones en las secuencias. Algunos ejemplos incluyen secuencias como `123456123456123...`, `111122223333...`, y `654321654321...`, que presentan una baja entropía criptográfica a pesar de tener una distribución uniforme y una alta entropía de Shannon.

Para mitigar este problema, Krux ha implementado un algoritmo de detección de patrones que evalúa la entropía de Shannon de las derivadas de las tiradas. En la práctica, este algoritmo detecta componentes de progresión aritmética en las tiradas de dados y emite una advertencia si se supera un umbral determinado.

## ¿Qué hace Krux?

- Krux requiere un número mínimo de tiradas basado en la entropía teórica.
- Krux advierte al usuario si detecta una baja entropía de Shannon, calculada con las tiradas reales.
- Krux advierte al usuario si sospecha que existen patrones en las tiradas reales.

## Conclusión

Si bien Krux no puede garantizar que las tiradas tengan una entropía criptográfica buena o mala, sí proporciona indicadores que ayudan a los usuarios a detectar problemas y a comprender los conceptos relacionados con la generación de mnemónicos.
