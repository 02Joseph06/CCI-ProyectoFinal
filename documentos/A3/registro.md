# A3: c?lculos y documentaci?n

Fuente de este registro: [../calculso/actualizacion_A_B.md](../calculso/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

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
