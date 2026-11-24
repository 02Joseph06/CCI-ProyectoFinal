# C3: c?lculos y documentaci?n

Fuente de este registro: [../../docs/formulas_C_D.md](../../docs/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

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
