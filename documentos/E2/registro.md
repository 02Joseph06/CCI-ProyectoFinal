# Actualización vigente — S = 2279892322

π=0,008; VPP de D1 y D2=0.75619; supuesto de independencia daría 0.98023.

Fuente: ../../outputs/E2/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# E2 — Bayes y prevalencia

Con sensibilidad $s=P(A\mid I)$, tasa falsa $f=P(A\mid I^c)$ y prevalencia $\pi$, $P(I\mid A)=\pi s/[\pi s+(1-\pi)f]$. Se usa $\pi=0,007$ para producción y $663/6000=0,1105$ para los datos de prueba, calculando además directamente incidentes entre alertas para verificación. Las estimaciones suponen que las tasas condicionales del experimento son transportables a producción.

| Regla | VPP producción | VPP archivo de pruebas |
|---|---:|---:|
| D1 | 0,322338 | 0,893417 |
| D2 | 0,391082 | 0,918819 |
| D1 y D2 | 0,730544 | 0,979499 |
| D1 o D2 | 0,260077 | 0,860999 |

**Conciliación:** el grupo confirmó que prevalecen los cálculos hechos con el CSV. La cifra anterior 0,25 no corresponde a la prevalencia observada y no se usa. Datos y método: `outputs/E2/bayes_E2.csv` y `src/parte_e.py`. El cálculo directo y Bayes usando la prevalencia observada coinciden.
