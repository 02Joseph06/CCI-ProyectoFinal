# D3: c?lculos y documentaci?n

Fuente de este registro: [../../docs/formulas_C_D.md](../../docs/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

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
