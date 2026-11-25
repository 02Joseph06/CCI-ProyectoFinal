"""D2: esperanza y varianza por clases; estimación por 25 grupos de cuantiles."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tiempos_cd import datos_estables
from parametros import T1_KB, T2_KB

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "D2"


def descomponer(data):
    group = data.groupby("clase", observed=True).gpu_ms
    n = group.size()
    weights = n/len(data)
    means = group.mean()
    variances = group.var(ddof=0)
    mean = data.gpu_ms.mean()
    within = float((weights*variances).sum())
    between = float((weights*(means-mean)**2).sum())
    total = float(data.gpu_ms.var(ddof=0))
    return {"n": len(data), "media_ms": float(mean), "var_empirica_ddof0_ms2": total,
            "var_muestral_ddof1_ms2": float(data.gpu_ms.var(ddof=1)),
            "esperanza_var_condicional_ms2": within, "var_esperanza_condicional_ms2": between,
            "suma_componentes_ms2": within+between, "fraccion_explicada": between/total,
            "comprobacion_media_ms": float((weights*means).sum())}


def cuantiles(data, q=25):
    bins = pd.qcut(data.tam_kb, q=q, duplicates="drop")
    return data.assign(grupo_cuantil=bins).groupby("grupo_cuantil", observed=True).agg(
        n=("gpu_ms", "size"), tam_min_kb=("tam_kb", "min"), tam_max_kb=("tam_kb", "max"),
        tam_medio_kb=("tam_kb", "mean"), gpu_media_ms=("gpu_ms", "mean"),
        gpu_var_empirica_ms2=("gpu_ms", lambda s: s.var(ddof=0))).reset_index(drop=True)


def lowess_local(x, y, grid, frac=0.15):
    """Ajuste lineal local tricúbico, sin iteraciones robustas adicionales."""
    x, y, grid = np.asarray(x, dtype=float), np.asarray(y, dtype=float), np.asarray(grid, dtype=float)
    if x.ndim != 1 or y.shape != x.shape or len(x) < 3 or not 0 < frac <= 1:
        raise ValueError("LOWESS requiere vectores compatibles y 0 < frac <= 1")
    neighbors = max(3, int(np.ceil(frac * len(x))))
    predicted = []
    for point in grid:
        delta = x-point
        distance = np.abs(delta)
        bandwidth = np.partition(distance, neighbors-1)[neighbors-1]
        if bandwidth <= 0:
            raise ValueError("Ancho de banda nulo por empates en el tamaño")
        weights = np.maximum(0., 1-(distance/bandwidth)**3)**3
        s0, s1, s2 = weights.sum(), np.sum(weights*delta), np.sum(weights*delta**2)
        t0, t1 = np.sum(weights*y), np.sum(weights*delta*y)
        det = s0*s2-s1*s1
        if det <= np.finfo(float).eps * max(1., abs(s0*s2)):
            raise ValueError("Regresión local singular")
        predicted.append((s2*t0-s1*t1)/det)
    return np.asarray(predicted)


def main():
    data = datos_estables()
    if data[["tam_kb", "gpu_ms", "cache_hit"]].isna().any().any():
        raise ValueError("Faltan variables necesarias para D2")
    data["clase"] = pd.cut(data.tam_kb, [-np.inf, T1_KB, T2_KB, np.inf],
                           labels=["pequeña", "mediana", "grande"], right=False)
    nocache = data[data.cache_hit == 0].copy()
    all_result, positive_result = descomponer(data), descomponer(nocache)
    for r in (all_result, positive_result):
        if not np.isclose(r["var_empirica_ddof0_ms2"], r["suma_componentes_ms2"], atol=1e-8):
            raise AssertionError("La ley de varianza total no se verificó")
        if not np.isclose(r["media_ms"], r["comprobacion_media_ms"], atol=1e-10):
            raise AssertionError("La ley de esperanza total no se verificó")
    conditional = nocache.groupby("clase", observed=True).gpu_ms.agg(["size", "mean"])
    quantiles = cuantiles(data)
    frac = .15
    grid = np.linspace(data.tam_kb.min(), data.tam_kb.quantile(.995), 120)
    smooth_all = lowess_local(data.tam_kb, data.gpu_ms, grid, frac=frac)
    smooth_nocache = lowess_local(nocache.tam_kb, nocache.gpu_ms, grid, frac=frac)
    result = {"todas": all_result, "sin_cache": positive_result,
              "metodo_continuo": "25 grupos por cuantiles y LOWESS lineal local tricúbico",
              "cuantiles_solicitados": 25, "cuantiles_obtenidos": len(quantiles),
              "lowess_frac": frac, "lowess_iteraciones_robustas": 0,
              "lowess_puntos": len(grid), "limite_superior_grafica_kb": float(grid[-1]),
              "nota": "Se representa hasta el percentil 99,5 % del tamaño; el suavizado no prueba ausencia de sesgo."}
    OUT.mkdir(parents=True, exist_ok=True)
    conditional.to_csv(OUT / "medias_clase_sin_cache.csv")
    quantiles.to_csv(OUT / "grupos_cuantiles.csv", index=False)
    pd.DataFrame({"tam_kb": grid, "lowess_todas_ms": smooth_all,
                  "lowess_sin_cache_ms": smooth_nocache}).to_csv(OUT / "lowess.csv", index=False)
    (OUT / "resultados.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(quantiles.tam_medio_kb, quantiles.gpu_media_ms, "o", label="Media en 25 grupos: todas")
    ax.plot(grid, smooth_all, label="LOWESS: todas, frac=0,15")
    ax.plot(grid, smooth_nocache, label="LOWESS: sin caché, frac=0,15")
    ax.set(xlabel="Tamaño medio de imagen (KB)", ylabel="Tiempo medio de GPU (ms)",
           title="D2. Esperanza condicional de GPU por tamaño")
    ax.set_xlim(0, grid[-1])
    ax.legend(); fig.tight_layout(); fig.savefig(OUT / "esperanza_cuantiles.png", dpi=160); plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
