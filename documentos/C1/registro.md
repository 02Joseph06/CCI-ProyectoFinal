# C1: c?lculos y documentaci?n

Fuente de este registro: [../../docs/formulas_C_D.md](../../docs/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

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
