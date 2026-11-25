# Actualización vigente — S = 2279892322

kₘáx=6; D1 y D2 tiene 2.4089 falsas alarmas/día, P(FA≤6) puntual=0.98826 y con FPR en extremo superior Wilson 95 %=0.82174. El segundo valor no alcanza 0,90; no hay una regla robustamente aceptable bajo ese criterio conservador.

Fuente: ../../outputs/E4/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# E4 — Falsas alarmas por día

Con $\pi=0,007$, $q=(1-\pi)\widehat{\mathrm{FPR}}$, $X\sim\mathrm{Binomial}(1440,q)$ y $k_{\max}=8$, se calcula $P(X\le8)$ y $1440q$. El modelo supone minutos independientes, prevalencia y FPR constantes: estas hipótesis no quedan verificadas por las cuentas agregadas.

Como propagación provisional y conservadora sobre el intervalo Wilson de FPR al 90 %, se sustituyen ambos extremos de ese intervalo en la función monótona $P(X\le8)$. No es un intervalo predictivo bayesiano ni garantiza cobertura si falla el modelo binomial. Además, se verifican las probabilidades mediante 200.000 réplicas binomiales usando `np.random.default_rng(2046185499)` y se reporta intervalo Wilson del error Monte Carlo.

| Regla | Media falsas/día | Probabilidad puntual | Extremos propagados Wilson |
|---|---:|---:|---:|
| D1 | 18,218954 | 0,005962 | [0,000470; 0,037815] |
| D2 | 11,788735 | 0,168271 | [0,035278; 0,427459] |
| D1 y D2 | 2,411332 | 0,999121 | [0,974309; 0,999984] |
| D1 o D2 | 27,596358 | 0,000010 | [0,000000274; 0,000194] |

Con estos supuestos, AND supera el 0,90 incluso en el extremo conservador de Wilson; ello no demuestra la exigencia para una serie temporal dependiente. El grupo indicó que el extremo superior de FPR también produciría más de 0,999, pero el cálculo reproducido da **0,974309**, por lo que se conserva ese resultado y se deja señalada la discrepancia. La probabilidad puntual sí es 0,999121. No se presupone una distribución posterior de la FPR. Salidas: `outputs/E4/decision_guardia_E4.csv`, `outputs/E4/figura_6_alertas.png`. Código `src/parte_e.py`.
