# Actualización vigente — S = 2279892322

r=4; μ=37.06796; k=42; cola Poisson=0.22933; Monte Carlo=0.22852, IC 95 % [0.22668; 0.23037].

Fuente: ../../outputs/B/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# B4: c?lculos y documentaci?n

Fuente de este registro: [../calculos/actualizacion_A_B.md](../calculos/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

### B4. Reintentos en diez segundos

Con `p̂_reintento = 0,152989`, la media bajo adelgazamiento Poisson es
`μ̂ = 10 λ̂ p̂_reintento = 37,067961` solicitudes. Como `r = 3`,
`k = ⌈37,067961⌉ + 3 = 41`. La cola analítica del modelo es
`P(X≥41) = 0,280158`. En 200.000 réplicas Poisson la proporción fue 0,278570,
con intervalo Monte Carlo del 90 % `[0,276921; 0,280224]`, que contiene la
cifra analítica. Este intervalo cuantifica el error de simulación, no la
incertidumbre de estimación de `λ` y `p`. La cifra depende de Poisson,
adelgazamiento independiente y del filtro de A1.
