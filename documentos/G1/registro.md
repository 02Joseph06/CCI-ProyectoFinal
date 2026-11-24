# G1. Validación de la simulación FIFO

**Estado:** implementado y ejecutado; la discrepancia de cola requiere revisión para utilizar la proyección como evidencia de capacidad. Fuentes: enunciado oficial, parte G1 (p. 6); decisiones del grupo sobre B, C y simulación G1/G2.

La tasa de entrada se estima con 24.956 solicitudes observadas en 1.030 s efectivos: $\widehat\lambda=24,229126\ \mathrm{s}^{-1}$. Los parámetros de caché y de los ajustes lognormal y normal se recalculan a partir de las salidas de A, C2 y C3. El modelo seleccionado usa llegadas Poisson, caché Bernoulli, red normal y GPU sin caché lognormal independientes. Una solicitud cacheada consume solo red; una no cacheada se atiende por la primera GPU disponible, con cola FIFO y sin interrupción:

$$s_i=\max(a_i,f_{\min}),\qquad W_i=1000(s_i-a_i),\qquad f_i=s_i+G_i/1000,\qquad L_i=R_i+W_i+G_i.$$

Aquí $a_i,s_i,f_i$ están en segundos; $W_i,R_i,G_i,L_i$ en ms. Las 20 réplicas independientes duran 1.030 s y empiezan sin cola. Se usa un único generador `np.random.default_rng(S)` con $S=2046185499$; las réplicas utilizan draws sucesivos sin compartir observaciones. Para cada estadístico se muestra el promedio de réplicas y el intervalo de Student entre réplicas al 90 %, que cuantifica error de simulación, no de calibración.

| Indicador | Observado | Simulado (media) | IC 90 % de réplicas |
|---|---:|---:|---:|
| Mediana (ms) | 53,205 | 53,224 | [53,046; 53,401] |
| P95 (ms) | 152,203 | 152,578 | [152,084; 153,072] |
| $P(L>210\ \mathrm{ms})$ | 0,011380 | 0,013588 | [0,013331; 0,013844] |

La proporción observada queda fuera del intervalo que solo describe las réplicas simuladas; **esto no es por sí mismo un contraste formal** frente a una proporción observada incierta. La diferencia de 0,002208 en la cola es relevante frente al límite SLO de 0,01; no debe ocultarse al comunicar G2. El código de simulación está en `src/parte_g.py`, la tabla en `outputs/G1/validacion_simulador_G1.csv`; las pruebas unitarias comprueban orden FIFO, unidades, bypass de caché y reproducibilidad. La interpretación final corresponde al grupo.

**Ambigüedad pendiente:** el PDF p. 3 define una fila por solicitud y `intentos` por solicitud; no queda demostrado que la tasa de filas incluya cada reintento del SDK como nueva llegada a GPU. No se añaden reintentos sintéticos para evitar doble contabilización sin evidencia.
