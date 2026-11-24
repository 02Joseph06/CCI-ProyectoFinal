# B3: c?lculos y documentaci?n

Fuente de este registro: [../calculso/actualizacion_A_B.md](../calculso/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

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
