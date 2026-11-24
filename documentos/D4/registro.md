# D4: c?lculos y documentaci?n

Fuente de este registro: [../../docs/formulas_C_D.md](../../docs/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

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
