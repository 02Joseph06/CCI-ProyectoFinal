"""G1/G2: simulador FIFO explícito calibrado con B, C y el régimen de A.

La simulación usa solicitudes observadas como unidad de llegada; que estas
incluyan los reintentos individuales es una hipótesis sin verificar.
"""
from pathlib import Path
import heapq
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SEED = 2046185499


def simular_fifo(rng, tasa_s, prob_cache, mu_log, sigma_log, red_media,
                  red_desv, servidores, duracion_s, calentamiento_s=0):
    """Devuelve latencias de llegadas observadas tras un calentamiento FIFO.

    Cache responde con red solamente. El reloj de la cola está en segundos;
    red, servicio y resultado están en milisegundos. Cada llamada empieza vacía.
    """
    if tasa_s <= 0 or servidores < 1 or duracion_s <= 0 or calentamiento_s < 0:
        raise ValueError("Parámetros de simulación inválidos")
    if not 0 <= prob_cache <= 1 or sigma_log <= 0 or red_desv <= 0:
        raise ValueError("Distribuciones inválidas")
    final = calentamiento_s + duracion_s
    n = rng.poisson(tasa_s * final)
    llegada = np.sort(rng.uniform(0, final, n))
    cache = rng.random(n) < prob_cache
    red = rng.normal(red_media, red_desv, n)
    servicio = np.zeros(n)
    servicio[~cache] = rng.lognormal(mu_log, sigma_log, (~cache).sum())
    libres = [0.0] * servidores
    heapq.heapify(libres)
    espera = np.zeros(n)
    for i in np.flatnonzero(~cache):
        disponible = heapq.heappop(libres)
        inicio = max(disponible, llegada[i])
        espera[i] = (inicio - llegada[i]) * 1000
        heapq.heappush(libres, inicio + servicio[i] / 1000)
    return (red + espera + servicio)[llegada >= calentamiento_s]


def _intervalo_replicas(values, nivel=.90):
    values = np.asarray(values, dtype=float)
    media = values.mean()
    margen = stats.t.ppf((1 + nivel) / 2, len(values) - 1) * stats.sem(values)
    return float(media), float(media - margen), float(media + margen)


def mmc_espera(tasa_gpu_s, media_servicio_ms, servidores):
    """Diagnóstico M/M/c para las solicitudes sin caché: P(espera), E[Wq].

    Este contraste no calcula P(L > τ): la regla de combinación con red y
    respuestas cacheadas debe especificarla el grupo.
    """
    if tasa_gpu_s <= 0 or media_servicio_ms <= 0 or servidores < 1:
        raise ValueError("Parámetros M/M/c inválidos")
    carga = tasa_gpu_s * media_servicio_ms / 1000
    rho = carga / servidores
    if rho >= 1:
        return rho, np.nan, np.nan
    term = 1.0
    suma = 1.0
    for n in range(1, servidores):
        term *= carga / n
        suma += term
    term *= carga / servidores
    cola = term / (1 - rho)
    prob_espera = cola / (suma + cola)
    espera_ms = 1000 * prob_espera / (servidores * (1000 / media_servicio_ms) - tasa_gpu_s)
    return rho, prob_espera, espera_ms


def main(seed=SEED):
    rng = np.random.default_rng(seed)
    data = pd.read_csv(ROOT / "outputs/A1/solicitudes_auditadas.csv")
    t = data.t_llegada_s
    stable = data[((t >= 0) & (t < 668)) | ((t >= 838) & (t <= 1200))]
    c2 = json.loads((ROOT / "outputs/C2/ajustes.json").read_text(encoding="utf-8"))
    c3 = json.loads((ROOT / "outputs/C3/resultados.json").read_text(encoding="utf-8"))
    mu = c2["lognormal"]["mu_log_ms"]
    sigma = c2["lognormal"]["sigma_log"]
    lam = len(stable) / 1030
    hit = float(stable.cache_hit.mean())
    red_mu, red_sd = c3["media_ms"], c3["desviacion_muestral_ms"]
    args = (hit, mu, sigma, red_mu, red_sd)

    # Réplicas independientes (subconjuntos sucesivos de un solo generador).
    rows = []
    for _ in range(20):
        lat = simular_fifo(rng, lam, *args, 2, 1030)
        rows.append([np.median(lat), np.quantile(lat, .95), np.mean(lat > 210)])
    rows = np.asarray(rows)
    empirical = stable.latencia_ms.to_numpy()
    measurements = [np.median(empirical), np.quantile(empirical, .95), np.mean(empirical > 210)]
    records = []
    for i, metric in enumerate(("mediana_ms", "p95_ms", "proporcion_mayor_210_ms")):
        mean, low, high = _intervalo_replicas(rows[:, i])
        records.append(dict(metrica=metric, observado=float(measurements[i]), simulado=mean,
                            ic_90_inferior=low, ic_90_superior=high,
                            diferencia_simulado_menos_observado=mean-measurements[i], replicas=20))
    out1 = ROOT / "outputs/G1"
    out1.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(out1 / "validacion_simulador_G1.csv", index=False)

    projection = []
    for c in range(1, 6):
        props = []
        for _ in range(30):
            lat = simular_fifo(rng, lam * 1.5, *args, c, 600, 30)
            props.append(float(np.mean(lat > 210)))
        mean, low, high = _intervalo_replicas(props)
        # La media teórica lognormal permite que utilización y modelo coincidan.
        rho = lam * 1.5 * (1 - hit) * np.exp(mu + sigma**2 / 2) / (1000 * c)
        projection.append(dict(gpus=c, rho=rho, violacion=mean, ic_90_inferior=low,
                               ic_90_superior=high, replicas=30,
                               duracion_s=600, calentamiento_s=30,
                               estable_rho_menor_1=bool(rho < 1)))
    out2 = ROOT / "outputs/G2"
    out2.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(projection)
    table.to_csv(out2 / "capacidad_proyeccion_G2.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    # El primer caso es inestable y su resultado se refiere al horizonte finito.
    ax.errorbar(table.gpus, table.violacion,
                yerr=[table.violacion-table.ic_90_inferior,
                      table.ic_90_superior-table.violacion], fmt="o-", capsize=4,
                label="Simulación; IC 90 % entre réplicas")
    ax.axhline(.01, color="red", linestyle="--", label="Objetivo: 1 %")
    ax.set(xlabel="Número de GPU", ylabel="Proporción de latencias > 210 ms",
           title="Figura 9. Capacidad proyectada: g = 1,5")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out2 / "figura_9_capacidad_slo.png", dpi=160)
    plt.close(fig)
    metadata = {"S": seed, "lambda_base_s": lam, "lambda_proyectada_s": lam*1.5,
                "prob_cache": hit, "media_lognormal_ms": float(np.exp(mu + sigma**2/2)),
                "modelo": "Poisson, caché Bernoulli, red normal, servicio lognormal independiente, FIFO",
                "limitacion": "λ cuenta filas de solicitudes; no se sabe si incluye reintentos individuales. "
                              "La red normal puede ser negativa, con probabilidad ínfima. "
                              "c=1 es inestable: el resultado describe solo el horizonte finito. "
                              "IC entre réplicas no incluye incertidumbre de calibración."}
    (out2 / "parametros_y_limites.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    out3 = ROOT / "outputs/G3"
    out3.mkdir(parents=True, exist_ok=True)
    mmc = []
    for c in range(1, 6):
        rho, p_wait, wait_ms = mmc_espera(lam * 1.5 * (1-hit), np.exp(mu + sigma**2/2), c)
        mmc.append(dict(gpus=c, rho=rho, probabilidad_espera=p_wait,
                        espera_media_ms=wait_ms, estable=bool(rho < 1)))
    pd.DataFrame(mmc).to_csv(out3 / "contraste_mmc_parcial.csv", index=False)
    print(pd.DataFrame(records).to_string(index=False))
    print(table.to_string(index=False))
    return records, table


if __name__ == "__main__":
    main()
