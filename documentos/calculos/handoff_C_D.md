# Handoff para informe — partes C y D

Las celdas nuevas se ejecutaron de forma aislada con la base auditada, sin
reescribir las celdas ni las salidas aprobadas de A/B. Las cifras completas,
fórmulas, unidades, métodos y advertencias están en `formulas_C_D.md`.

| Punto | Celda | Evidencia | Estado y tarea del informe |
|---|---:|---|---|
| C1 | 14 | `outputs/C1/` | FDA empírica y lognormal; identidad de varianza verificada con divisor n. Falta deducción manuscrita. |
| C2 | 16 | `outputs/C2/` | Gamma y lognormal BFGS, comparación por momentos y distancias KS. Interpretación cautelosa confirmada; la dirección de una cola futura requiere evidencia. |
| C3 | 18 | `outputs/C3/` | Red, Figura 3, colas y percentil bootstrap. Referencia elegida: 0,656; SciPy 1.18.1 calcula 0,631. Ambos valores se conservan con su procedencia. KS tiene p nominal. |
| C4 | 20 | `outputs/C4/` | Normal, Gamma y 200000 réplicas i.i.d. empíricas. Explicar que el intervalo es de simulación y que no se preserva dependencia temporal. |
| D1 | 22 | `outputs/D1/` | Conjunta, condicionales, Wald y χ²; Figura 4. El estudiante interpreta el contraste. |
| D2 | 24 | `outputs/D2/` | Esperanza y varianza total; 25 grupos por cuantiles y LOWESS local con frac 0,15. El estudiante interpreta la curva. |
| D3 | 26 | `outputs/D3/` | OLS y WLS matriciales; errores clásicos y HC3; intervalos t al 90 %, Figura 5 y diagnóstico BP. Falta deducción manuscrita. |
| D4 | 28 | `outputs/D4/` | Covarianza y correlación. P numérico cero por subdesbordamiento; interpretar relación con D2/D3. |

No se ha afirmado que una distribución marginal implique independencia, que
WLS corrija necesariamente toda la heterocedasticidad, ni que el remuestreo
empírico i.i.d. represente la dependencia entre solicitudes consecutivas.
