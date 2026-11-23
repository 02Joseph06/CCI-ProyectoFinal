"""D4: covarianza muestral y correlación de Pearson en solicitudes no cacheadas."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "D4"


def main():
    df = pd.read_csv(ROOT / "outputs" / "A1" / "solicitudes_auditadas.csv")
    stable = ((df.t_llegada_s >= 0) & (df.t_llegada_s < 668)) | (
        (df.t_llegada_s >= 838) & (df.t_llegada_s <= 1200))
    selected = df.loc[stable & (df.cache_hit == 0), ["tam_kb", "gpu_ms"]]
    if selected.isna().any().any():
        raise ValueError("Hay valores faltantes: se requiere una decisión de tratamiento")
    size, gpu = selected.tam_kb.to_numpy(), selected.gpu_ms.to_numpy()
    correlation = stats.pearsonr(size, gpu)
    result = {"n": len(selected),
              "covarianza_muestral_kb_ms": float(np.cov(size, gpu, ddof=1)[0, 1]),
              "pearson_r": float(correlation.statistic),
              "pearson_p_numerico": float(correlation.pvalue),
              "nota_p": "Si p se imprime como 0, se trata de subdesbordamiento numérico, no probabilidad exactamente nula.",
              "r_cuadrado": float(correlation.statistic**2)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "correlacion.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(8, 5))
    dots = ax.hexbin(size, gpu, gridsize=45, mincnt=1, cmap="viridis", bins="log")
    colorbar = fig.colorbar(dots, ax=ax)
    colorbar.set_label("Solicitudes por celda (escala logarítmica)")
    ax.set(title="D4. Tamaño de imagen y tiempo de GPU sin caché",
           xlabel="Tamaño de imagen (KB)", ylabel="Tiempo de GPU (ms)")
    fig.tight_layout()
    fig.savefig(OUT / "tamano_gpu.png", dpi=160)
    plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
