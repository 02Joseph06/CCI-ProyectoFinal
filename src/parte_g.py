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
from scipy import stats, integrate
from parametros import S as SEED, CONFIANZA, TAU_MS, EPSILON, CRECIMIENTO

ROOT = Path(__file__).resolve().parents[1]


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


def _intervalo_replicas(values, nivel=CONFIANZA):
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


def evaluar_escenarios_g3(escenarios, servidores, rng, replicas, duracion_s,
                          calentamiento_s, umbral_ms, epsilon, regla,
                          simulador=simular_fifo):
    """Evalúa escenarios suministrados por el usuario, sin generarlos.

    Cada escenario debe contener tasa_s, prob_cache, mu_log, sigma_log,
    red_media y red_desv. Se conserva su dependencia conjunta: el llamador
    es responsable de construir cada fila y documentar su procedimiento.
    `regla` es 'estimacion' o 'limite_superior'; la segunda usa un IC t
    entre réplicas de simulación, no un IC de los parámetros calibrados.
    Devuelve una fila por escenario y capacidad. Ningún c cumple si su cola
    es inestable. Una capacidad sin cumplimiento queda como valor faltante.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng debe ser un numpy.random.Generator")
    if replicas < 2 or int(replicas) != replicas:
        raise ValueError("Se necesitan al menos dos réplicas enteras")
    if regla not in ("estimacion", "limite_superior"):
        raise ValueError("Seleccione explícitamente la regla de cumplimiento")
    if (not np.isfinite(umbral_ms) or not 0 <= epsilon <= 1
            or not np.isfinite(duracion_s) or duracion_s <= 0
            or not np.isfinite(calentamiento_s) or calentamiento_s < 0):
        raise ValueError("Umbral o tolerancia no válidos")
    capacidades = list(servidores)
    if not capacidades or any(int(c) != c or c < 1 for c in capacidades):
        raise ValueError("Las capacidades deben ser enteros positivos")
    if len(set(capacidades)) != len(capacidades):
        raise ValueError("Las capacidades no pueden repetirse")
    capacidades = sorted(int(c) for c in capacidades)
    nombres = ("tasa_s", "prob_cache", "mu_log", "sigma_log", "red_media", "red_desv")
    filas = []
    for indice, escenario in enumerate(escenarios):
        valores = [float(escenario[nombre]) for nombre in nombres]
        tasa, cache, mu, sigma, red_mu, red_sd = valores
        if (not np.all(np.isfinite(valores)) or tasa <= 0 or not 0 <= cache <= 1
                or sigma <= 0 or red_sd <= 0):
            raise ValueError(f"Escenario {indice}: parámetros no válidos")
        media_gpu = np.exp(mu + sigma**2 / 2)
        if not np.isfinite(media_gpu):
            raise ValueError(f"Escenario {indice}: media lognormal no finita")
        escenario_filas = []
        for c in capacidades:
            rho = tasa * (1 - cache) * media_gpu / (1000 * c)
            fila = {"escenario": indice, "gpus": c, "rho": rho,
                    "estable": bool(rho < 1), "violacion": np.nan,
                    "ic_inferior": np.nan, "ic_superior": np.nan,
                    "nivel_confianza": CONFIANZA,
                    "cumple": False}
            if rho < 1:
                proporciones = []
                for _ in range(int(replicas)):
                    latencias = np.asarray(simulador(
                        rng, tasa, cache, mu, sigma, red_mu, red_sd,
                        c, duracion_s, calentamiento_s), dtype=float)
                    if not latencias.size or not np.all(np.isfinite(latencias)):
                        raise ValueError("Simulación vacía o con latencias no finitas")
                    proporciones.append(np.mean(latencias > umbral_ms))
                media, inferior, superior = _intervalo_replicas(proporciones)
                criterio = media if regla == "estimacion" else superior
                fila.update(violacion=media, ic_inferior=inferior,
                            ic_superior=superior, cumple=bool(criterio <= epsilon))
            escenario_filas.append(fila)
        elegibles = [f["gpus"] for f in escenario_filas if f["cumple"]]
        c_optimo = min(elegibles) if elegibles else np.nan
        for fila in escenario_filas:
            fila["c_optimo_entre_capacidades_evaluadas"] = c_optimo
        filas.extend(escenario_filas)
    if not filas:
        raise ValueError("Debe suministrar al menos un escenario")
    return pd.DataFrame(filas)


def generar_escenarios_g3(stable, rng, n_escenarios=200, duracion_estable=1030,
                          crecimiento=CRECIMIENTO):
    """Posteriores independientes de llegada, caché y parámetros lognormales."""
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng debe ser un numpy.random.Generator")
    if n_escenarios < 1 or int(n_escenarios) != n_escenarios or duracion_estable <= 0 or crecimiento <= 0:
        raise ValueError("Configuración de escenarios inválida")
    if not set(stable.cache_hit.unique()).issubset({0, 1}):
        raise ValueError("cache_hit debe ser binario")
    n = len(stable)
    k = int(stable.cache_hit.sum())
    gpu = stable.loc[stable.cache_hit == 0, "gpu_ms"].to_numpy(dtype=float)
    red = stable.red_ms.to_numpy(dtype=float)
    if n < 2 or len(gpu) < 2 or np.any(gpu <= 0) or not np.isfinite(gpu).all() or not np.isfinite(red).all():
        raise ValueError("Datos insuficientes o inválidos")
    y = np.log(gpu)
    media, s2 = y.mean(), y.var(ddof=1)
    n_s = int(n_escenarios)
    tasa = crecimiento * rng.gamma(n, 1 / duracion_estable, n_s)
    cache = rng.beta(k + .5, n - k + .5, n_s)
    sigma2 = (len(gpu) - 1) * s2 / rng.chisquare(len(gpu) - 1, n_s)
    mu = rng.normal(media, np.sqrt(sigma2 / len(gpu)))
    return pd.DataFrame(dict(tasa_s=tasa, prob_cache=cache, mu_log=mu,
                             sigma_log=np.sqrt(sigma2), red_media=red.mean(),
                             red_desv=red.std(ddof=1)))


def mmc_cola_latencia(tasa, cache, mu, sigma, red_mu, red_sd, c, umbral=TAU_MS):
    """Cola total bajo M/M/c: caché/red independientes y servicio exponencial."""
    if cache == 1:
        return 0., float(stats.norm.sf((umbral-red_mu)/red_sd))
    media_servicio = np.exp(mu + sigma**2 / 2)
    rho, espera_prob, _ = mmc_espera(tasa * (1-cache), media_servicio, c)
    if rho >= 1:
        return rho, np.nan
    a = 1 / media_servicio  # tasas en ms^-1
    b = c * a - tasa * (1-cache) / 1000

    def cola_gpu(x):
        if x <= 0:
            return 1.0
        if np.isclose(a, b, rtol=1e-8):
            suma = np.exp(-a*x) * (1 + a*x)
        else:
            suma = (b*np.exp(-a*x) - a*np.exp(-b*x)) / (b-a)
        return (1-espera_prob)*np.exp(-a*x) + espera_prob*suma

    # Integración sobre R normal; S y W son independientes de R.
    z = (umbral-red_mu) / red_sd
    # Acotar la integral al soporte numérico de la normal evita que QUADPACK
    # omita toda la masa cuando z es muy grande (p. ej., z ≈ 39).
    integral = 0.0
    if z > -10:
        integral = integrate.quad(
            lambda u: stats.norm.pdf(u)*cola_gpu(umbral-red_mu-red_sd*u),
            -10, min(z, 10), epsabs=1e-10)[0]
    parte_no_cache = stats.norm.sf(z) + integral
    return rho, cache*stats.norm.sf(z) + (1-cache)*parte_no_cache


def ejecutar_g3(stable, seed=SEED, n_escenarios=200, replicas=5,
                 duracion_s=400, calentamiento_s=20, capacidades=(2, 3, 4, 5),
                 umbral_ms=TAU_MS, epsilon=EPSILON, crecimiento=CRECIMIENTO, guardar=True):
    """Genera y evalúa escenarios; conserva fallos de la rejilla seleccionada."""
    rng = np.random.default_rng(seed)
    if duracion_s <= calentamiento_s:
        raise ValueError("La duración total debe superar el calentamiento")
    escenarios = generar_escenarios_g3(stable, rng, n_escenarios, 1030, crecimiento)
    # simular_fifo recibe duración observada, no duración total.
    detalles = evaluar_escenarios_g3(escenarios.to_dict("records"), capacidades, rng,
                                      replicas, duracion_s - calentamiento_s, calentamiento_s,
                                      umbral_ms, epsilon, "estimacion")
    optimos = detalles.groupby("escenario").first().c_optimo_entre_capacidades_evaluadas
    distribucion = pd.DataFrame({"capacidad": [*sorted(capacidades), "sin capacidad en la rejilla"]})
    distribucion["escenarios"] = [int((optimos == c).sum()) for c in sorted(capacidades)] + [int(optimos.isna().sum())]
    distribucion["proporcion"] = distribucion.escenarios / len(optimos)
    resumen = detalles.groupby("gpus", as_index=False).agg(
        prob_cumplimiento=("cumple", "mean"), escenarios=("cumple", "size"),
        violacion_media=("violacion", "mean"), rho_media=("rho", "mean"))
    comparacion = []
    for c in sorted(capacidades):
        values = [mmc_cola_latencia(e.tasa_s, e.prob_cache, e.mu_log, e.sigma_log,
                                    e.red_media, e.red_desv, c, umbral_ms)[1]
                  for e in escenarios.itertuples(index=False)]
        valid = np.asarray(values)
        comparacion.append({"gpus": c, "violacion_media_mmc": np.nanmean(valid),
                            "prob_cumplimiento_mmc": np.mean(valid <= epsilon),
                            "escenarios_inestables_mmc": int(np.isnan(valid).sum())})
    resumen = resumen.merge(pd.DataFrame(comparacion), on="gpus")
    # Intervalos Wilson para el error de Monte Carlo entre escenarios.
    for tabla, columna in ((distribucion, "escenarios"), (resumen, "prob_cumplimiento")):
        if columna == "escenarios":
            exitos = tabla.escenarios.to_numpy(dtype=int)
        else:
            exitos = np.rint(tabla.prob_cumplimiento.to_numpy() * n_escenarios).astype(int)
        limites = [stats.binomtest(int(k), n_escenarios).proportion_ci(
            confidence_level=CONFIANZA, method="wilson") for k in exitos]
        tabla["ic_mc_inferior"] = [v.low for v in limites]
        tabla["ic_mc_superior"] = [v.high for v in limites]
        tabla["nivel_confianza"] = CONFIANZA
    if guardar:
        out = ROOT / "outputs/G3"
        out.mkdir(parents=True, exist_ok=True)
        escenarios.to_csv(out / "escenarios_G3.csv", index_label="escenario")
        detalles.to_csv(out / "detalle_escenarios_G3.csv", index=False)
        distribucion.to_csv(out / "distribucion_capacidad_G3.csv", index=False)
        resumen.to_csv(out / "robustez_c_G3.csv", index=False)
    return escenarios, detalles, distribucion, resumen


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
        rows.append([np.median(lat), np.quantile(lat, .95), np.mean(lat > TAU_MS)])
    rows = np.asarray(rows)
    empirical = stable.latencia_ms.to_numpy()
    measurements = [np.median(empirical), np.quantile(empirical, .95), np.mean(empirical > TAU_MS)]
    records = []
    for i, metric in enumerate(("mediana_ms", "p95_ms", f"proporcion_mayor_{TAU_MS}_ms")):
        mean, low, high = _intervalo_replicas(rows[:, i])
        records.append(dict(metrica=metric, observado=float(measurements[i]), simulado=mean,
                            ic_inferior=low, ic_superior=high, nivel_confianza=CONFIANZA,
                            diferencia_simulado_menos_observado=mean-measurements[i], replicas=20))
    out1 = ROOT / "outputs/G1"
    out1.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(out1 / "validacion_simulador_G1.csv", index=False)

    projection = []
    for c in range(1, 6):
        props = []
        for _ in range(30):
            lat = simular_fifo(rng, lam * CRECIMIENTO, *args, c, 600, 30)
            props.append(float(np.mean(lat > TAU_MS)))
        mean, low, high = _intervalo_replicas(props)
        # La media teórica lognormal permite que utilización y modelo coincidan.
        rho = lam * CRECIMIENTO * (1 - hit) * np.exp(mu + sigma**2 / 2) / (1000 * c)
        projection.append(dict(gpus=c, rho=rho, violacion=mean, ic_inferior=low,
                               ic_superior=high, nivel_confianza=CONFIANZA, replicas=30,
                               duracion_s=600, calentamiento_s=30,
                               estable_rho_menor_1=bool(rho < 1)))
    out2 = ROOT / "outputs/G2"
    out2.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(projection)
    table.to_csv(out2 / "capacidad_proyeccion_G2.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    # El primer caso es inestable y su resultado se refiere al horizonte finito.
    ax.errorbar(table.gpus, table.violacion,
                yerr=[table.violacion-table.ic_inferior,
                      table.ic_superior-table.violacion], fmt="o-", capsize=4,
                label=f"Simulación; IC {CONFIANZA:.0%} entre réplicas")
    ax.axhline(EPSILON, color="red", linestyle="--", label=f"Objetivo: {EPSILON:.0%}")
    ax.set(xlabel="Número de GPU", ylabel=f"Proporción de latencias > {TAU_MS} ms",
           title=f"Figura 9. Capacidad proyectada: g = {CRECIMIENTO:g}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out2 / "figura_9_capacidad_slo.png", dpi=160)
    plt.close(fig)
    metadata = {"S": seed, "lambda_base_s": lam, "lambda_proyectada_s": lam*CRECIMIENTO,
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
        rho, p_wait, wait_ms = mmc_espera(lam * CRECIMIENTO * (1-hit), np.exp(mu + sigma**2/2), c)
        mmc.append(dict(gpus=c, rho=rho, probabilidad_espera=p_wait,
                        espera_media_ms=wait_ms, estable=bool(rho < 1)))
    pd.DataFrame(mmc).to_csv(out3 / "contraste_mmc_parcial.csv", index=False)
    print(pd.DataFrame(records).to_string(index=False))
    print(table.to_string(index=False))
    return records, table


if __name__ == "__main__":
    main()
