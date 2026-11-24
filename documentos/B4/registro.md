# B4: c?lculos y documentaci?n

Fuente de este registro: [../calculso/actualizacion_A_B.md](../calculso/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

### B4. Reintentos en diez segundos

Con `p̂_reintento = 0,152989`, la media bajo adelgazamiento Poisson es
`μ̂ = 10 λ̂ p̂_reintento = 37,067961` solicitudes. Como `r = 3`,
`k = ⌈37,067961⌉ + 3 = 41`. La cola analítica del modelo es
`P(X≥41) = 0,280158`. En 200.000 réplicas Poisson la proporción fue 0,278570,
con intervalo Monte Carlo del 90 % `[0,276921; 0,280224]`, que contiene la
cifra analítica. Este intervalo cuantifica el error de simulación, no la
incertidumbre de estimación de `λ` y `p`. La cifra depende de Poisson,
adelgazamiento independiente y del filtro de A1.
