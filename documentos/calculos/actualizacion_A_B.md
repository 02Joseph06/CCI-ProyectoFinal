# Actualización de A y B — auditoría y régimen

## Estado y procedencia

Esta actualización sustituye los resultados preliminares de auditoría y
segmentación descritos en `registro.md`. El CSV original no se modifica. El
grupo confirmó la semilla y las convenciones de A3. Las salidas se recalculan
desde el CSV en `outputs/A1`, `outputs/A2`, `outputs/A3` y `outputs/B`.

## A1. Conversión, limpieza y conteos

1. Se leen 34.072 filas. Los 50 tamaños superiores a 5.000 se dividen entre
   1024, siguiendo la indicación del estudiante, antes de deduplicar. Este
   criterio de unidades es una decisión de tratamiento del grupo.
2. Tras convertir, hay 101 duplicados exactos. Se conserva la primera copia:
   quedan 33.971 identificadores distintos.
3. Entre estos identificadores hay 34 ausencias de red, 33 de GPU y 101
   latencias negativas. Una fila tiene tanto ausencia como latencia negativa.
4. Además hay 67 latencias inferiores a la suma de red y GPU fuera de la
   tolerancia. Se excluyen 234 solicitudes distintas en total; quedan 33.737.
   Los criterios se solapan y no se deben sumar ciegamente.

El control físico usa `L + 0,015001 ≥ red + GPU` en ms. Cada una de las tres
mediciones está expresada a centésimas de milisegundo: la suma de sus tres
semierrores de redondeo es `3 × 0,005 = 0,015 ms`. El margen adicional
`0,000001 ms` evita clasificar residuos binarios de punto flotante como
violaciones. La desigualdad estricta sin tolerancia excluiría observaciones
adicionales. Las filas excluidas y sus motivos están en
`outputs/A1/solicitudes_excluidas.csv`; la base retenida está en
`outputs/A1/solicitudes_auditadas.csv`.

## A2. Régimen y sensibilidad

Se usa el detector existente con log-verosimilitud de Poisson perfilada y BIC,
sin limitarlo artificialmente a tres segmentos. Para una ventana con `m`
intervalos, `Y` llegadas y `k` segmentos, la contribución perfilada de cada
segmento es `Y log(Y/m) − Y`, omitiendo constantes comunes; el criterio es
`−2 log L + (2k−1) log(m_total)`. Se comparan de uno a cinco segmentos con
duración mínima de 60 s.

Con agregación de 1 s, los tramos estimados son [0,668), [668,838) y
[838,1200] s, con 16.353, 8.781 y 8.603 solicitudes válidas. El grupo eligió
como régimen estable la unión de los dos tramos exteriores: 24.956 solicitudes
en una exposición de `668 + (1200−838) = 1030 s`. Los tiempos entre llegadas
deben calcularse dentro de cada tramo antes de concatenarlos; no se debe
introducir el salto de 170 s como una observación.

La sensibilidad con intervalos de 5 y 10 s selecciona límites (665,840) y
(670,840); con 15 y 30 s, BIC selecciona cuatro segmentos con cortes
660, 720 y 840. Los límites detectados **varían con la granularidad** y el
subcorte de 720 s también debe reportarse. La mezcla de tráfico alrededor del
inicio es una explicación posible, no una causa única demostrada. Los BIC
recalculados sobre la base depurada figuran en la salida y difieren de los de
la ejecución anterior sobre 33.971 registros.

La comparación de los tramos exteriores produce KS para tiempos entre llegadas
`D = 0,0142077`, `p ≈ 0,20328`; KS para latencia `D ≈ 0,007468`,
`p ≈ 0,90929`; y Mann–Whitney para latencia `p ≈ 0,54023`. El resultado de
tiempos usa diferencias calculadas dentro de cada tramo. La ausencia de rechazo
indica compatibilidad con las hipótesis de esas pruebas, no demuestra igualdad,
estacionariedad ni ausencia de sesgo. No se conoce el procedimiento anterior
que produjo `p = 0,2007`, por lo que no se puede atribuir con certeza la
diferencia numérica a una causa específica.

Exclusión de filas completas: como algunas observaciones con tiempos de llegada
válidos se excluyen por red/GPU/latencia, las tasas e intervalos entre llegadas
calculados con la base retenida describen las solicitudes retenidas y pueden
diferir de los del tráfico total. En los dos tramos elegidos se cuentan 25.132
identificadores antes de excluir por latencia y 24.956 después: 24,4 frente a
24,2291 solicitudes/s sobre 1030 s. Esta limitación afecta B1 y B4; no se ha
supuesto que las solicitudes eliminadas sean una muestra aleatoria.

## A3. Descriptivos

`outputs/A3/resumen_descriptivo.csv` contiene n, media, mediana, mínimo, máximo,
rango y cuartiles por versión y régimen, agrupando los dos tramos estables.
También reporta varianza y desviación muestral, asimetría corregida y exceso de
curtosis corregido. El grupo confirmó usar la segunda expresión desarrollada en
los apuntes de la página 7, `s² = Σ(xᵢ − x̄)²/(n−1)`, y `s = √s²`.

Para los momentos centrales empíricos `mₖ = Σ(xᵢ−x̄)ᵏ/n`, la asimetría
corregida es `√[n(n−1)]/(n−2) × m₃/m₂^(3/2)`. El exceso de curtosis corregido
es `(n−1)/[(n−2)(n−3)] × [(n+1)(m₄/m₂²−3)+6]`. Estas expresiones corresponden
a `pandas.Series.skew()` y `pandas.Series.kurt()`; el exceso para una normal
teórica es cero. Se usa cada fórmula solo cuando hay suficientes observaciones.

## B. Estado y controles

El código prepara ambos tramos estables con duración de 1030 s. Las diferencias
entre llegadas se calculan por separado. Para los conteos de B1 usa ventanas
completas de 10 s en [0,660) y [838,1198), omitiendo 8 s y 2 s solo en esa
comprobación. Los bloques de B2 se construyen por separado antes y después del
incidente para no unir solicitudes separadas por el tramo anómalo. Una prueba
sintética comprueba que no se contabiliza el salto entre tramos.

Los cálculos de B se ejecutan con `np.random.default_rng(S)` y la confianza del
90 %. El archivo `outputs/B/resultados.json` registra las cifras sin redondear,
y `B2_contraste.csv` y los archivos de bloques permiten revisarlas. Las
fórmulas de B1–B4 constan en `registro.md`; su referencia temporal anterior
debe leerse ahora como la unión estable de duración 1030 s. Las pruebas de ajuste
no prueban por sí solas independencia u homogeneidad. El informe debe indicar
los modelos, los supuestos y las decisiones del grupo, sin sustituir la
deducción manuscrita exigida para B3.

### B1. Llegadas y conteos

Con `n = 24.956` y `T = 1030 s`, la estimación usada es
`λ̂ = n/T = 24,229126 solicitudes/s`. El intervalo del 90 % basado en Poisson
es `[23,977402; 24,482930] solicitudes/s`. Aplicando la transformación
decreciente `1/λ`, la media entre llegadas del modelo es `0,041273 s` y su
intervalo transformado es `[0,040845; 0,041706] s`.

Se calcularon 24.954 diferencias por separado en los dos tramos; la mayor es
0,4849 s y hay 42 empates por resolución de la marca temporal. La distancia
KS frente a una exponencial ajustada es 0,005052; el valor p mediante 400
réplicas que reajustan el parámetro es aproximadamente 0,35162. El índice
varianza/media de los conteos en 102 ventanas completas de 10 s es 0,81613;
el contraste aproximado de dispersión da p ≈ 0,17738. El bootstrap KS simula
datos continuos y no reproduce ni la cuantización ni el condicionamiento por
límites de observación; por ello su calibración es aproximada. El intervalo de
tasa depende del modelo Poisson y de haber fijado los tramos tras mirar datos.

### B2. Reintentos por bloques

En 24.956 solicitudes estables, `p̂ = 0,152989` y, bajo la binomial de 100,
`E[X] = 100p̂ = 15,2989` y `Var(X) = 100p̂(1−p̂) = 12,9584`. Para los
249 bloques completos estables se observan media 15,3012 y varianza muestral
12,1226; quedan 56 solicitudes fuera de bloques completos.

En el tramo de carga alta hay 87 bloques completos, con media observada
31,2759 y varianza 18,3184, y 81 solicitudes fuera de los bloques. La media
de esos bloques supera en 15,9769 la media 15,2989 calculada con el parámetro
estable. Si se estima la proporción por separado en carga alta se obtiene
`p̂ = 0,313404`, con media binomial 31,3404 y varianza 21,5182. La tabla da
ambos puntos de referencia; estas cifras descriptivas no establecen una causa
ni un contraste formal de equivalencia.

### B3. Intentos y verosimilitud

La deducción algebraica del modelo de intentos independientes truncados en
tres aparece en `registro.md`: `F = Σ(kᵢ−eᵢ)`, `A = Σkᵢ`,
`ℓ(q) = F log(q)+(A−F)log(1−q)` y `q̂ = F/A`. En la muestra retenida,
`F = 4501`, `A = 29360` y `q̂ = 0,153304`; el intervalo de perfil de
verosimilitud al 90 % es `[0,149867; 0,156784]`. Depende de los supuestos de
igual probabilidad e independencia de intentos.

El estimador inmediato `1−1/k̄` es 0,150000. Con 1.000 simulaciones al valor
ajustado, el sesgo y la raíz del error cuadrático medio fueron aproximadamente
`0,00000021` y `0,002133` para `F/A`, frente a `−0,003056` y `0,003670`
para el estimador inmediato. Son resultados de esa simulación calibrada; la
deducción manuscrita y la valoración de adecuación corresponden al grupo.

### B4. Reintentos en diez segundos

Con `p̂_reintento = 0,152989`, la media bajo adelgazamiento Poisson es
`μ̂ = 10 λ̂ p̂_reintento = 37,067961` solicitudes. Como `r = 3`,
`k = ⌈37,067961⌉ + 3 = 41`. La cola analítica del modelo es
`P(X≥41) = 0,280158`. En 200.000 réplicas Poisson la proporción fue 0,278570,
con intervalo Monte Carlo del 90 % `[0,276921; 0,280224]`, que contiene la
cifra analítica. Este intervalo cuantifica el error de simulación, no la
incertidumbre de estimación de `λ` y `p`. La cifra depende de Poisson,
adelgazamiento independiente y del filtro de A1.

## Semilla y parámetros confirmados

Se proporcionaron `C1 = 1023092749`, `C2 = 1023092750` y su suma
`S = 2046185499`. El grupo confirmó aplicar la tabla del PDF, página 2:
confianza 0,90, `τ = 210 ms`, `ε = 0,01`, `g = 1,5`, `t₁ = 120 KB`,
`t₂ = 500 KB`, `π = 0,007`, `kₘáx = 8`, `r = 3` y `N = 16`. Estos valores
resuelven la contradicción anterior con los parámetros comunicados inicialmente.
