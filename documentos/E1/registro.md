# E1 — Sensibilidad y falsos positivos

Fuente: `data/raw/monitoreo.csv`, 6.000 minutos: 663 con incidente, 5.337 sin incidente; sin nulos en las columnas necesarias. Cada regla se evalúa directamente con sus alertas observadas.

Para cada regla, sensibilidad = TP/(TP+FN), FPR = FP/(FP+TN). Los intervalos al 90 % son Wilson: con $\hat p=x/n$, $z=\Phi^{-1}(0.95)$, centro $(\hat p+z^2/(2n))/(1+z^2/n)$ y semiancho $z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}/(1+z^2/n)$.

| Regla | TP | FP | Sensibilidad | FPR |
|---|---:|---:|---:|---:|
| D1 | 570 | 68 | 0,859729 | 0,012741 |
| D2 | 498 | 44 | 0,751131 | 0,008244 |
| D1 y D2 | 430 | 9 | 0,648567 | 0,001686 |
| D1 o D2 | 638 | 103 | 0,962293 | 0,019299 |

Los límites están en `outputs/E1/metricas_E1.csv`. Implementación: `src/parte_e.py`, función `analyze`; las pruebas verifican conteos y límites. La cobertura Wilson presupone observaciones Bernoulli independientes y probabilidad constante dentro de cada estado; la dependencia temporal no se ha validado.
