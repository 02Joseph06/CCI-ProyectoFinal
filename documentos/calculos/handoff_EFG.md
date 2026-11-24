# Handoff de E, F y G — avance provisional

Los cálculos se ejecutan desde las celdas 31, 33, 35, 37 y 39 del notebook. Se
verificó Run All con los 200 escenarios G3 en una copia temporal; se guardaron
las salidas ejecutadas en el notebook del proyecto y se comprobó que las tablas
seleccionadas coinciden con las salidas previas. Los CSV originales no se
sobrescribieron. Las fórmulas y las cifras
de cada punto están en su carpeta `documentos/<punto>/`; las tablas y figuras,
en `outputs/<punto>/`.

| Punto | Estado | Evidencia y alcance | Pendiente para informe |
|---|---|---|---|
| E1 | Ejecutado | Sensibilidad, FPR y Wilson en `outputs/E1/`. | Revisar supuestos de independencia temporal. |
| E2 | Ejecutado | Bayes y prevalencia observada 0,1105 en `outputs/E2/`. | Conservar discrepancia histórica con 0,25 y revisar transportabilidad. |
| E3 | Provisional | χ² y comparación de probabilidades en `outputs/E3/`. | Frecuencia esperada mínima 0,56; decidir si añadir Fisher y conciliar valores p. |
| E4 | Ejecutado | Binomial y extremos Wilson: puntual 0,999121, extremo conservador 0,974309. | Revisar dependencia temporal; se usa binomial/Wilson según decisión del grupo. |
| F1 | Ejecutado | Distribuciones y dos convenciones de cobertura en `outputs/F1/`. | El grupo eligió s muestral por réplica; n=200 es el menor de la rejilla con cobertura estimada ≥0,89. |
| F2 | Ejecutado | Intervalo clásico y bootstrap de bloques de longitud 20 en `outputs/F2/`. | La cifra reproducida prevalece; documentar su diferencia con la facilitada. |
| F3 | Ejecutado | Diferencias, intervalos individuales y conjuntos y pruebas de balance en `outputs/F3/`. | La decisión de versión y sus riesgos corresponden al grupo; no rechazar no prueba equivalencia. |
| F4 | Ejecutado | Coberturas simuladas y exactas en `outputs/F4/`. | Documentar que Wilson para n=20, p=0,01 tiene cobertura exacta 0,81790694. |
| F5 | Ejecutado | Cálculo y simulación en `outputs/F5/`. | Se reportan 7392/12372 según datos; completar la deducción manuscrita. |
| F6 | Provisional | Auditoría de validación, comparaciones y diagnósticos en `outputs/F6/`. | La ausencia de cambios detectados no prueba invariancia ni valida G; revisar hipótesis pendientes. |
| G1 | Provisional | Simulador FIFO y comparación histórica en `outputs/G1/`. | Revisar discrepancia de cola observada 0,011380 frente a simulada 0,013588. |
| G2 | Provisional | Proyección, intervalos de simulación y Figura 9 en `outputs/G2/`. | La selección de capacidad está condicionada al modelo y no incluye incertidumbre de parámetros. |
| G3 | Ejecutado | 200 escenarios y contraste M/M/c con red/caché en `outputs/G3/`, celda 37. | Cinco réplicas por capacidad añaden ruido; G3 usa criterio puntual y G2 el límite superior del IC. Revisar sensibilidad al modelo. |
| G4 | Borrador | Memorando Markdown y PDF de una página en `outputs/G4/`; texto original en `documentos/G4/`. | Resolver contradicciones y validar G antes de emitir recomendaciones definitivas. |

La nota F6 facilitada por el grupo se conserva textualmente en la bitácora y en
`documentos/informe/borrador_informe.md`, seguida de las reservas necesarias.
La deducción manuscrita F5 y las decisiones e interpretaciones que el grupo deba
defender siguen pendientes. La documentación bajo `documentos/` y `docs/` es
local e ignorada por Git.

La [guía digital B3/C1/D3/F5](../manuscrito/deducciones_B3_C1_D3_F5.md)
reúne el material disponible y distingue los pasos reconstruidos; no sustituye
las deducciones manuscritas que exige el enunciado.
