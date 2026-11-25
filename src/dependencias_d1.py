"""D1: tabla empírica, marginales, condicionales y contraste solicitado."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from parametros import CONFIANZA, T1_KB, T2_KB

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "D1"


def main():
    df = pd.read_csv(ROOT / "outputs" / "A1" / "solicitudes_auditadas.csv")
    stable = ((df.t_llegada_s >= 0) & (df.t_llegada_s < 668)) | (
        (df.t_llegada_s >= 838) & (df.t_llegada_s <= 1200))
    data = df.loc[stable, ["tam_kb", "cache_hit"]].copy()
    if data.isna().any().any() or not data.cache_hit.isin([0, 1]).all():
        raise ValueError("Valores faltantes o categorías de caché inválidas; se requiere decisión del grupo")
    data["clase"] = pd.cut(data.tam_kb, bins=[-np.inf, T1_KB, T2_KB, np.inf],
                           labels=["pequeña", "mediana", "grande"], right=False)
    counts = pd.crosstab(data.clase, data.cache_hit).reindex(
        index=["pequeña", "mediana", "grande"], columns=[0, 1], fill_value=0)
    if (counts.sum(axis=1) == 0).any() or (counts.sum(axis=0) == 0).any():
        raise ValueError("Categoría vacía; no se pueden calcular todas las condicionales")
    joint = counts / counts.to_numpy().sum()
    given_class = counts.div(counts.sum(axis=1), axis=0)
    given_cache = counts.div(counts.sum(axis=0), axis=1)
    result = stats.chi2_contingency(counts, correction=False)
    n_class = counts.sum(axis=1)
    p_cache = counts[1] / n_class
    z = stats.norm.ppf((1 + CONFIANZA) / 2)
    margin = z * np.sqrt(p_cache * (1-p_cache) / n_class)
    intervals = pd.DataFrame({"n": n_class, "cache_1": counts[1], "proporcion": p_cache,
                              "inferior_wald": p_cache-margin,
                              "superior_wald": p_cache+margin,
                              "nivel_confianza": CONFIANZA})
    OUT.mkdir(parents=True, exist_ok=True)
    counts.to_csv(OUT / "conteos.csv")
    joint.to_csv(OUT / "conjunta.csv")
    given_class.to_csv(OUT / "cache_dada_clase.csv")
    given_cache.to_csv(OUT / "clase_dado_cache.csv")
    intervals.to_csv(OUT / "intervalos_cache_dada_clase.csv")
    summary = {"n": int(len(data)), "marginal_clase": joint.sum(axis=1).to_dict(),
               "marginal_cache": {str(k): float(v) for k, v in joint.sum(axis=0).items()},
               "chi_cuadrado": float(result.statistic), "grados_libertad": int(result.dof),
               "p_valor": float(result.pvalue),
               "frecuencia_esperada_minima": float(result.expected_freq.min()),
               "intervalos": f"Wald normal al {CONFIANZA:.0%}."}
    (OUT / "resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    heat = ax.imshow(joint.to_numpy(), cmap="YlOrBr", aspect="auto")
    for i in range(len(joint.index)):
        for j in range(len(joint.columns)):
            color = "white" if joint.iloc[i, j] > joint.to_numpy().max() * .6 else "black"
            ax.text(j, i, f"{joint.iloc[i, j]:.2%}\n(n={counts.iloc[i, j]})",
                    ha="center", va="center", color=color)
    ax.set(xticks=[0, 1], xticklabels=["No (0)", "Sí (1)"],
           yticks=np.arange(len(joint.index)), yticklabels=joint.index,
           xlabel="Respuesta desde caché", ylabel="Clase de tamaño (KB)",
           title="Figura 4. Distribución conjunta de tamaño y caché")
    fig.colorbar(heat, ax=ax, label="Probabilidad conjunta")
    fig.tight_layout()
    fig.savefig(OUT / "figura_4_conjunta.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
