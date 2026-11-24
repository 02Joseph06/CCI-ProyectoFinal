# A2: c?lculos y documentaci?n

Fuente de este registro: [../calculso/actualizacion_A_B.md](../calculso/actualizacion_A_B.md). El c?lculo reproducible y las salidas se identifican en la fuente.

## A2. Régimen y sensibilidad

Se usa el detector existente con log-verosimilitud de Poisson perfilada y BIC,
sin limitarlo artificialmente a tres segmentos. Para una ventana con `m`
intervalos, `Y` llegadas y `k` segmentos, la contribución perfilada de cada
segmento es `Y log(Y/m) − Y`, omitiendo constantes comunes; el criterio es
`−2 log L + (2k−1) log(m_total)`. Se comparan de uno a cinco segmentos con
duración mínima de 60 s.

Con agregación de 1 s, los tramos estimados son [0,668), [668,838) y
[838,1200] s, con 16.353, 8.781 y 8.603 solicitudes válidas. El grupo eligió
como régimen estable la unión de los dos tramos exteriores: 24.956 solicitudes
en una exposición de `668 + (1200−838) = 1030 s`. Los tiempos entre llegadas
deben calcularse dentro de cada tramo antes de concatenarlos; no se debe
introducir el salto de 170 s como una observación.

La sensibilidad con intervalos de 5 y 10 s selecciona límites (665,840) y
(670,840); con 15 y 30 s, BIC selecciona cuatro segmentos con cortes
660, 720 y 840. Los límites detectados **varían con la granularidad** y el
subcorte de 720 s también debe reportarse. La mezcla de tráfico alrededor del
inicio es una explicación posible, no una causa única demostrada. Los BIC
recalculados sobre la base depurada figuran en la salida y difieren de los de
la ejecución anterior sobre 33.971 registros.

La comparación de los tramos exteriores produce KS para tiempos entre llegadas
`D = 0,0142077`, `p ≈ 0,20328`; KS para latencia `D ≈ 0,007468`,
`p ≈ 0,90929`; y Mann–Whitney para latencia `p ≈ 0,54023`. El resultado de
tiempos usa diferencias calculadas dentro de cada tramo. La ausencia de rechazo
indica compatibilidad con las hipótesis de esas pruebas, no demuestra igualdad,
estacionariedad ni ausencia de sesgo. No se conoce el procedimiento anterior
que produjo `p = 0,2007`, por lo que no se puede atribuir con certeza la
diferencia numérica a una causa específica.

Exclusión de filas completas: como algunas observaciones con tiempos de llegada
válidos se excluyen por red/GPU/latencia, las tasas e intervalos entre llegadas
calculados con la base retenida describen las solicitudes retenidas y pueden
diferir de los del tráfico total. En los dos tramos elegidos se cuentan 25.132
identificadores antes de excluir por latencia y 24.956 después: 24,4 frente a
24,2291 solicitudes/s sobre 1030 s. Esta limitación afecta B1 y B4; no se ha
supuesto que las solicitudes eliminadas sean una muestra aleatoria.
