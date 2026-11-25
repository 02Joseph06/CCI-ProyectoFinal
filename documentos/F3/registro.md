# Actualización vigente — S = 2279892322

GPU sin caché (ms): B−A=0.53024, IC Bonferroni 95 % [-0.92951; 1.99000]; reintento (>1): B−A=0.00637, IC Bonferroni 95 % [-0.00454; 0.01728]; violación SLO >190 ms: B−A=0.00108, IC Bonferroni 95 % [-0.00306; 0.00522]. Los intervalos incluyen cero; no rechazar diferencias no demuestra equivalencia.

Fuente: ../../outputs/F3/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# F3 - Comparación de versiones

Diferencias B−A: GPU sin caché, indicador de reintento y violación SLO >210 ms. Los intervalos simultáneos usan el crítico normal elegido por el grupo: $\hat\Delta\pm z_{1-\alpha/6}\sqrt{s_A^2/n_A+s_B^2/n_B}$, con $z_{1-0,10/6}\approx2,128$. Los intervalos individuales usan $z_{0,95}$. La corrección Bonferroni proporciona cobertura conjunta de al menos 90 % en la medida en que los intervalos individuales alcancen sus coberturas nominales. Se mantienen por separado valores p nominales del contraste t de Welch; no son el contraste dual exacto de los IC normales. Se comparan tamaños y caché entre grupos para diagnosticar balance, sin confundir no rechazo con equivalencia o causalidad.

Evidencia: `outputs/F3/comparacion_AB_F3.csv` y `balance_grupos_F3.csv`. La comparación GPU usa solo no cacheadas; las otras usan todas las solicitudes. Implementado y ejecutado. Pendientes: decisión del grupo e interpretación, además de la salvedad de selección por caché y dependencia temporal.

El balance se examina también mediante KS para tamaño y chi-cuadrado para caché; son diagnósticos, no una prueba de equivalencia. Se exportan IC individuales y conjuntos.

Para la tabla de caché se incluyen chi-cuadrado sin corrección (p=0,6720) y con Yates (p=0,6814), con su identificación explícita. El no rechazo no demuestra equivalencia.
