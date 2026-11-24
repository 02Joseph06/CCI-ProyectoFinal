# C2: c?lculos y documentaci?n

Fuente de este registro: [../../docs/formulas_C_D.md](../../docs/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

## C2 — Ajuste de la parte positiva

- **Objetivo:** ajustar Gamma y lognormal a G dado no caché, y comparar Gamma
  por momentos y por máxima verosimilitud.
- **Fórmulas dadas por el estudiante:**
  ℓ_Γ(k,θ) = (k−1)Σln(gᵢ) − Σgᵢ/θ − n[lnΓ(k)+k ln θ];
  ℓ_LN(μ,σ) = −Σln(gᵢ) − n ln(σ√(2π)) − Σ(ln(gᵢ)−μ)²/(2σ²).
  Momentos Gamma: k̃ = x̄²/s² y θ̃ = s²/x̄, con s² de divisor n−1.
- **Variables y unidades:** gᵢ y θ, ms; k y σ, adimensionales; μ corresponde al
  logaritmo de los valores de G expresados en ms; n = 14696.
- **Método indicado:** minimizar la log-verosimilitud negativa con BFGS y sin
  `.fit()`. Se optimizan parámetros positivos en escala logarítmica y se
  proporciona el gradiente analítico; la tolerancia sobre el gradiente medio es
  10⁻⁸. Los dos optimizadores reportaron convergencia.
- **Referencia:** apuntes suministrados, páginas 4–5 y 7–8, variables continuas,
  media y varianza; la verosimilitud es la fórmula facilitada por el estudiante.
- **Ubicación:** notebook, celda de código 16; implementación
  `src/tiempos_c2.py`. Salidas: `outputs/C2/ajustes.json` y `ajustes_gpu.png`.
- **Verificaciones:** k = 2,52565986 y θ = 21,09865503 ms, ℓ = −70333,5700;
  momentos k̃ = 2,07890612 y θ̃ = 25,63272364 ms. Lognormal μ = 3,76487131,
  σ = 0,65929251, ℓ = −70059,0926. Distancias KS descriptivas 0,0397561 y
  0,0107189. Las pruebas automáticas comprueban las ecuaciones de máximo y
  rechazan observaciones no positivas.
- **Limitación:** las distancias KS usan datos con los mismos parámetros
  ajustados; no se presenta un valor p calibrado ni se concluye adecuación a
  partir de esas distancias. La discusión estructural queda para el estudiante.
- **Estado:** IMPLEMENTADO y VERIFICADO técnicamente. El grupo confirmó una
  formulación cautelosa: un ajuste marginal por sí solo no implica
  independencia. Un cambio de mezcla de tamaños puede modificar la cola, pero
  su dirección y efecto requieren evidencia adicional. El R² lineal observado
  no demuestra causalidad ni cuantifica por sí solo los cambios futuros.
