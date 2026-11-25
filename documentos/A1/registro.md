# Actualización vigente — S = 2279892322

34.072 filas originales, 101 duplicados tras conversión y 33.737 filas válidas; tolerancia física 0,015001 ms.

Fuente: ../../outputs/A1/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# A1: c?lculos y documentaci?n

Fuente de este registro: [../calculos/actualizacion_A_B.md](../calculos/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

## A1. Conversión, limpieza y conteos

1. Se leen 34.072 filas. Los 50 tamaños superiores a 5.000 se dividen entre
   1024, siguiendo la indicación del estudiante, antes de deduplicar. Este
   criterio de unidades es una decisión de tratamiento del grupo.
2. Tras convertir, hay 101 duplicados exactos. Se conserva la primera copia:
   quedan 33.971 identificadores distintos.
3. Entre estos identificadores hay 34 ausencias de red, 33 de GPU y 101
   latencias negativas. Una fila tiene tanto ausencia como latencia negativa.
4. Además hay 67 latencias inferiores a la suma de red y GPU fuera de la
   tolerancia. Se excluyen 234 solicitudes distintas en total; quedan 33.737.
   Los criterios se solapan y no se deben sumar ciegamente.

El control físico usa `L + 0,015001 ≥ red + GPU` en ms. Cada una de las tres
mediciones está expresada a centésimas de milisegundo: la suma de sus tres
semierrores de redondeo es `3 × 0,005 = 0,015 ms`. El margen adicional
`0,000001 ms` evita clasificar residuos binarios de punto flotante como
violaciones. La desigualdad estricta sin tolerancia excluiría observaciones
adicionales. Las filas excluidas y sus motivos están en
`outputs/A1/solicitudes_excluidas.csv`; la base retenida está en
`outputs/A1/solicitudes_auditadas.csv`.
