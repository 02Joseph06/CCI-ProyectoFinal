"""Segmentación cuantitativa de las llegadas por tasas de Poisson por tramos."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "A2"


def segmentar(tiempos, ancho, max_segmentos=5, minimo_s=60):
    bordes = np.arange(0, 1200 + ancho, ancho)
    conteos, _ = np.histogram(tiempos, bins=bordes)
    n = len(conteos)
    minimo = int(np.ceil(minimo_s / ancho))
    suma = np.r_[0, np.cumsum(conteos)]
    # Perfil de log-verosimilitud de Poisson; las constantes se cancelan en BIC.
    def loglik(i, j):
        total = suma[j] - suma[i]
        return total * np.log(total / (j - i)) - total if total else 0.0
    dp = np.full((max_segmentos + 1, n + 1), -np.inf)
    prev = np.full((max_segmentos + 1, n + 1), -1, dtype=int)
    dp[0, 0] = 0.0
    for k in range(1, max_segmentos + 1):
        for j in range(k * minimo, n + 1):
            opciones = [(dp[k - 1, i] + loglik(i, j), i)
                        for i in range((k - 1) * minimo, j - minimo + 1)]
            dp[k, j], prev[k, j] = max(opciones)
    # Cuenta k tasas y k-1 ubicaciones de cambio; es un criterio aproximado.
    bic = [-2 * dp[k, n] + (2 * k - 1) * np.log(n)
           for k in range(1, max_segmentos + 1)]
    k = int(np.argmin(bic)) + 1
    segmentos = []
    j = n
    for step in range(k, 0, -1):
        i = prev[step, j]
        segmentos.append((int(bordes[i]), int(bordes[j]), int(suma[j] - suma[i])))
        j = i
    return list(reversed(segmentos)), bic


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / "outputs" / "A1" / "solicitudes_auditadas.csv")
    tiempos = df.t_llegada_s.dropna().to_numpy()
    records = []
    for ancho in (1, 5, 10, 15, 30):
        segments, bics = segmentar(tiempos, ancho)
        print(f"ancho={ancho}s segmentos={segments} BIC={np.round(bics, 1)}")
        for start, end, n in segments:
            records.append(dict(ancho_s=ancho, inicio_s=start, fin_s=end,
                                solicitudes=n, tasa_s=n / (end - start),
                                segmentos_seleccionados=len(segments), bic_min=min(bics)))
    pd.DataFrame(records).to_csv(OUT / "sensibilidad_segmentacion.csv", index=False)
    main_segments, _ = segmentar(tiempos, 1)
    first = df[(df.t_llegada_s >= 0) & (df.t_llegada_s < 668)].sort_values("t_llegada_s")
    last = df[(df.t_llegada_s >= 838) & (df.t_llegada_s <= 1200)].sort_values("t_llegada_s")
    comparisons = []
    for name, result in (
        ("KS tiempos entre llegadas", stats.ks_2samp(first.t_llegada_s.diff().dropna(),
                                                     last.t_llegada_s.diff().dropna())),
        ("KS latencia", stats.ks_2samp(first.latencia_ms, last.latencia_ms)),
        ("Mann-Whitney latencia", stats.mannwhitneyu(first.latencia_ms, last.latencia_ms)),
    ):
        comparisons.append(dict(prueba=name, estadistico=result.statistic, p_valor=result.pvalue))
    pd.DataFrame(comparisons).to_csv(OUT / "comparacion_tramos_estables.csv", index=False)
    print("Comparación de tramos:", comparisons)
    counts, edges = np.histogram(tiempos, bins=np.arange(0, 1210, 10))
    fig, (ax, lat, retry) = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    ax.step(edges[:-1], counts / 10, where="post", label="Tasa por intervalos de 10 s")
    for index, (start, end, n) in enumerate(main_segments):
        ax.hlines(n / (end-start), start, end, colors="tab:red", linewidth=2,
                  label="Tasa estimada por tramo" if index == 0 else None)
        ax.axvline(start, color="black", linestyle="--", alpha=.4)
    ax.set(title="Figura 1. Evolución del sistema y segmentos estimados",
           ylabel="Llegadas por segundo")
    ax.legend()
    ventanas = df.copy()
    ventanas["ventana"] = (ventanas.t_llegada_s // 30).astype(int)
    ventanas["reintento"] = (ventanas.intentos > 1).astype(float)
    agregado = ventanas.groupby("ventana").agg(latencia=("latencia_ms", "mean"),
                                                 reintento=("reintento", "mean"))
    lat.plot(agregado.index * 30, agregado.latencia, label="Latencia media")
    retry.plot(agregado.index * 30, agregado.reintento * 100, label="Reintentos")
    lat.set_ylabel("Latencia (ms)")
    retry.set(xlabel="Tiempo desde el inicio (s)", ylabel="Reintentos (%)")
    for axis in (lat, retry):
        for boundary in (668, 838):
            axis.axvline(boundary, color="black", linestyle="--", alpha=.4)
        axis.legend()
    fig.tight_layout()
    fig.savefig(OUT / "figura_1_llegadas.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
