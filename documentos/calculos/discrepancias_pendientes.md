# Discrepancias pendientes de resolver

Este registro distingue cifras suministradas en la conversación de cálculos
reproducidos. Las conclusiones afectadas permanecen provisionales mientras el
estudiante decide; las salidas no deben copiarse al memorando como hechos
validados sin revisar la fuente, los métodos y sus límites.

| Punto | Fuente o afirmación | Evidencia contrastada | Decisión pendiente |
|---|---|---|---|
| E2 | La tabla reciente indica prevalencia de prueba 0,25; un aporte anterior indica 663/6000. | `data/raw/monitoreo.csv`: 663 de 6000, o 0,1105. | El grupo confirmó que prevalecen los resultados calculados desde los CSV. |
| E3 | La tabla reciente da p=0,032 con incidente y p=0,962 sin incidente; el aporte anterior proporciona otros p. | El χ² sin corrección sobre el CSV da p≈0,6313 y p≈4,64×10⁻³⁰, respectivamente; en el segundo estrato el mínimo esperado es 0,56. | Confirmar si complementar con Fisher y cómo reportar la diferencia. |
| F1 | Un aporte sitúa el menor n en 30 y otro en 200. | Con 20.000 réplicas, para n=30 la cobertura es 0,87360 usando s por réplica y 0,90225 usando σ empírica fija; para n=5 son 0,78565 y 0,91990. La cobertura tiene incertidumbre Monte Carlo. | El grupo eligió s por réplica y n=200 entre los valores evaluados. |
| F2 | Se facilitó [64,68; 65,64] ms para bloques móviles. | Bloques móviles de longitud 20, separados por tramo, y 20.000 réplicas producen [64,52476; 65,80996] ms. Este bootstrap no equivale al i.i.d. | El grupo indicó que prevalecen los cálculos reproducidos; documentar la diferencia. |
| F4 | Se afirmó que Wilson mantiene cobertura de al menos 89 % en todas las configuraciones. | La ejecución actual con n=20, p=0,01 y 10000 réplicas dio 82,27 %. La suma binomial exacta da 0,99²⁰ = 0,81790694: solo el conteo cero produce un intervalo Wilson del 90 % que contiene 0,01. | El grupo indicó que prevalecen los cálculos reproducidos; no afirmar cobertura uniforme ≥89 %. |
| F5 | Una referencia indica 7392/12372 observaciones; otra 7388/12325. | Las varianzas de los CSV y los cuantiles indicados dan 7392/12372 tras redondear hacia arriba. | Se reportan los cálculos reproducidos y la diferencia; falta verificar la deducción manuscrita. |
| G1/G2 | Se propone recomendar cuatro GPU con resultados simulados suministrados. | El simulador calculado da violación histórica 0,013588 frente a observada 0,011380; la diferencia afecta la validación. | Decidir cómo tratar la discrepancia y la proyección condicionada al modelo. |
| G3/F6 | Se afirmó que los reintentos ya se cuentan como llegadas separadas y que 4 GPU sigue garantizando el SLO. | El PDF, sección 4.2, define una fila por solicitud y una columna `intentos`; no aclara si cada reintento ya es otra llegada. La baja carga por sí sola no prueba el SLO. | G3 se ejecutó con los 200 escenarios y el contraste elegidos; el significado de λ y la robustez estructural siguen sin verificarse. |
| G3, contraste M/M/c | Se anticipó que el contraste podría dar una capacidad menor. | Con caché y red incluidos, el contraste calcula una violación aproximada del 2,08 % con cuatro GPU; ninguna capacidad de la cuadrícula 2–5 alcanza el 1 %. Tres escenarios de G3 presentan clasificaciones no monótonas por ruido de simulación. | Interpretar el contraste como dependiente de sus supuestos y decidir si se amplía la simulación; no presentar cuatro GPU como garantía. |
| E4 | Se afirmó que la probabilidad de cumplir supera 0,999 incluso al usar el extremo superior Wilson de FPR. | La binomial calculada da 0,999121 para la FPR puntual y 0,974309 con el extremo superior Wilson. | El grupo indicó binomial exacta y Wilson; se documentan ambas cifras y su diferencia. |

Las pruebas con p alto no demuestran por sí solas equivalencia, independencia
ni estacionariedad estricta. Los intervalos Monte Carlo no incluyen
automáticamente la incertidumbre de los parámetros calibrados.
