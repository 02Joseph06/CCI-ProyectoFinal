# Actualización vigente — S = 2279892322

N=14; umbral=956.0324 ms; normal=0.06443, Gamma=0.05555, remuestreo=0.07537, IC 95 % [0.07422; 0.07654].

Fuente: ../../outputs/C4/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# C4: c?lculos y documentaci?n

Fuente de este registro: [../calculos/formulas_C_D.md](../calculos/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

## C4 — Tiempo total en N solicitudes sin caché

- **Objetivo:** implementar dos aproximaciones y una comparación Monte Carlo.
- **Fórmulas dadas:** u = N(μ̂₊ + 15 ms); aproximación normal con media
  Nμ̂₊ y varianza Nσ̂₊²; aproximación Gamma con forma Nk̂ y escala θ̂.
- **Variables:** N = 16; μ̂₊ y θ̂, ms; σ̂₊², ms²; T_N y u, ms.
- **Referencia:** apuntes suministrados, páginas 9–11, normal y estandarización.
- **Ubicación:** notebook, celda 20; implementación `src/tiempos_cd.py` y
  `outputs/C4/resultados.json`.
- **Método confirmado:** 200000 bloques i.i.d. de 16 extracciones con reemplazo
  desde la distribución empírica de solicitudes sin caché. Umbral 1092,6084 ms;
  aproximación normal 0,052247; Gamma 0,044947; remuestreo 0,063425 con IC del
  90 % por error de simulación [0,062531; 0,064329].
- **Limitación:** el remuestreo no conserva dependencia temporal ni convierte
  la distribución empírica en la verdadera distribución de la población.
- **Estado:** IMPLEMENTADO y VERIFICADO técnicamente; la elección e
  interpretación para el informe corresponde al estudiante.
