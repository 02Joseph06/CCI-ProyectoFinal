# MEMORANDO EJECUTIVO — BORRADOR PARA REVISIÓN



Para: Dirección Técnica (CTO), Andes Vision AI | De: Equipo SRE y Datos

Fecha: 22 de noviembre de 2026 | Asunto: confiabilidad, versiones y capacidad

ESTADO: cifras calculadas con hipótesis y discrepancias pendientes; no es una recomendación validada.

1. SERVICIO OBSERVADO

En 1.030 s estables se retuvieron 24.956 solicitudes: tasa 24.229/s (IC 95% [23.929; 24.532]) y caché 41.11%. La latencia media es 65.17 ms; el bootstrap por bloques da [64.43; 65.94] ms. La tasa se refiere a filas conservadas tras auditoría.

La proporción observada de latencias superiores a 190 ms es 1.90%. En F6, la estimación de fallos por intento cambia de 15.33% a 20.47%; la estabilidad de todas las distribuciones y la causa del cambio no están demostradas.

2. COMPARACIÓN B − A

GPU sin caché: +0.530 ms; IC conjunto 95% [-0.930; 1.990] ms. Reintentos: +0.637 puntos porcentuales; violación del SLO: +0.108 puntos porcentuales. La decisión sobre la versión debe considerar los intervalos completos; no rechazar una diferencia no prueba equivalencia.

3. CAPACIDAD Y ALERTAS: RESULTADOS CONDICIONALES

Con el tráfico multiplicado por 1.5, G2 estima violaciones de 4.58%, 1.58% y 1.39% para 2, 3 y 4 GPU. En G1 la cola simulada (2.13%) difiere de la observada (1.90%); los intervalos de G2 miden error de simulación con parámetros fijos.

Para D1 y D2, E estima 2.41 falsas alarmas/día y 75.6% de probabilidad de incidente por alerta en producción, bajo transportabilidad de tasas. La probabilidad puntual de no superar 6 falsas alarmas es 98.83%; con FPR en el extremo superior Wilson es 82.17%. El extremo conservador no cumple el 90 % exigido; se suponen minutos independientes y tasa constante.

En G3, la capacidad mínima fue 3/4/5 GPU en 100.0%/0.0%/0.0% de los escenarios. Con 3 GPU, cumplimiento puntual 100.0%; M/M/c estima 3.38% de violaciones. G3 usa el criterio puntual, cinco réplicas internas y posterior del modelo; G2 usa el límite superior del IC. El significado de los reintentos en la tasa observada sigue sin comprobarse.



Fuentes: salidas reproducibles B, C1, E2, E4, F2, F3, F6 y G1–G3; ver `documentos/calculos/discrepancias_pendientes.md`. 

Las cifras propuestas por el grupo están conservadas en `documentos/G4/memorando_aportado_por_el_grupo.md`.
