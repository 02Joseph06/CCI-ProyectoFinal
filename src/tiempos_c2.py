"""C2: máxima verosimilitud explícita para Gamma y lognormal sin usar .fit()."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize, special, stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "C2"


def estimar_gamma(values):
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.all(np.isfinite(x) & (x > 0)):
        raise ValueError("Gamma requiere observaciones positivas finitas")
    n, total, log_sum = len(x), x.sum(), np.log(x).sum()
    mean, variance = x.mean(), x.var(ddof=1)
    initial = np.log([mean**2 / variance, variance / mean])

    def objective(log_params):
        k, theta = np.exp(log_params)
        loglik = (k - 1) * log_sum - total / theta - n * (special.gammaln(k) + k * np.log(theta))
        grad_k = k * (log_sum - n * (special.digamma(k) + np.log(theta)))
        grad_theta = total / theta - n * k
        return -loglik / n, -np.array([grad_k, grad_theta]) / n

    result = optimize.minimize(objective, initial, jac=True, method="BFGS", options={"gtol": 1e-8})
    k, theta = np.exp(result.x)
    return {"k": float(k), "theta_ms": float(theta), "log_verosimilitud": float(-n * result.fun),
            "convergencia": bool(result.success), "mensaje": str(result.message),
            "gradiente_norma": float(np.linalg.norm(result.jac)),
            "momentos_k": float(mean**2 / variance), "momentos_theta_ms": float(variance / mean)}


def estimar_lognormal(values):
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.all(np.isfinite(x) & (x > 0)):
        raise ValueError("Lognormal requiere observaciones positivas finitas")
    logs = np.log(x)
    n = len(x)

    def objective(params):
        mu, log_sigma = params
        sigma = np.exp(log_sigma)
        residual = logs - mu
        loglik = -logs.sum() - n * (log_sigma + .5 * np.log(2*np.pi)) - (residual @ residual)/(2*sigma**2)
        gradient = np.array([residual.sum()/sigma**2, -n + (residual @ residual)/sigma**2])
        return -loglik / n, -gradient / n

    initial = np.array([logs.mean(), np.log(logs.std(ddof=0))])
    result = optimize.minimize(objective, initial, jac=True, method="BFGS", options={"gtol": 1e-9})
    return {"mu_log_ms": float(result.x[0]), "sigma_log": float(np.exp(result.x[1])),
            "log_verosimilitud": float(-n * result.fun), "convergencia": bool(result.success),
            "mensaje": str(result.message), "gradiente_norma": float(np.linalg.norm(result.jac))}


def main():
    df = pd.read_csv(ROOT / "outputs" / "A1" / "solicitudes_auditadas.csv")
    selected = df[((df.t_llegada_s >= 0) & (df.t_llegada_s < 668)) |
                  ((df.t_llegada_s >= 838) & (df.t_llegada_s <= 1200))]
    positive = selected.loc[selected.cache_hit == 0, "gpu_ms"].to_numpy()
    gamma = estimar_gamma(positive)
    lognormal = estimar_lognormal(positive)
    if not gamma["convergencia"] or not lognormal["convergencia"]:
        raise RuntimeError(f"Al menos un optimizador no convergió: {gamma['mensaje']}; {lognormal['mensaje']}")
    gamma["ks_distancia"] = float(stats.kstest(positive, lambda z: stats.gamma.cdf(z, gamma["k"], scale=gamma["theta_ms"])).statistic)
    lognormal["ks_distancia"] = float(stats.kstest(positive, lambda z: stats.lognorm.cdf(z, lognormal["sigma_log"], scale=np.exp(lognormal["mu_log_ms"]))).statistic)
    result = {"n_sin_cache": len(positive), "gamma": gamma, "lognormal": lognormal,
              "nota_ks": "Distancia descriptiva con parámetros estimados en los mismos datos; no es una prueba calibrada."}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ajustes.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(positive, bins=80, density=True, alpha=.45, label="GPU sin caché: datos")
    grid = np.linspace(0, np.quantile(positive, .995), 500)
    ax.plot(grid, stats.gamma.pdf(grid, gamma["k"], scale=gamma["theta_ms"]), label="Gamma: MLE")
    ax.plot(grid, stats.lognorm.pdf(grid, lognormal["sigma_log"], scale=np.exp(lognormal["mu_log_ms"])), label="Lognormal: MLE")
    ax.set(xlim=(0, grid[-1]), title="C2. Distribución del tiempo de GPU sin caché",
           xlabel="Tiempo de GPU (ms)", ylabel="Densidad (1/ms)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "ajustes_gpu.png", dpi=160)
    plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
