# D2: c?lculos y documentaci?n

Fuente de este registro: [../../docs/formulas_C_D.md](../../docs/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

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
