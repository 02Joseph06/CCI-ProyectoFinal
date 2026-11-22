"""Segmentación cuantitativa de las llegadas por tasas de Poisson por tramos."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
    for ancho in (5, 10, 20, 30):
        segments, bics = segmentar(tiempos, ancho)
        print(f"ancho={ancho}s segmentos={segments} BIC={np.round(bics, 1)}")
        for start, end, n in segments:
            records.append(dict(ancho_s=ancho, inicio_s=start, fin_s=end,
                                solicitudes=n, tasa_s=n / (end - start)))
    pd.DataFrame(records).to_csv(OUT / "sensibilidad_segmentacion.csv", index=False)
    main_segments, _ = segmentar(tiempos, 10)
    counts, edges = np.histogram(tiempos, bins=np.arange(0, 1210, 10))
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.step(edges[:-1], counts / 10, where="post", label="Tasa por intervalos de 10 s")
    for start, end, n in main_segments:
        ax.hlines(n / (end-start), start, end, colors="tab:red", linewidth=2)
        ax.axvline(start, color="black", linestyle="--", alpha=.4)
    ax.set(title="Figura 1. Evolución de la tasa de llegadas y segmentos estimados",
           xlabel="Tiempo desde el inicio (s)", ylabel="Llegadas por segundo")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "figura_1_llegadas.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
