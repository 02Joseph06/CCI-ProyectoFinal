# Bitácora de decisiones vigente

| Fecha | Punto | Decisión | Alternativa o limitación |
|---|---|---|---|
| 2026-11-25 | Parámetros | C1=1137978133, C2=1141914189; S=2279892322, confianza 95 %. El grupo confirmó que los CSV corresponden. | Las salidas con la semilla anterior son históricas. |
| 2026-11-25 | A1 | Convertir tamaños >5000 de bytes a KB antes de deduplicar; tolerancia física 0,015001 ms. | La comparación estricta descartaría diferencias compatibles con redondeo. |
| 2026-11-25 | A2 y B | Mantener los tramos [0,668) y [838,1200] s y calcular intervalos por tramo. | La ausencia de rechazo no demuestra estacionariedad. |
| 2026-11-25 | C | FDA mixta; ajuste Gamma y lognormal por BFGS; C4 con N=14 y remuestreo i.i.d. | El ajuste marginal no incorpora explícitamente tamaño ni dependencia temporal. |
| 2026-11-25 | D | Clases con límites 100 y 450 KB; varianza empírica con divisor n; WLS con pesos 1/tamaño² y HC3. | Los pesos son un supuesto y no eliminan todas las fuentes de sesgo o dependencia. |
| 2026-11-25 | E | Wilson 95 %, prevalencia 0,008 y kₘáx=6; propagar extremo superior de FPR. | D1 y D2 cumple puntualmente, pero no con el extremo conservador; decidir con el responsable de guardia. |
| 2026-11-25 | F | IC al 95 %, Bonferroni para tres métricas y bootstrap por bloques de 20 por tramo. | La falta de diferencia significativa no demuestra equivalencia. |
| 2026-11-25 | G | Simulación FIFO y 200 escenarios; τ=190 ms y ε=0,02; contrastar con M/M/c. | Tres GPU cumplen en el modelo principal, pero M/M/c y la discrepancia G1 limitan la recomendación. |

Las fórmulas, cálculos y referencias se encuentran en [los registros vigentes](formulas_C_D.md) y en las tablas de `outputs/`. Las deducciones manuscritas y la declaración de IA requieren revisión y firma del grupo.

## Registro histórico — semilla anterior

# Bitácora de decisiones

Decisiones comunicadas por el estudiante y aplicadas al proyecto. Las fechas
indican cuándo se registraron en esta bitácora; las referencias matemáticas y
verificaciones detalladas están en `formulas_C_D.md` y en
`actualizacion_A_B.md`.

| Fecha | Punto | Decisión del grupo | Alternativa o limitación registrada |
|---|---|---|---|
| 2026-11-22 | A1 | Convertir tamaños superiores a 5000 dividiendo entre 1024 antes de deduplicar; usar tolerancia de 0,015001 ms y excluir las filas indicadas. | La desigualdad estricta produciría una exclusión mucho mayor. Las tasas posteriores describen las filas conservadas. |
| 2026-11-22 | A2/B | Usar como régimen estable [0,668) ∪ [838,1200] s y calcular diferencias de tiempo por tramo. | La selección del régimen se basa en los datos observados; no introducir el salto entre tramos. |
| 2026-11-22 | A3 | Varianza muestral con n−1; asimetría y exceso de curtosis corregidos. | Se registra separadamente de la varianza empírica con n usada para identidades. |
| 2026-11-22 | C1/D2 | Verificar las leyes de varianza con divisor n y mostrar también n−1 como referencia. | La identidad empírica no debe mezclar denominadores sin corrección. |
| 2026-11-22 | C1/C2 | Representar la FDA mixta empírica y lognormal; ajustar Gamma y lognormal por verosimilitud BFGS y Gamma por momentos. | La dirección del efecto de cambios en la mezcla y la interpretación estructural requieren cautela y confirmación. |
| 2026-11-22 | C3 | Usar momentos recalculados, p nominal de KS, bootstrap del percentil y referencia AD 0,656 elegida por el estudiante. | SciPy 1.18.1 calcula 0,631; se reportan ambos y no se atribuye 0,656 a la versión instalada. |
| 2026-11-22 | C4 | Comparar las aproximaciones normal y Gamma con 200000 bloques i.i.d. remuestreados con reemplazo. | El remuestreo empírico no conserva dependencia temporal ni demuestra independencia real. |
| 2026-11-22 | D1 | Utilizar proporciones, contraste χ² e intervalos Wald al 90 %. | Los intervalos Wald y el contraste dependen de sus supuestos. |
| 2026-11-22 | D2 | Usar 25 grupos de cuantiles y una curva LOWESS con fracción 0,15. | El cálculo usa ajuste local lineal tricúbico sin iteraciones robustas; ambas elecciones son parámetros del método. |
| 2026-11-22 | D3 | Reportar OLS y WLS con pesos 1/tamaño², errores clásicos y HC3 e intervalos t con n−2 grados de libertad. | HC3 no corrige cualquier dependencia ni sesgo; sus intervalos son aproximados. |

## Lectura de F6 facilitada por el grupo

> El detector de cambio de r?gimen confirma que `solicitudes_validacion.csv` no presenta r?fagas abruptas internas ($1$ solo tramo continuo de $1{,}200\text{ s}$), pero **no equivale a estacionariedad estricta respecto al dataset original**, porque la tasa de fallos por intento subi? de $0.1533$ a $0.2047$ (fuera del IC $90\%$ original) y $\lambda$ subi? marginalmente de $24.229$ a $24.571\text{ req/s}$.

> **?Por qu? sigue siendo v?lida la recomendaci?n de $c^* = 4$ GPUs?** Porque el simulador de capacidad **G2** modela expl?citamente la tasa total de llegadas $\lambda$ que entra al balanceador (ya incluyendo los reintentos generados por el SDK del cliente) y porque los tiempos de servicio en GPU ($G_+$), red ($R$) y tasa de cach? ($p_c$) s? resultaron invariantes entre ambos conjuntos de datos. Con $c = 4$ GPUs, la utilizaci?n sigue siendo baja ($\rho \approx 0.288$), dejando holgura suficiente incluso bajo la tasa elevada de reintentos observada en validaci?n.

**Estado de la segunda afirmación:** es una interpretación aportada por el
grupo y permanece sin validar. El CSV no aclara si cada reintento está contado
como nueva llegada; que una diferencia no resulte significativa no demuestra
invariancia, y baja utilización no prueba el cumplimiento del SLO. G1 presenta
una discrepancia en la cola y falta propagar la incertidumbre en G3. La primera
lectura se comprobó con el detector para ventanas de 10 y 30 s, no con todas las
formas posibles de cambio temporal.
