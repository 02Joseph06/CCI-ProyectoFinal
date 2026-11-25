# Actualización vigente — S = 2279892322

Auditoría y comparación temporal con solicitudes_validacion.csv: ../../outputs/F6/comparacion_validacion_F6.csv. Cambios en fallos no identifican por sí solos su causa.

Fuente: ../../outputs/F6/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# F6 - Validación temporal independiente

Se reutiliza la auditoría A1 en una carpeta temporal sin modificar los archivos originales ni sus salidas: corrección de tamaños, deduplicación y tolerancia física de 0,015001 ms. Se conservan 29.485 de 29.781 registros; 88 duplicados exactos eliminados, un identificador contradictorio y 207 exclusiones por latencia no verificable. Se usa la ventana completa de 1.200 s solo para F6.

Se comparan estimaciones de B, C y F, intervalos de referencia y pruebas KS de dos muestras: `outputs/F6/comparacion_validacion_F6.csv`, `comparacion_intervalos_B_F6.csv`, `comparacion_intervalos_C_F_F6.csv`, `pruebas_distribucionales_F6.csv` y `segmentacion_validacion_F6.csv`. Los intervalos son individuales y las pruebas son nominales; se evalúan varias variables y la ausencia de rechazo no demuestra equivalencia. Los cálculos del proceso de llegadas solo describen las filas conservadas tras la auditoría y sus intervalos dependen del modelo.

La tasa pasa de 24,2291 a 24,5708 solicitudes/s y los fallos por intento de 0,15330 a 0,20469; ambas estimaciones caen fuera del IC original correspondiente. La similitud numérica de otras medias no demuestra invariancia. Un detector con un solo tramo no establece estacionariedad estricta ni valida el simulador de capacidad. La relación con G depende de la validación independiente de G; no se concluye que la recomendación de cuatro GPU sea sólida solamente a partir de F6.

Diagnósticos adicionales: `diagnosticos_B_F6.csv` y `metricas_version_F6.csv` comparan gaps, bloques de reintentos, probabilidad modelada B4 y métricas por versión; el p de KS exponencial es nominal con parámetro estimado. No constituyen validación integral de las hipótesis B1-B4, de intervalos conjuntos F3 ni del simulador G.
