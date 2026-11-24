# Registro de trabajo — partes A y B

> **Registro histórico:** la actualización posterior de A1 y A2 y su estado
> vigente se encuentran en `actualizacion_A_B.md`. Las cifras y advertencias
> anteriores conservadas a continuación no describen las salidas actuales.

> **Actualización pendiente de conciliación:** el estudiante indicó convertir
> los 50 tamaños superiores a 5.000 dividiéndolos entre 1024 antes de deduplicar.
> El código de auditoría ya aplica esa indicación y, al probarlo en una carpeta
> temporal, obtuvo 101 duplicados exactos. Las salidas conservadas en `outputs`
> todavía corresponden a la auditoría anterior: no se han regenerado porque
> falta aclarar la tolerancia de la comprobación de latencia. Las secciones de
> abajo describen las decisiones y los resultados anteriores, no una auditoría
> definitiva. El grupo también solicitó usar los tramos estables [0,668) y
> [838,1200], decisión pendiente de integrar con la auditoría revisada.

> **Comprobaciones pendientes de decisión:** con la tolerancia de 0,015001 ms
> se obtienen 33.737 filas y los conteos por tramo 16.353, 8.781 y 8.603. Con
> desigualdad estricta se detectan 2.792 violaciones físicas no negativas en
> lugar de 67 y quedan 31.012 filas. Los valores faltantes y las latencias
> negativas tienen una intersección de una fila. El contraste KS de tiempos
> entre llegadas recalculado con SciPy da D=0,0142077 y p≈0,203282; el estudiante
> reportó p=0,2007. Con el criterio BIC existente de 1 a 5 segmentos, ventanas
> de 15 y 30 s seleccionan un segmento adicional con límite en 720 s. Estas
> diferencias se han comunicado y esperan decisión antes de regenerar salidas.
> Las pruebas que no rechazan una diferencia no demuestran por sí solas que
> los tramos sean idénticos o estacionarios; la unión de los tramos es la
> decisión solicitada por el estudiante y requiere declarar sus supuestos.

## Estado

La auditoría A1 y la segmentación exploratoria A2 son reproducibles con
`src/auditoria.py` y `src/regimenes.py`. El trabajo de A3 y B está pendiente de
la semilla del grupo y de aclarar la fórmula de varianza de los apuntes. Las
salidas aún no constituyen las partes A y B completas.

Fuentes: enunciado oficial, páginas 3–4; apuntes del curso, página 7; y
`data/raw/solicitudes.csv`. La ventana de validación se reserva para F6.

## A1. Auditoría y decisiones

Se procesan 34.072 filas sin modificar el original. Se eliminan 99 duplicados
exactos. Dos identificadores aparecen con valores distintos de `tam_kb`: en
cada caso uno es 1024 veces el otro. Se conserva una solicitud por identificador
y se deja el tamaño como dato faltante; los demás campos coinciden y se
conservan. Quedan 33.971 solicitudes.

Además hay 48 tamaños por encima de 5.000 KB; el menor es 31.221,76 KB y el
mayor de los restantes es 1.776,07 KB. Los 48 pasan a ser valores faltantes
solo para análisis de tamaño: cada uno dividido entre 1024 coincide con un
valor expresado a centésimas, pero no se puede probar su unidad. Se requiere
análisis de sensibilidad antes de afirmar cualquier conversión. Los campos
faltantes originales no se imputan: 34 de red y 33 de GPU.

Para cada observación se verifica que los tiempos sean no negativos y que
`latencia_ms ≥ red_ms + gpu_ms`: la ecuación física del enunciado incluye
además una espera no negativa. Como las tres medidas se presentan a
centésimas, se acepta una tolerancia de 0,015 ms, suma de tres semierrores de
redondeo de 0,005 ms. Se marcan como faltantes 101 latencias negativas y 67
inferiores a la suma fuera de la tolerancia. Esto no invalida automáticamente
los demás campos de la fila. También se revisan dominios de caché, versión,
intentos, éxito, tamaños y ventana temporal.

Los resultados por criterio están en `outputs/A1/resumen_auditoria.csv`; los
criterios se pueden solapar, por lo que sus conteos no deben sumarse como si
fuesen filas distintas. La base resultante y los motivos por fila están en
`outputs/A1/solicitudes_auditadas.csv`.

## A2. Segmentación de llegadas

En intervalos de ancho fijo se modela provisionalmente cada conteo como Poisson
con tasa constante por segmento. Para un segmento con conteos `y_i`, su suma es
`Y` y contiene `m` intervalos. La media de conteo estimada es `Y/m`, y la
log-verosimilitud perfilada, omitiendo constantes comunes, es
`Y log(Y/m) − Y`. Se maximizan las log-verosimilitudes mediante programación
dinámica para uno a cinco segmentos, imponiendo al menos 60 s por segmento.
Se selecciona el menor `BIC = −2 log L + (2k−1) log(m_total)`, contando `k`
tasas y `k−1` puntos de cambio. La penalización de los cambios es una
aproximación; no constituye prueba exacta de homogeneidad.

Con intervalos de 10 s, BIC selecciona tres tramos: [0,670), [670,840) y
[840,1200] s, con 16.566, 8.790 y 8.615 solicitudes, respectivamente. Sus
tasas son el conteo dividido por la duración: aproximadamente 24,73, 51,71 y
23,93 solicitudes/s. Se usa provisionalmente [0,670) como régimen estable:
evita unir periodos no contiguos y permite estudiar los tiempos entre llegadas.
La afirmación de Poisson y de estabilidad interna aún requiere las validaciones
de B1; estabilidad aquí significa ausencia de cambio detectado por este criterio.

La sensibilidad se evalúa con intervalos de 5, 10, 20 y 30 s; con 5 s los
cambios son 665 y 840 s; con 20 y 30 s BIC divide además el periodo de alta
carga. Esto implica incertidumbre en el primer límite y posible heterogeneidad
dentro de la carga alta. La tabla completa está en
`outputs/A2/sensibilidad_segmentacion.csv` y la figura en
`outputs/A2/figura_1_llegadas.png`.

## A3. Estadísticos descriptivos

En `outputs/A3/resumen_parcial.csv` se reportan media, mediana, extremos,
rango, cuartiles y rango intercuartílico por versión y por los tres tramos de
A2. `n` se calcula para cada variable después de sus exclusiones. El rango
es `máximo − mínimo` y el rango intercuartílico es `Q3 − Q1`. Los cuartiles
usan interpolación lineal, por lo que debe indicarse ese método al reportarlos.

Pendiente: resolver la discrepancia entre las dos expresiones manuscritas de
varianza muestral en la página 7 de los apuntes antes de calcular la varianza,
desviación, asimetría y curtosis de acuerdo con los métodos del curso.

## B1–B4. Análisis y simulaciones

Pendientes de validación con la semilla real `S = C1 + C2`. Sin `S` no se
pueden fijar el nivel de confianza, `r` ni la fuente aleatoria exigida.

### B1. Modelo propuesto

Para el tramo estable [0,670), el modelo de referencia es Poisson homogéneo,
con `λ̂ = n/T`, donde `n` es el número de llegadas y `T = 670 s`. Bajo ese
modelo, `N(t) ~ Poisson(λt)` y los intervalos entre llegadas son exponenciales
con media `1/λ`. El intervalo exacto para la tasa, condicionado al modelo, es
`[χ²_(α/2,2n)/(2T), χ²_(1−α/2,2(n+1))/(2T)]`.

El código contrasta cuantitativamente la distribución de tiempos mediante la
distancia de Kolmogórov frente a exponenciales simuladas y reajustadas; para
los conteos, calcula su índice de dispersión `s²/ȳ` y un contraste basado en
chi cuadrado. Estas pruebas verifican aspectos distintos; ninguna por sí sola
demuestra independencia ni homogeneidad. El redondeo temporal produce empates
y debe considerarse al interpretar el contraste. La ejecución y las cifras
reales están pendientes de la semilla, por lo que el ajuste aún no está validado.

### B2. Bloques de 100

Sea `p̂` la proporción de solicitudes que necesitan más de un intento. Si las
solicitudes tienen la misma probabilidad y son independientes, el número de
ellas en un bloque completo de 100 sigue `Binomial(100,p̂)`, con media `100p̂`
y varianza `100p̂(1−p̂)`. Se comparan por separado el tramo estable y el tramo
de carga alta. El último bloque incompleto se registra y no se mezcla con los
de 100; deben interpretarse tanto la diferencia de medias como la dispersión
observada frente a la esperada, y examinar dependencia o mezcla temporal antes
de atribuir una discrepancia a una causa particular.

### B3. Verosimilitud con máximo de tres intentos

Sea `q` la probabilidad de fallo de un intento y supónganse intentos independientes
con igual probabilidad. Para cada solicitud observamos `kᵢ ∈ {1,2,3}` y el
indicador de éxito `eᵢ`. El número de fallos observados es `kᵢ−eᵢ`. Por tanto,
con `F = Σ(kᵢ−eᵢ)` y `A = Σkᵢ`, la verosimilitud es
`L(q) = q^F (1−q)^(A−F)`, y
`ℓ(q) = F log(q) + (A−F) log(1−q)`.

Derivando, `ℓ'(q) = F/q − (A−F)/(1−q)`. Igualar a cero da `q̂ = F/A`;
`ℓ''(q) = −F/q² − (A−F)/(1−q)² < 0` en el interior, de modo que es un máximo.
El intervalo implementado usa el perfil de verosimilitud con corte
`2[ℓ(q̂)−ℓ(q)] ≤ χ²_(1,1−α)`, aproximado y sujeto a los supuestos anteriores.
El estimador inmediato `1−1/k̄` supone implícitamente intentos sin truncamiento;
se compara su sesgo y raíz del error cuadrático medio con los del estimador de
verosimilitud mediante simulación a `q̂`, respetando el máximo de tres intentos.
Faltan resultados reales e interpretación de la simulación.

### B4. Adelgazamiento y verificación

Si las llegadas son Poisson homogéneas y cada solicitud requiere más de un
intento independientemente con probabilidad constante `p`, el adelgazamiento
da `R(10) ~ Poisson(10λp)`. Las estimaciones son `μ̂ = 10 λ̂ p̂` y
`k = ⌈μ̂⌉ + (S mod 6)`. La probabilidad analítica es
`P(R(10) ≥ k) = 1 − Σ_(j=0)^(k−1) exp(−μ̂) μ̂^j/j!`. Se compara con la
proporción de 200.000 réplicas Poisson calibradas, acompañada de intervalo para
el error Montecarlo. El resultado depende de los supuestos de B1 y B2; si fallan,
esta cifra es solo una referencia bajo el modelo y no una garantía empírica.
