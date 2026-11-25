# Actualización vigente — S = 2279892322

λ=24.22913 solicitudes/s; IC Poisson 95 % [23.92944; 24.53163].

Fuente: ../../outputs/B/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# B1: c?lculos y documentaci?n

Fuente de este registro: [../calculos/actualizacion_A_B.md](../calculos/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

### B1. Llegadas y conteos

Con `n = 24.956` y `T = 1030 s`, la estimación usada es
`λ̂ = n/T = 24,229126 solicitudes/s`. El intervalo del 90 % basado en Poisson
es `[23,977402; 24,482930] solicitudes/s`. Aplicando la transformación
decreciente `1/λ`, la media entre llegadas del modelo es `0,041273 s` y su
intervalo transformado es `[0,040845; 0,041706] s`.

Se calcularon 24.954 diferencias por separado en los dos tramos; la mayor es
0,4849 s y hay 42 empates por resolución de la marca temporal. La distancia
KS frente a una exponencial ajustada es 0,005052; el valor p mediante 400
réplicas que reajustan el parámetro es aproximadamente 0,35162. El índice
varianza/media de los conteos en 102 ventanas completas de 10 s es 0,81613;
el contraste aproximado de dispersión da p ≈ 0,17738. El bootstrap KS simula
datos continuos y no reproduce ni la cuantización ni el condicionamiento por
límites de observación; por ello su calibración es aproximada. El intervalo de
tasa depende del modelo Poisson y de haber fijado los tramos tras mirar datos.
