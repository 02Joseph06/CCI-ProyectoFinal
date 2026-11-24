# G3. Incertidumbre de parámetros y capacidad

Se generan 200 escenarios a partir del régimen estable auditado: n = 24.956 solicitudes, duración de 1.030 s y 14.696 sin caché. Se usa `np.random.default_rng(2046185499)`. La tasa base se extrae de Gamma(n, escala = 1/1030) y se multiplica por 1,5. La probabilidad de caché se extrae de Beta(k+0,5, n-k+0,5). Para los logaritmos de GPU se usan $\sigma^2=(n_+-1)s^2/\chi^2_{n_+-1}$ y $\mu\mid\sigma^2\sim N(\bar y,\sigma^2/n_+)$. Las estadísticas se calculan con la precisión completa de los datos, no con las cifras redondeadas del enunciado del usuario. La red normal conserva media y desviación muestral fijas. Los sorteos de tasa, caché y parámetros de GPU se generan independientemente: esta independencia es un supuesto de modelación, no una dependencia empírica comprobada.

Para cada escenario se evalúan 2, 3, 4 y 5 GPU con cinco réplicas independientes de 400 s totales: 20 s de calentamiento y 380 s medidos. Se escoge el menor $c$ evaluado cuya media de las cinco proporciones de $L>210$ ms es como máximo 0,01. Si ninguna capacidad cumple, se conserva como “sin capacidad en la rejilla”. El intervalo t entre cinco réplicas cuantifica solamente ruido interno de simulación; no garantiza la clasificación cerca del umbral. Las frecuencias de 200 escenarios tienen también error Monte Carlo. La variabilidad paramétrica y la de simulación se mezclan en la distribución resultante de $c^*$.

## Contraste analítico

Se compara cada escenario con un modelo $M/M/c$: llegadas sin caché Poisson de tasa $\lambda(1-p_c)$, servicio exponencial con media igual a la lognormal del escenario, y red normal independiente. Para caché $L=R$; para no caché $L=R+W_q+S$. Bajo Erlang C, $P(W_q>0)$ viene de la fórmula de Erlang C y, condicionada a espera positiva, $W_q$ es exponencial con tasa $c\mu-\lambda(1-p_c)$; $S$ es exponencial independiente de $W_q$. Se integra numéricamente sobre la red normal la cola de la suma. Es un contraste simplificado de servicio exponencial, no una validación del modelo lognormal ni una prueba de que el tamaño recomendado sea seguro.

## Evidencia y limitaciones

`outputs/G3/escenarios_G3.csv` contiene los parámetros; `detalle_escenarios_G3.csv`, cada combinación y su intervalo de simulación; `distribucion_capacidad_G3.csv`, todas las categorías de $c^*$ incluyendo sin cumplimiento; y `robustez_c_G3.csv`, probabilidades de cumplimiento por capacidad y contraste M/M/c. Los intervalos entre réplicas no reflejan por sí solos incertidumbre estadística de parámetros. La sobreestimación de cola en G1 es una diferencia observada, cuyas causas no se han identificado; la ausencia de modelado de correlaciones, reintentos o colas finitas son posibles limitaciones, no causas demostradas. Las métricas de F6 no prueban invariancia ni resuelven si las filas incluyen intentos como llegadas separadas.


## Ejecución y resultados

Con las 24.956 filas estables y 10.260 aciertos de caché se ejecutaron los 200 escenarios con semilla 2046185499. El mínimo puntual fue 3 GPU en 81 escenarios (40,5 %), 4 GPU en 115 (57,5 %) y 5 GPU en 4 (2 %); ninguno quedó sin solución dentro de la rejilla. La proporción que cumple para cada capacidad evaluada es 0 %, 40,5 %, 97,5 % y 99 % para 2, 3, 4 y 5 GPU, respectivamente. El IC Wilson del 90 % para 4 GPU es [94,954 %, 98,778 %]: representa error Monte Carlo entre los 200 escenarios, sin corregir el ruido de las cinco réplicas interiores ni la especificación del modelo.

Hay tres escenarios con clasificación no monótona entre capacidades consecutivas; en uno, 3 GPU cumple y 4 GPU no. Por eso P(c* ≤ 4) = 98 % difiere de P(c = 4 cumple) = 97,5 %. Las réplicas son independientes entre capacidades y cinco por escenario generan ruido de simulación cerca del umbral; estas cifras no establecen un efecto físico de mayor capacidad.

El contraste M/M/c para la misma mezcla de red y caché da violaciones medias de 5,777 %, 2,336 %, 2,083 % y 2,053 %, respectivamente. Ninguno de los 200 escenarios satisface el umbral para capacidades de 2 a 5 con servicio exponencial. Esta diferencia expresa sensibilidad a la distribución de servicio; no demuestra seguridad ni causalidad. La integral se evaluó sobre el soporte numérico [-10, 10] de la normal estandarizada: una versión anterior omitía la masa central; la versión corregida se contrastó frente a Monte Carlo independiente.

El criterio de G3 usa la **estimación puntual** media frente al 1 %; G2 usa el **límite superior del intervalo**, una regla distinta. Los intervalos t entre cinco réplicas son descriptivos y pueden salir del rango [0,1]. Las estimaciones de 200 escenarios no aseguran robustez frente a incertidumbre estructural.

La posterior Gamma(n, escala 1/T) de la tasa corresponde, con verosimilitud Poisson, a una previa impropia proporcional a 1/λ; la previa Beta(1/2,1/2) se usa para caché. Se asumen independientes las posteriores de tasa, caché y servicio y el proceso de llegadas Poisson. La tasa se estima de las filas retenidas tras auditoría: no está establecido que cada fila sea un intento enviado al balanceador. La red normal puede generar tiempos negativos con probabilidad pequeña.
