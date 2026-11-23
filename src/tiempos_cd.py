"""C1, C3 y C4 con las convenciones elegidas por el estudiante."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy import stats

from tiempos_c2 import estimar_gamma, estimar_lognormal

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
SEED = 2046185499


def datos_estables():
    data = pd.read_csv(OUT / "A1" / "solicitudes_auditadas.csv")
    stable = ((data.t_llegada_s >= 0) & (data.t_llegada_s < 668)) | (
        (data.t_llegada_s >= 838) & (data.t_llegada_s <= 1200))
    data = data.loc[stable].copy()
    cols = ["cache_hit", "gpu_ms", "red_ms"]
    if data[cols].isna().any().any():
        raise ValueError("Hay datos faltantes en el régimen estable")
    return data


def guardar(name, result):
    target = OUT / name
    target.mkdir(parents=True, exist_ok=True)
    (target / "resultados.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return target


def c1():
    data = datos_estables()
    gpu = data.gpu_ms.to_numpy(dtype=float)
    positive = data.loc[data.cache_hit == 0, "gpu_ms"].to_numpy(dtype=float)
    cached = data.loc[data.cache_hit == 1, "gpu_ms"].to_numpy(dtype=float)
    if np.any(cached != 0) or np.any(positive <= 0):
        raise ValueError("Los datos no cumplen la separación caché / GPU positiva")
    p = len(cached) / len(data)
    mu, var = positive.mean(), positive.var(ddof=0)
    mixture_mean = (1-p)*mu
    mixture_var = (1-p)*var + p*(1-p)*mu**2
    fitted = estimar_lognormal(positive)
    if not fitted["convergencia"]:
        raise RuntimeError("No convergió el ajuste lognormal de C1")
    result = {"n": len(gpu), "n_cache": len(cached), "n_positivos": len(positive),
              "p_cache": float(p), "mu_positiva_ms": float(mu),
              "var_positiva_ddof0_ms2": float(var), "media_modelo_ms": float(mixture_mean),
              "media_empirica_ms": float(gpu.mean()), "var_modelo_ddof0_ms2": float(mixture_var),
              "var_empirica_ddof0_ms2": float(gpu.var(ddof=0)),
              "var_muestral_ddof1_ms2": float(gpu.var(ddof=1)), "lognormal": fitted}
    if not np.isclose(mixture_var, gpu.var(ddof=0), rtol=1e-12, atol=1e-9):
        raise AssertionError("La descomposición de varianza no coincide")
    target = guardar("C1", result)
    values = np.sort(gpu)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.step(np.r_[-1., values], np.r_[0., np.arange(1, len(values)+1)/len(values)],
            where="post", label="FDA empírica mixta")
    grid = np.linspace(0, np.quantile(positive, .997), 500)
    param = p + (1-p)*stats.lognorm.cdf(grid, fitted["sigma_log"], scale=np.exp(fitted["mu_log_ms"]))
    ax.plot(grid, param, label="Masa en 0 + lognormal MLE")
    ax.vlines(0, 0, p, colors="black", linestyles="dotted", label="Salto en 0")
    ax.set(xlabel="Tiempo de GPU G (ms)", ylabel="Probabilidad acumulada",
           title="Figura 2. FDA de GPU con masa puntual en cero", xlim=(-3, grid[-1]), ylim=(0, 1.02))
    ax.legend()
    fig.tight_layout(); fig.savefig(target / "figura_2_fda_gpu.png", dpi=160); plt.close(fig)
    return result


def c3(seed=SEED, replicas=2000):
    data = datos_estables()
    red = data.red_ms.to_numpy(dtype=float)
    series = pd.Series(red)
    mean, sd = red.mean(), red.std(ddof=1)
    z = (red-mean)/sd
    ks = stats.kstest(z, "norm")
    ad = stats.anderson(red, dist="norm")
    rng = np.random.default_rng(seed)
    quantiles = np.empty(replicas)
    for start in range(0, replicas, 50):
        count = min(50, replicas-start)
        samples = rng.choice(red, size=(count, len(red)), replace=True)
        quantiles[start:start+count] = np.quantile(samples, .999, axis=1)
    intervals = np.quantile(quantiles, [.05, .95])
    tails = [{"umbral_ms": threshold, "empirica": float(np.mean(red > threshold)),
              "normal": float(stats.norm.sf(threshold, loc=mean, scale=sd))}
             for threshold in (35, 40, 45)]
    result = {"n": len(red), "scipy_version": scipy.__version__,
              "media_ms": float(mean), "desviacion_muestral_ms": float(sd),
              "asimetria_corregida": float(series.skew()), "exceso_curtosis_corregido": float(series.kurt()),
              "KS_D": float(ks.statistic), "KS_p_nominal_parametros_estimados": float(ks.pvalue),
              "AD_estadistico": float(ad.statistic), "AD_valores_criticos": ad.critical_values.tolist(),
              "AD_significancias_pct": ad.significance_level.tolist(), "colas": tails,
              "AD_critico_10_scipy_instalado": float(ad.critical_values[np.flatnonzero(ad.significance_level == 10)[0]]),
              "AD_referencia_10_indicada_por_estudiante": .656,
              "AD_decision_referencia_estudiante": "no rechaza" if ad.statistic < .656 else "rechaza",
              "percentil_empirico_999_ms": float(np.quantile(red, .999)),
              "bootstrap_percentil_replicas": replicas, "bootstrap_confianza": .90,
              "bootstrap_IC_ms": intervals.tolist(),
              "percentil_normal_999_ms": float(stats.norm.ppf(.999, loc=mean, scale=sd)),
              "nota": "KS con parámetros ajustados: p nominal; el bootstrap remuestrea observaciones, no bloques temporales. "
                      "El crítico 0,656 es la referencia elegida por el estudiante; SciPy 1.18.1 calcula 0,631, por lo que no se atribuye 0,656 a esa versión."}
    target = guardar("C3", result)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].hist(red, bins=60, density=True, alpha=.55, label="Red observada")
    grid = np.linspace(red.min(), red.max(), 400)
    axes[0].plot(grid, stats.norm.pdf(grid, loc=mean, scale=sd), label="Normal ajustada")
    axes[0].set(xlabel="Tiempo de red (ms)", ylabel="Densidad (1/ms)", title="Tiempo de red")
    axes[0].legend()
    theoretical, ordered = stats.probplot(red, dist="norm", fit=False)
    axes[1].scatter(theoretical, ordered, s=4, alpha=.3, label="Cuantiles observados")
    axes[1].plot(theoretical, mean+sd*theoretical, color="tab:red", label="Normal ajustada")
    axes[1].set(xlabel="Cuantil normal estándar", ylabel="Tiempo de red observado (ms)", title="Gráfico Q–Q")
    axes[1].legend()
    fig.tight_layout(); fig.savefig(target / "figura_3_red.png", dpi=160); plt.close(fig)
    return result


def c4(seed=SEED, replicas=200000, N=16):
    data = datos_estables()
    positive = data.loc[data.cache_hit == 0, "gpu_ms"].to_numpy(dtype=float)
    if np.any(positive <= 0):
        raise ValueError("Se encontraron tiempos de GPU no positivos sin caché")
    mean, var = positive.mean(), positive.var(ddof=1)
    threshold = N*(mean+15)
    gamma = estimar_gamma(positive)
    if not gamma["convergencia"]:
        raise RuntimeError("No convergió el ajuste Gamma de C4")
    normal = float(stats.norm.sf(threshold, loc=N*mean, scale=np.sqrt(N*var)))
    gamma_tail = float(stats.gamma.sf(threshold, a=N*gamma["k"], scale=gamma["theta_ms"]))
    rng = np.random.default_rng(seed)
    hits = 0
    for start in range(0, replicas, 10000):
        size = min(10000, replicas-start)
        blocks = rng.choice(positive, size=(size, N), replace=True)
        hits += int(np.count_nonzero(blocks.sum(axis=1) > threshold))
    mc = hits/replicas
    mc_interval = stats.binomtest(hits, replicas).proportion_ci(confidence_level=.90)
    result = {"N": N, "n_positivos": len(positive), "media_ms": float(mean),
              "var_muestral_ms2": float(var), "umbral_ms": float(threshold),
              "prob_normal": normal, "prob_gamma": gamma_tail,
              "prob_remuestreo_iid": mc, "replicas": replicas,
              "IC_monte_carlo_90": [float(mc_interval.low), float(mc_interval.high)],
              "nota": "El remuestreo i.i.d. usa la distribución empírica; no preserva dependencia temporal ni prueba que sea la distribución poblacional."}
    guardar("C4", result)
    return result
