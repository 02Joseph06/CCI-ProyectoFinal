"""Partes B1–B4: requiere la semilla real del grupo, nunca una inventada."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "B"


def profile_interval(failures, trials, confidence):
    p = failures / trials
    def ll(x):
        return stats.binom.logpmf(failures, trials, x)
    target = ll(p) - stats.chi2.ppf(confidence, 1) / 2
    f = lambda x: ll(x) - target
    low = 0.0 if failures == 0 else optimize.brentq(f, 1e-12, p)
    high = 1.0 if failures == trials else optimize.brentq(f, p, 1-1e-12)
    return [low, high]


def main(seed):
    if not isinstance(seed, int) or seed < 0:
        raise ValueError("S debe ser la suma no negativa real de las identificaciones")
    OUT.mkdir(parents=True, exist_ok=True)
    confidence = {0: .90, 1: .95, 2: .99}[seed % 3]
    alpha = 1 - confidence
    rng = np.random.default_rng(seed)
    df = pd.read_csv(ROOT / "outputs" / "A1" / "solicitudes_auditadas.csv")
    df = df.dropna(subset=["t_llegada_s"]).sort_values("t_llegada_s")
    # Se usa el primer tramo estable, evitando unir tramos separados en el tiempo.
    stable = df[(df.t_llegada_s >= 0) & (df.t_llegada_s < 670)].copy()
    burst = df[(df.t_llegada_s >= 670) & (df.t_llegada_s < 840)].copy()
    n = len(stable)
    duration = 670
    rate = n / duration
    rate_ci = [stats.chi2.ppf(alpha / 2, 2*n) / (2*duration),
               stats.chi2.ppf(1-alpha / 2, 2*(n+1)) / (2*duration)]
    gaps = np.diff(stable.t_llegada_s.to_numpy())
    # La telemetría registra tiempos con precisión de 0,0001 s: puede haber empates.
    gap_mean = gaps.mean()
    observed_ks = stats.kstest(gaps, "expon", args=(0, gap_mean)).statistic
    reps = 400
    simulated_ks = np.empty(reps)
    for i in range(reps):
        simulated = rng.exponential(gap_mean, len(gaps))
        simulated_ks[i] = stats.kstest(simulated, "expon", args=(0, simulated.mean())).statistic
    ks_p = (1 + np.count_nonzero(simulated_ks >= observed_ks)) / (reps + 1)
    counts, _ = np.histogram(stable.t_llegada_s, bins=np.arange(0, 671, 10))
    dispersion = counts.var(ddof=1) / counts.mean()
    chi = (len(counts)-1) * dispersion
    dispersion_p = min(1., 2 * min(stats.chi2.cdf(chi, len(counts)-1),
                                   stats.chi2.sf(chi, len(counts)-1)))
    b1 = dict(n=n, duration_s=duration, rate_s=rate, confidence=confidence,
              rate_interval=rate_ci, mean_gap_s=gap_mean, ks_stat=observed_ks,
              ks_bootstrap_p=ks_p, bootstrap_replicas=reps,
              count_window_s=10, fano=dispersion, dispersion_p=dispersion_p,
              ties=int((gaps == 0).sum()))

    block_results = []
    for name, group in [("estable", stable), ("alta_carga", burst)]:
        retry = (group.intentos.to_numpy() > 1).astype(int)
        num_blocks = len(retry)//100
        blocks = retry[:100*num_blocks].reshape(num_blocks, 100).sum(axis=1)
        p = retry.mean()
        theoretical_variance = 100*p*(1-p)
        block_results.append(dict(regimen=name, solicitudes=len(retry), bloques=num_blocks,
            solicitudes_restantes=len(retry)-100*num_blocks, proporcion=p,
            media_bloques=blocks.mean(), media_binomial=100*p,
            varianza_bloques=blocks.var(ddof=1), varianza_binomial=theoretical_variance,
            dispersion=blocks.var(ddof=1)/theoretical_variance))
        pd.DataFrame({"bloque": np.arange(1, num_blocks+1), "reintentos": blocks}).to_csv(
            OUT / f"B2_bloques_{name}.csv", index=False)
    pd.DataFrame(block_results).to_csv(OUT / "B2_contraste.csv", index=False)

    attempts = stable.intentos.to_numpy(dtype=int)
    successes = stable.exito.to_numpy(dtype=int)
    failures = int((attempts-successes).sum())
    trials = int(attempts.sum())
    p_failure = failures/trials
    p_ci = profile_interval(failures, trials, confidence)
    naive = 1 - 1/attempts.mean()
    simulations = 1000
    estimates = np.empty((simulations, 2))
    # Cada fila representa intentos independientes hasta éxito, truncados en tres.
    for i in range(simulations):
        fails = rng.random((n, 3)) < p_failure
        simulated_attempts = 1 + fails[:, 0] + (fails[:, 0] & fails[:, 1])
        total_failures = fails[:, 0].sum() + (fails[:, 0] & fails[:, 1]).sum() + (
            fails[:, 0] & fails[:, 1] & fails[:, 2]).sum()
        estimates[i, 0] = total_failures/simulated_attempts.sum()
        estimates[i, 1] = 1 - 1/simulated_attempts.mean()
    b3 = dict(n=n, observed_failures=failures, observed_attempts=trials,
              failure_probability=p_failure, profile_interval=p_ci, naive=naive,
              simulation_replicas=simulations,
              bias_mle=float(estimates[:, 0].mean()-p_failure),
              bias_naive=float(estimates[:, 1].mean()-p_failure),
              rmse_mle=float(np.sqrt(np.mean((estimates[:, 0]-p_failure)**2))),
              rmse_naive=float(np.sqrt(np.mean((estimates[:, 1]-p_failure)**2))))

    p_retry = float((stable.intentos > 1).mean())
    mu = 10*rate*p_retry
    k = int(np.ceil(mu)) + seed % 6
    analytic = float(stats.poisson.sf(k-1, mu))
    mc_n = 200000
    mc_samples = rng.poisson(mu, size=mc_n)
    hits = int(np.count_nonzero(mc_samples >= k))
    mc = hits/mc_n
    mc_ci = stats.binomtest(hits, mc_n).proportion_ci(confidence_level=confidence)
    b4 = dict(p_retry=p_retry, mu_10s=mu, r=seed%6, k=k,
              probability_analytic=analytic, probability_mc=mc, mc_replicas=mc_n,
              mc_interval=[mc_ci.low, mc_ci.high])
    result = dict(B1=b1, B2=block_results, B3=b3, B4=b4)
    with (OUT / "resultados.json").open("w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].hist(gaps, bins=60, density=True, alpha=.6, label="Datos")
    xs = np.linspace(0, np.quantile(gaps, .995), 250)
    axes[0].plot(xs, stats.expon.pdf(xs, scale=gap_mean), label="Exponencial ajustada")
    axes[0].set(xlim=(0, xs[-1]), xlabel="Tiempo entre llegadas (s)", ylabel="Densidad (1/s)", title="Tiempos entre llegadas")
    axes[0].legend()
    axes[1].hist(counts, bins=15, alpha=.7, label="Conteos observados")
    axes[1].set(xlabel="Llegadas en 10 s", ylabel="Número de intervalos", title="Conteos en el régimen estable")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "B1_llegadas.png", dpi=160)
    plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--semilla", type=int, required=True)
    main(parser.parse_args().semilla)
