"""D3: ecuaciones matriciales, residuos y errores clásicos y HC3."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from tiempos_cd import datos_estables
from parametros import CONFIANZA

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "D3"


def regresion(X, y, weights):
    n, p = X.shape
    normal = X.T @ (weights[:, None]*X)
    beta = np.linalg.solve(normal, X.T @ (weights*y))
    inverse = np.linalg.solve(normal, np.eye(p))
    residuals = y-X@beta
    leverage = weights*np.einsum("ij,jk,ik->i", X, inverse, X)
    if np.any(leverage >= 1):
        raise ValueError("HC3 no está definido para leverage >= 1")
    sigma2 = np.sum(weights*residuals**2)/(n-p)
    classic = inverse*sigma2
    factors = (weights*residuals/(1-leverage))**2
    meat = X.T@(X*factors[:, None])
    robust = inverse@meat@inverse
    return {"beta": beta, "residuos": residuals, "leverage": leverage,
            "se_clasico": np.sqrt(np.diag(classic)), "se_hc3": np.sqrt(np.diag(robust)),
            "condicion_matriz": float(np.linalg.cond(normal))}


def main():
    data = datos_estables()
    data = data[data.cache_hit == 0]
    if data[["tam_kb", "gpu_ms"]].isna().any().any() or (data.tam_kb <= 0).any():
        raise ValueError("WLS requiere tamaños positivos y valores finitos")
    size, gpu = data.tam_kb.to_numpy(), data.gpu_ms.to_numpy()
    X = np.column_stack([np.ones(len(size)), size])
    ols = regresion(X, gpu, np.ones(len(size)))
    wls = regresion(X, gpu, 1/size**2)
    squared = ols["residuos"]**2
    aux_beta = np.linalg.solve(X.T@X, X.T@squared)
    aux_pred = X@aux_beta
    r2 = 1-np.sum((squared-aux_pred)**2)/np.sum((squared-squared.mean())**2)
    lm = len(size)*r2
    degrees = len(size)-X.shape[1]
    critical = stats.t.ppf((1 + CONFIANZA) / 2, degrees)
    interval_rows = []
    for name, model in (("OLS", ols), ("WLS", wls)):
        for variance_method in ("clasico", "hc3"):
            for idx, coefficient in enumerate(("intercepto_ms", "pendiente_ms_por_kb")):
                estimate = model["beta"][idx]
                error = model[f"se_{variance_method}"][idx]
                interval_rows.append({"modelo": name, "coeficiente": coefficient,
                    "estimacion": estimate, "metodo_se": variance_method,
                    "error_estandar": error, "nivel": CONFIANZA,
                    "critico_t": critical, "gl": degrees,
                    "limite_inferior": estimate-critical*error,
                    "limite_superior": estimate+critical*error})
    result = {"n": len(size), "ols": {"beta": ols["beta"].tolist(),
              "se_clasico": ols["se_clasico"].tolist(), "se_hc3": ols["se_hc3"].tolist(),
              "max_leverage": float(ols["leverage"].max()), "condicion_matriz": ols["condicion_matriz"]},
              "wls": {"beta": wls["beta"].tolist(), "se_clasico": wls["se_clasico"].tolist(),
              "se_hc3": wls["se_hc3"].tolist(), "max_leverage": float(wls["leverage"].max()),
              "condicion_matriz": wls["condicion_matriz"]},
              "breusch_pagan_lm": float(lm), "bp_gl": 1,
              "bp_p_numerico": float(stats.chi2.sf(lm, 1)),
              "intervalos": {"nivel": CONFIANZA, "distribucion": "t de Student",
                             "grados_libertad": degrees, "valor_critico": float(critical)},
              "nota": "p numérico cero puede indicar subdesbordamiento; WLS asume la forma de pesos elegida."}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "resultados.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
    pd.DataFrame(interval_rows).to_csv(OUT / "intervalos_coeficientes.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].scatter(size, gpu, s=3, alpha=.12, label="Solicitudes sin caché")
    grid = np.linspace(size.min(), size.max(), 200)
    axes[0].plot(grid, ols["beta"][0]+ols["beta"][1]*grid, color="tab:red", label="OLS")
    axes[0].plot(grid, wls["beta"][0]+wls["beta"][1]*grid, color="tab:green", label="WLS")
    axes[0].set(xlabel="Tamaño de imagen (KB)", ylabel="Tiempo de GPU (ms)", title="Ajustes lineales")
    axes[0].legend()
    axes[1].scatter(size, ols["residuos"], s=3, alpha=.12, label="Residuos OLS")
    axes[1].axhline(0, color="black", linestyle="--")
    axes[1].set(xlabel="Tamaño de imagen (KB)", ylabel="Residuo de GPU (ms)", title="Residuos frente a tamaño")
    axes[1].legend()
    fig.tight_layout(); fig.savefig(OUT / "figura_5_regresion.png", dpi=160); plt.close(fig)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
