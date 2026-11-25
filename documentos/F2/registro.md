# Actualización vigente — S = 2279892322

Media=65.16652 ms; t 95 % [64.61621; 65.71683]; bootstrap de bloques 95 % [64.42717; 65.93976] ms.

Fuente: ../../outputs/F2/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# F2 - Intervalo de la latencia media

IC clásico $\bar L\pm t_{.95,n-1}s/\sqrt n$. Bootstrap de bloques móviles por tramo, longitud 20 solicitudes, 20.000 réplicas, percentiles 5 y 95: se conservan los tamaños de cada tramo y no se cruzan bloques por el incidente. Se usa la población de latencias auditadas y la semilla del grupo. La independencia de bloques remuestreados, el ancho de bloque escogido y la representatividad de la ventana son supuestos; el método no equivale a bootstrap i.i.d.

Evidencia: `outputs/F2/ic_latencia_F2.csv`. El IC clásico es aproximadamente [64,705; 65,628] ms y el de bloques calculado [64,525; 65,810] ms. Este último difiere del intervalo de referencia del usuario [64,68; 65,64]; puede depender de implementación y dependencia y no se selecciona silenciosamente. Estado: implementado y ejecutado; pendiente explicar y resolver la discrepancia antes de fijar el intervalo para informe.
