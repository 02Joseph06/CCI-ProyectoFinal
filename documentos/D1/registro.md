# Actualización vigente — S = 2279892322

Clases <100, [100,450), ≥450 KB; χ²=933.2784, p=2.194e-203; probabilidades e IC Wald 95 % en ../../outputs/D1/intervalos_cache_dada_clase.csv.

Fuente: ../../outputs/D1/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# D1: c?lculos y documentaci?n

Fuente de este registro: [../calculos/formulas_C_D.md](../calculos/formulas_C_D.md). El c?lculo reproducible y las salidas se identifican en la fuente.

## D1 — Distribución conjunta e independencia

- **Objetivo:** tabla conjunta de clase de tamaño y caché, marginales,
  condicionales, contraste y figura 4.
- **Fórmulas:** p̂ᵢⱼ = nᵢⱼ/n; p̂ᵢ· = Σⱼp̂ᵢⱼ; p̂·ⱼ = Σᵢp̂ᵢⱼ;
  P̂(cache=j | clase=i) = nᵢⱼ/nᵢ·;
  χ² = Σᵢⱼ(Oᵢⱼ−Eᵢⱼ)²/Eᵢⱼ, Eᵢⱼ = nᵢ·n·ⱼ/n.
- **Variables:** tamaño en KB, clases [0,120), [120,500), [500,∞);
  cache_hit ∈ {0,1}; n = 24956.
- **Método indicado:** frecuencias empíricas, χ² de Pearson e intervalos Wald
  al 90 %: p̂ ± z₀.₉₅ √[p̂(1−p̂)/nᵢ].
- **Referencia:** apuntes suministrados, páginas 1–3 y 6, probabilidad conjunta,
  condicional y variables discretas.
- **Ubicación:** notebook, celda de código 22; `src/dependencias_d1.py`.
  Tablas, `resumen.json` y `figura_4_conjunta.png` en `outputs/D1/`.
- **Verificaciones:** la conjunta suma 1, las condicionales suman 1 por grupo;
  χ² = 950,161634, gl = 2, p ≈ 4,73176×10⁻²⁰⁷. El mínimo esperado es 821,01.
  Una prueba automática verifica los límites 120 y 500 KB y las sumas.
- **Estado:** IMPLEMENTADO y VERIFICADO para tablas, contraste e intervalos.
  La interpretación del contraste corresponde al estudiante.
