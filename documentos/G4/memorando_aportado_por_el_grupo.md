# Memorando ejecutivo aportado por el grupo — pendiente de verificación

El texto que sigue reproduce las cifras y recomendaciones facilitadas por el
estudiante. **Es una fuente de trabajo, no el memorando validado:** existen
discrepancias entre cifras proporcionadas en distintos mensajes y resultados
que deben calcularse con los CSV y las simulaciones. No se ha comprobado la
recomendación de capacidad ni la de alertas en esta copia.

---

# Memorando Ejecutivo — Confiabilidad y Planeación de Capacidad de Inferencia de IA

**Para:** Dirección Técnica (CTO) — Andes Vision AI  
**De:** Equipo de Ingeniería SRE y Datos  
**Fecha:** 22 de noviembre de 2026  
**Asunto:** Diagnóstico de confiabilidad, evaluación de Modelo B y plan de capacidad GPU (+50 % tráfico)

## 1. Comportamiento real del servicio y confiabilidad de las métricas (P1)

Tras auditar la telemetría de producción (33.737 solicitudes válidas después
de depurar 335 registros corruptos o duplicados), identificamos que el sistema
operó en un **régimen estable** durante 1.030 s (24.956 solicitudes),
interrumpido por un incidente anómalo de 170 s donde el tráfico se duplicó y
los fallos crecieron casi siete veces. En operación normal con el pool actual
de dos GPU:

- **Tráfico y caché:** Llegan **24,23 solicitudes/s** (IC 90 %: [23,98;
  24,48]). El **41,1 %** de las peticiones se resuelve desde caché sin consumir
  GPU (55,8 % en imágenes pequeñas menores de 120 KB, bajando a 23,2 % en
  grandes de al menos 500 KB).
- **Tiempos y latencia:** El tiempo de red es estable (29,61 ± 4,61 ms),
  mientras que el cómputo en GPU sin caché promedia **53,29 ms**. La latencia
  extremo a extremo tiene una media de **65,17 ms** (IC 90 %: **[64,70;
  65,63] ms**).
- **Confiabilidad y estado actual del SLO:** La probabilidad de fallo por
  intento es **15,33 %** (IC 90 %: [14,99 %; 15,68 %]), pero los reintentos
  automáticos del SDK rescatan el **99,6 %** de las solicitudes. Sin embargo,
  con dos GPU la tasa de violación del umbral de 210 ms es **1,14 %**,
  superando marginalmente el objetivo máximo permitido del **1,00 %**.

## 2. Evaluación comparativa: Versión B vs. Versión A (P2)

**Recomendación proporcionada: No desplegar la Versión B (mantener A).**

El experimento aleatorio (12.411 solicitudes en A vs. 12.545 en B, grupos
descritos como balanceados en tamaño de imagen y tasa de caché) se presenta con
intervalos conjuntos del 90 % mediante Bonferroni:

| Métrica | A | B | Diferencia B−A | IC 90 % conjunto | p |
|---|---:|---:|---:|---:|---:|
| Tiempo GPU sin caché | 53,02 ms | 53,55 ms | +0,53 ms | [−0,77; +1,83] ms | 0,3845 |
| Probabilidad de reintento | 14,98 % | 15,62 % | +0,64 pp | [−0,33; +1,61] pp | 0,1621 |
| Violación de SLO | 1,10 % | 1,18 % | +0,08 pp | [−0,20; +0,37] pp | 0,5318 |

## 3. Plan de capacidad y regla de alertas ante crecimiento del 50 % (P3)

- **Capacidad propuesta:** para 36,34 solicitudes/s y P(L > 210 ms) ≤ 1 %,
  ampliar de dos a cuatro GPU. Cifras facilitadas: con dos GPU 3,13 % de
  violaciones (IC 90 % [3,03 %; 3,22 %]); con tres 1,01 % (IC [0,98 %;
  1,03 %]) y 50 % de riesgo bajo incertidumbre; con cuatro 0,90 % (IC
  [0,89 %; 0,92 %]) y 28,5 % de utilización.
- **Regla propuesta:** «D1 y D2», con 2,41 falsas alarmas/día y 73,1 % de
  probabilidad de incidente por alerta; el texto suministrado la presenta como
  la única que cumpliría la exigencia de ocho falsas alarmas diarias.
- **Riesgos propuestos:** mantener la distribución de tamaños y el caché;
  la ventana de validación con 29.485 solicitudes mostró una tasa de fallos
  por intento de 20,5 %, por lo que se propone auditar los workers GPU.

Las afirmaciones y decisiones anteriores están pendientes de reconciliarse con
los resultados reproducidos y su incertidumbre. En particular, no rechazar una
diferencia estadística no demuestra equivalencia, y baja utilización no prueba
por sí sola el cumplimiento del SLO.
