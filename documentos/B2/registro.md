# Actualización vigente — S = 2279892322

Bloques de 100: media estable 15.3012; media en sobrecarga 31.2759.

Fuente: ../../outputs/B/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# B2: c?lculos y documentaci?n

Fuente de este registro: [../calculos/actualizacion_A_B.md](../calculos/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

### B2. Reintentos por bloques

En 24.956 solicitudes estables, `p̂ = 0,152989` y, bajo la binomial de 100,
`E[X] = 100p̂ = 15,2989` y `Var(X) = 100p̂(1−p̂) = 12,9584`. Para los
249 bloques completos estables se observan media 15,3012 y varianza muestral
12,1226; quedan 56 solicitudes fuera de bloques completos.

En el tramo de carga alta hay 87 bloques completos, con media observada
31,2759 y varianza 18,3184, y 81 solicitudes fuera de los bloques. La media
de esos bloques supera en 15,9769 la media 15,2989 calculada con el parámetro
estable. Si se estima la proporción por separado en carga alta se obtiene
`p̂ = 0,313404`, con media binomial 31,3404 y varianza 21,5182. La tabla da
ambos puntos de referencia; estas cifras descriptivas no establecen una causa
ni un contraste formal de equivalencia.
