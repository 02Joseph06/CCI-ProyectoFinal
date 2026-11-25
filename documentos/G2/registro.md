# Actualización vigente — S = 2279892322

g=1,5, τ=190 ms, ε=2 %: con 3 GPU violación=1.57760%, IC 95 % [1.5441 %; 1.6111 %]; primera capacidad que cumple por límite superior en la cuadrícula evaluada, bajo el modelo.

Fuente: ../../outputs/G2/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# G2. Proyección de capacidad

**Estado:** implementado y ejecutado con el modelo de G1; selección provisional, supeditada a la validación de cola y al significado de la tasa. Se aplica $g=1,5$, $\tau=210$ ms y $\epsilon=0,01$.

Para cada $c=1,\ldots,5$ se ejecutan 30 réplicas independientes de 600 s, luego de 30 s de calentamiento. El indicador por réplica es $\hat q_j=n_j^{-1}\sum_i \mathbf1(L_{ij}>210)$; se informa $\bar q\pm t_{0,95;29}\,s_q/\sqrt{30}$. El IC mide variación de simulación y presupone parámetros fijos. La carga por GPU usa la media del modelo lognormal elegido, no la media empírica:

$$\rho_c=\frac{g\widehat\lambda(1-\widehat p_c)\exp(\widehat\mu_{\log}+\widehat\sigma_{\log}^2/2)}{1000c}.$$

| GPU | $\rho$ | Proporción simulada | IC 90 % |
|---:|---:|---:|---:|
| 1 | 1,147896 | 0,588579 | [0,587568; 0,589591] |
| 2 | 0,573948 | 0,030694 | [0,029804; 0,031585] |
| 3 | 0,382632 | 0,010189 | [0,009943; 0,010435] |
| 4 | 0,286974 | 0,009057 | [0,008858; 0,009256] |
| 5 | 0,229579 | 0,008768 | [0,008555; 0,008981] |

Con el criterio solicitado de límite superior del IC menor o igual a 0,01, 4 es el primer valor probado que lo satisface **dentro del simulador calibrado**. No incorpora la incertidumbre de parámetros, y G1 registra discrepancia frente a la cola observada. Con $c=1$, $\rho>1$ y el resultado se refiere al horizonte finito, no a estado estacionario. Los parámetros se registran en `outputs/G2/parametros_y_limites.json`; tabla y Figura 9 en `outputs/G2/`. La probabilidad de red negativa bajo el modelo normal es no nula aunque muy pequeña; el modelo no la trunca.

El enunciado define filas como solicitudes y guarda el número de intentos por fila. La afirmación de que la tasa de filas ya cuenta cada reintento como llegada al balanceador no se ha corroborado; el simulador no añade reintentos por su cuenta. El resultado no demuestra que cuatro GPU cumplan en producción.
