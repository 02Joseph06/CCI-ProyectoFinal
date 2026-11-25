# Actualización vigente — S = 2279892322

La prueba χ² por estado y su frecuencia esperada mínima están en ../../outputs/E3/independencia_condicional_E3.csv; el estrato sin incidente tiene frecuencia esperada menor a 5.

Fuente: ../../outputs/E3/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# E3 — Dependencia condicional

Por cada valor de `incidente` se tabulan D1 y D2 y se calcula el estadístico $\chi^2=\sum_{i,j}(O_{ij}-E_{ij})^2/E_{ij}$, con $E_{ij}=O_{i+}O_{+j}/n$ y 1 grado de libertad. Se emplea `scipy.stats.chi2_contingency(..., correction=False)`. Las combinaciones conjuntas observadas se comparan con $P(D_1=1\mid I)P(D_2=1\mid I)$ y su complemento para la regla OR; esas tasas hipotéticas también se insertan en Bayes de E2.

Con incidente: $\chi^2=0,230278$, $p=0,631318$ y mínimo esperado 23,145. Sin incidente: $\chi^2=129,754243$, $p=4,64\times10^{-30}$ y mínimo esperado 0,5606; **la aproximación asintótica de este segundo contraste es poco fiable**. La falta de rechazo en cualquier estrato no demuestra independencia.

**Conciliación:** los valores suministrados fueron $p=0,032$ con incidente y $p=0,962$ sin incidente; no se reproducen con los datos ni con el método arriba descrito. El grupo confirmó la prioridad de los cálculos desde el CSV. No se ha elegido una prueba adicional para la tabla dispersa; el segundo valor p se conserva como diagnóstico limitado por la baja frecuencia esperada. Bajo independencia hipotética el VPP de la regla AND sería 0,977445 frente a 0,730544 al usar la frecuencia conjunta observada; esta comparación es aritmética, no una validación de independencia. Tablas: `outputs/E3/independencia_condicional_E3.csv` y `outputs/E2/bayes_E2.csv`.
