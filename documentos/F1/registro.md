# Actualización vigente — S = 2279892322

Coberturas simuladas con s muestral: n=30 0.92550, n=200 0.94740; primer tamaño de la rejilla que supera 0,94: 200.

Fuente: ../../outputs/F1/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# F1 - Distribución muestral de la media

Población utilizada: las 24.956 latencias de los dos tramos estables auditados. Cada réplica extrae con reemplazo de esa población empírica; hay 20.000 réplicas por tamaño, semilla 2046185499. La media de referencia es la media empírica de la población, no un valor conocido de producción.

Para cada muestra se calcula $\bar L=\sum_i L_i/n$ y sus momentos. La cobertura se mide por la frecuencia de inclusión de la media poblacional empírica en $\bar L\pm z_{.95}s/\sqrt n$; también se muestra $\bar L\pm z_{.95}\sigma_{emp}/\sqrt n$, que usa una desviación fija empírica y responde otra pregunta. Umbral requerido: 0,89. La desviación de Monte Carlo de cobertura es $\sqrt{\hat c(1-\hat c)/R}$, aproximadamente 0,0022 cerca de 0,90. Por ello los valores cercanos a 0,89 no justifican por sí solos una clasificación definitiva.

El CSV registra ahora el error estándar Monte Carlo de cada una de las dos coberturas. Este error cuantifica la variabilidad debida a las réplicas simuladas y no incluye incertidumbre sobre la población empírica ni decide cuál convención usar.

El grupo confirmó la convención con $s$ de cada réplica. En la ejecución guardada las coberturas para $n=30$ y $n=200$ son 0,87360 y 0,89495 respectivamente; entre los tamaños evaluados, el menor que supera 0,89 es 200. Esto es una estimación Monte Carlo, cuyo error estándar para 200 es aproximadamente 0,00217; no asegura que la cobertura exacta de la población empírica supere el umbral. Las cifras 0,8733 y 0,8935 aportadas no coinciden exactamente y se reportan los resultados reproducidos.

Para medir la precisión numérica se añade el intervalo Wilson del 90 % de la frecuencia de cobertura Monte Carlo: [0,86968; 0,87741] para $n=30$ y [0,89133; 0,89846] para $n=200$. La selección corresponde únicamente a la rejilla probada, y la cobertura se define respecto a la población empírica. El resumen reproducible está en `outputs/F1/resumen_cobertura_F1.csv`.

Evidencia: `outputs/F1/distribucion_muestral_F1.csv` y `figura_7_tcl_latencia.png`. Estado: implementado y ejecutado bajo los supuestos indicados.
