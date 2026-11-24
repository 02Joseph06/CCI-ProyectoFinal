# Registro matemático — partes C y D

Estado al momento de la actualización. Fuente de observaciones:
`data/raw/solicitudes.csv`, a través de la auditoría de A1. Régimen estable
solicitado por el grupo: [0,668) ∪ [838,1200] s; S = 2046185499; confianza
90 %; t₁ = 120 KB; t₂ = 500 KB; N = 16. Los cálculos de C/D no usan el CSV de
validación. Las deducciones manuscritas siguen pendientes del estudiante.

## C1 — Caracterización de G

- **Objetivo:** representar la masa de caché y la parte positiva de GPU.
- **Fórmulas del estudiante:** F_G(g) = 0 si g < 0; para g ≥ 0,
  F_G(g) = p + (1−p)F₊(g); E[G] = (1−p)μ₊;
  Var(G) = (1−p)σ₊² + p(1−p)μ₊².
- **Variables y unidades:** G y μ₊, ms; σ₊², ms²; p es la proporción de
  solicitudes cacheadas; F₊ es la FDA de G dado que no hay caché.
- **Método indicado:** mezcla puntual en cero y ambas FDA de la parte positiva:
  empírica y lognormal ajustada. Varianzas empíricas con divisor n para la
  identidad y varianza con n−1 como referencia muestral.
- **Referencia:** apuntes suministrados, páginas 4–6 y 7–8, FDA y momentos.
- **Ubicación:** notebook, celda 14; implementación `src/tiempos_cd.py`.
  Salidas: `outputs/C1/resultados.json` y `figura_2_fda_gpu.png`.
- **Comprobaciones previas:** p = 0,41112358, n₊ = 14696, media positiva
  53,288026 ms. Con divisor n en ambas varianzas se obtiene
  Var(G) = 1491,774994 ms² por ambas vías. Con divisor n−1 en G se obtiene
  1491,834773 ms². Mezclar varianza condicional con divisor n₊−1 y pesos
  empíricos produce 1491,829727 ms²: esa diferencia no es solo la conversión
  global n/(n−1), pues también cambia el denominador de la varianza condicional.
- **Estado:** IMPLEMENTADO y VERIFICADO numéricamente. La deducción manuscrita
  requerida por el proyecto corresponde al estudiante.

## C2 — Ajuste de la parte positiva

- **Objetivo:** ajustar Gamma y lognormal a G dado no caché, y comparar Gamma
  por momentos y por máxima verosimilitud.
- **Fórmulas dadas por el estudiante:**
  ℓ_Γ(k,θ) = (k−1)Σln(gᵢ) − Σgᵢ/θ − n[lnΓ(k)+k ln θ];
  ℓ_LN(μ,σ) = −Σln(gᵢ) − n ln(σ√(2π)) − Σ(ln(gᵢ)−μ)²/(2σ²).
  Momentos Gamma: k̃ = x̄²/s² y θ̃ = s²/x̄, con s² de divisor n−1.
- **Variables y unidades:** gᵢ y θ, ms; k y σ, adimensionales; μ corresponde al
  logaritmo de los valores de G expresados en ms; n = 14696.
- **Método indicado:** minimizar la log-verosimilitud negativa con BFGS y sin
  `.fit()`. Se optimizan parámetros positivos en escala logarítmica y se
  proporciona el gradiente analítico; la tolerancia sobre el gradiente medio es
  10⁻⁸. Los dos optimizadores reportaron convergencia.
- **Referencia:** apuntes suministrados, páginas 4–5 y 7–8, variables continuas,
  media y varianza; la verosimilitud es la fórmula facilitada por el estudiante.
- **Ubicación:** notebook, celda de código 16; implementación
  `src/tiempos_c2.py`. Salidas: `outputs/C2/ajustes.json` y `ajustes_gpu.png`.
- **Verificaciones:** k = 2,52565986 y θ = 21,09865503 ms, ℓ = −70333,5700;
  momentos k̃ = 2,07890612 y θ̃ = 25,63272364 ms. Lognormal μ = 3,76487131,
  σ = 0,65929251, ℓ = −70059,0926. Distancias KS descriptivas 0,0397561 y
  0,0107189. Las pruebas automáticas comprueban las ecuaciones de máximo y
  rechazan observaciones no positivas.
- **Limitación:** las distancias KS usan datos con los mismos parámetros
  ajustados; no se presenta un valor p calibrado ni se concluye adecuación a
  partir de esas distancias. La discusión estructural queda para el estudiante.
- **Estado:** IMPLEMENTADO y VERIFICADO técnicamente. El grupo confirmó una
  formulación cautelosa: un ajuste marginal por sí solo no implica
  independencia. Un cambio de mezcla de tamaños puede modificar la cola, pero
  su dirección y efecto requieren evidencia adicional. El R² lineal observado
  no demuestra causalidad ni cuantifica por sí solo los cambios futuros.

## C3 — Tiempo de red

- **Objetivo y método indicado:** media y desviación de red, asimetría,
  curtosis, KS y Anderson–Darling, colas para 35, 40 y 45 ms, percentil 99,9 %
  e intervalo bootstrap al 90 %.
- **Fórmula general:** P(R > x) bajo el modelo normal =
  1−Φ((x−μ_R)/σ_R). R, x y σ_R se expresan en ms.
- **Referencia:** apuntes suministrados, páginas 9–11, normal e intervalos.
- **Ubicación:** notebook, celda 18; código `src/tiempos_cd.py`; salidas y
  Figura 3 en `outputs/C3/`.
- **Resultados:** asimetría −0,0038978 y exceso −0,0192937, confirmados por el
  estudiante. KS nominal D = 0,00455276, p = 0,677277; al estimar media y
  desviación con la misma muestra, ese p no es una calibración exacta para
  normalidad compuesta. Con 2000 réplicas de bootstrap y S del grupo, el
  percentil 99,9 % es 43,33 ms y el intervalo percentil al 90 % es
  [42,96405; 43,70495] ms; el remuestreo no preserva dependencia temporal.
- **Referencia y procedencia:** el estudiante indicó usar como referencia el
  crítico 0,656 al 10 %; A² = 0,591089 < 0,656, por lo que con esa referencia
  no se rechaza. En este entorno SciPy 1.18.1 devuelve 0,631; con ese umbral
  tampoco se rechaza. No se atribuye 0,656 a la versión instalada: su código
  local `_morestats.py` usa `_Avals_norm[1] = 0,631` y aplica la corrección
  muestral antes de redondear. La procedencia de la tabla 0,656 no se ha
  verificado aquí. No rechazar no demuestra que la distribución sea normal.
  `requirements.txt` fija SciPy 1.18.1: la biblioteca advierte que la interfaz
  de los valores críticos cambia a partir de 1.19; actualizarla requiere
  adaptar y volver a verificar C3.
- **Estado:** IMPLEMENTADO y VERIFICADO computacionalmente; comparación con
  referencia indicada documentada junto al valor de la versión instalada.

## C4 — Tiempo total en N solicitudes sin caché

- **Objetivo:** implementar dos aproximaciones y una comparación Monte Carlo.
- **Fórmulas dadas:** u = N(μ̂₊ + 15 ms); aproximación normal con media
  Nμ̂₊ y varianza Nσ̂₊²; aproximación Gamma con forma Nk̂ y escala θ̂.
- **Variables:** N = 16; μ̂₊ y θ̂, ms; σ̂₊², ms²; T_N y u, ms.
- **Referencia:** apuntes suministrados, páginas 9–11, normal y estandarización.
- **Ubicación:** notebook, celda 20; implementación `src/tiempos_cd.py` y
  `outputs/C4/resultados.json`.
- **Método confirmado:** 200000 bloques i.i.d. de 16 extracciones con reemplazo
  desde la distribución empírica de solicitudes sin caché. Umbral 1092,6084 ms;
  aproximación normal 0,052247; Gamma 0,044947; remuestreo 0,063425 con IC del
  90 % por error de simulación [0,062531; 0,064329].
- **Limitación:** el remuestreo no conserva dependencia temporal ni convierte
  la distribución empírica en la verdadera distribución de la población.
- **Estado:** IMPLEMENTADO y VERIFICADO técnicamente; la elección e
  interpretación para el informe corresponde al estudiante.

## D1 — Distribución conjunta e independencia

- **Objetivo:** tabla conjunta de clase de tamaño y caché, marginales,
  condicionales, contraste y figura 4.
- **Fórmulas:** p̂ᵢⱼ = nᵢⱼ/n; p̂ᵢ· = Σⱼp̂ᵢⱼ; p̂·ⱼ = Σᵢp̂ᵢⱼ;
  P̂(cache=j | clase=i) = nᵢⱼ/nᵢ·;
  χ² = Σᵢⱼ(Oᵢⱼ−Eᵢⱼ)²/Eᵢⱼ, Eᵢⱼ = nᵢ·n·ⱼ/n.
- **Variables:** tamaño en KB, clases [0,120), [120,500), [500,∞);
  cache_hit ∈ {0,1}; n = 24956.
- **Método indicado:** frecuencias empíricas, χ² de Pearson e intervalos Wald
  al 90 %: p̂ ± z₀.₉₅ √[p̂(1−p̂)/nᵢ].
- **Referencia:** apuntes suministrados, páginas 1–3 y 6, probabilidad conjunta,
  condicional y variables discretas.
- **Ubicación:** notebook, celda de código 22; `src/dependencias_d1.py`.
  Tablas, `resumen.json` y `figura_4_conjunta.png` en `outputs/D1/`.
- **Verificaciones:** la conjunta suma 1, las condicionales suman 1 por grupo;
  χ² = 950,161634, gl = 2, p ≈ 4,73176×10⁻²⁰⁷. El mínimo esperado es 821,01.
  Una prueba automática verifica los límites 120 y 500 KB y las sumas.
- **Estado:** IMPLEMENTADO y VERIFICADO para tablas, contraste e intervalos.
  La interpretación del contraste corresponde al estudiante.

## D2 — Esperanzas y varianzas condicionales

- **Objetivo:** medias condicionales, esperanza y varianza total, y fracción
  explicada por clase.
- **Fórmulas del estudiante:** E[G] = Σᵢpᵢ E[G|claseᵢ];
  Var(G) = Σᵢpᵢ Var(G|claseᵢ) + Σᵢpᵢ(E[G|claseᵢ]−E[G])².
- **Unidades:** medias en ms; varianzas en ms²; fracciones adimensionales.
- **Referencia:** apuntes suministrados, páginas 7–8, momentos y esperanza.
- **Ubicación:** notebook, celda 24; `src/esperanza_d2.py`; tablas, figura y
  resultados en `outputs/D2/`.
- **Método y verificación:** con divisor n, 1171,703194 + 320,071801 =
  1491,774994 ms². La media ponderada también coincide. Se implementaron los
  25 grupos de cuantiles y LOWESS con fracción 0,15, confirmados por el grupo.
  El suavizado usa regresión local lineal y pesos tricúbicos, sin iteraciones
  robustas, en 120 puntos hasta el percentil 99,5 % de tamaño; se trazan por
  separado las curvas para todas las solicitudes y para las no cacheadas.
  Tanto 25 grupos como 0,15 son elecciones del método; no prueban ausencia de
  sesgo. La prueba sintética verifica que LOWESS reproduce una recta.
- **Estado:** IMPLEMENTADO y VERIFICADO técnicamente; la interpretación de la
  curva corresponde al estudiante.

## D3 — Regresión y corrección de residuos

- **Objetivo:** programar OLS matricial, intervalos, diagnóstico y WLS indicados.
- **Fórmulas del estudiante:** β̂ = (XᵀX)⁻¹Xᵀy; WLS con wᵢ = 1/tamᵢ² y HC3.
- **Unidades:** intercepto, ms; pendiente, ms/KB; residuos, ms.
- **Referencia:** enunciado oficial, página 5; cálculo matricial del estudiante.
- **Ubicación:** notebook, celda 26; `src/regresion_d3.py`; resultados y
  Figura 5 en `outputs/D3/`.
- **Verificación:** para WLS, coeficientes 14,94877 y 0,144704;
  errores clásicos 0,082957 y 0,001259, frente a HC3 calculados como
  1,010698 y 0,006870. Los dos errores facilitados como HC3 coinciden con los
  clásicos. Ambos se reportan con sus etiquetas, según confirmó el estudiante.
  HC3 no garantiza corrección frente a cualquier fuente de dependencia o sesgo;
  el mayor leverage ponderado observado es 0,3143.
- **Intervalos:** el estudiante indicó t de Student con 14694 grados de
  libertad; el crítico al 90 % bilateral es 1,64495733. La tabla
  `outputs/D3/intervalos_coeficientes.csv` contiene intervalos OLS y WLS,
  clásicos y HC3. Los intervalos HC3 son aproximados.
- **Estado:** IMPLEMENTADO y VERIFICADO técnicamente. La deducción manuscrita
  e interpretación corresponden al estudiante.

## D4 — Covarianza y correlación

- **Objetivo:** calcular covarianza y Pearson para solicitudes no cacheadas.
- **Fórmulas:** covarianza muestral `Σ(xᵢ−x̄)(yᵢ−ȳ)/(n−1)`;
  `r = cov(x,y)/(sₓsᵧ)`; `R² = r²` para el caso lineal con intercepto.
- **Unidades:** x = tamaño (KB), y = GPU (ms); covarianza en KB·ms; r y R²
  son adimensionales. Se usa divisor n−1, confirmado por el grupo para A3.
- **Referencia:** apuntes suministrados, página 7, medidas muestrales.
- **Ubicación:** notebook, celda de código 28; `src/dependencias_d4.py`.
  Salidas: `outputs/D4/correlacion.json` y `tamano_gpu.png`.
- **Verificaciones:** n = 14696; covarianza 4526,561308 KB·ms;
  r = 0,693838456; R² = 0,481411804. Una prueba con datos sintéticos verifica
  filtro estable, divisor y r. La librería devuelve p = 0 por subdesbordamiento;
  no se interpreta como probabilidad exactamente cero.
- **Estado:** IMPLEMENTADO y VERIFICADO técnicamente; interpretación y relación
  con D2/D3 pendientes del estudiante.
