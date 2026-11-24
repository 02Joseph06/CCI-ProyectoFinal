# Borrador de informe — resultados y decisiones pendientes

**Estado: borrador de trabajo, no informe final.** Cada punto tiene su registro
de fórmulas y resultados en el [índice de cálculos](../calculos/README.md).
Las cifras contradictorias y decisiones sin resolver se mantienen en el
[registro de discrepancias](../calculos/discrepancias_pendientes.md). El
memorando ejecutivo generado se identifica como provisional.

## Nota F6 solicitada por el grupo

La siguiente lectura recoge la interpretación facilitada por el estudiante:

> El detector de cambio de r?gimen confirma que `solicitudes_validacion.csv` no presenta r?fagas abruptas internas ($1$ solo tramo continuo de $1{,}200\text{ s}$), pero **no equivale a estacionariedad estricta respecto al dataset original**, porque la tasa de fallos por intento subi? de $0.1533$ a $0.2047$ (fuera del IC $90\%$ original) y $\lambda$ subi? marginalmente de $24.229$ a $24.571\text{ req/s}$.

> **?Por qu? sigue siendo v?lida la recomendaci?n de $c^* = 4$ GPUs?** Porque el simulador de capacidad **G2** modela expl?citamente la tasa total de llegadas $\lambda$ que entra al balanceador (ya incluyendo los reintentos generados por el SDK del cliente) y porque los tiempos de servicio en GPU ($G_+$), red ($R$) y tasa de cach? ($p_c$) s? resultaron invariantes entre ambos conjuntos de datos. Con $c = 4$ GPUs, la utilizaci?n sigue siendo baja ($\rho \approx 0.288$), dejando holgura suficiente incluso bajo la tasa elevada de reintentos observada en validaci?n.

**Revisión necesaria:** el detector se ejecutó con ventanas de 10 y 30 s; un
único tramo bajo esos criterios no prueba estacionariedad estricta. La segunda
afirmación no está validada: el enunciado no confirma que cada reintento se
cuente como otra llegada, la ausencia de diferencias detectadas no demuestra
invariancia y una utilización baja no demuestra cumplimiento del SLO. La
simulación G1 muestra una discrepancia de cola y G3 sigue pendiente de definir
su método de incertidumbre.

Los cálculos reproducibles de F6 están en [su registro](../F6/registro.md) y
en `outputs/F6/`. La conclusión final debe resolverse con el grupo antes de
emitir el informe.
