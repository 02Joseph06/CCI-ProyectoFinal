"""Resumen parcial A3: las medidas basadas en varianza están pendientes."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = pd.read_csv(ROOT / "outputs" / "A1" / "solicitudes_auditadas.csv")
    data["regimen"] = np.select(
        [data.t_llegada_s < 670, data.t_llegada_s < 840, data.t_llegada_s <= 1200],
        ["estable_inicial", "carga_alta", "posterior"], default="sin_regimen")
    rows = []
    for (regimen, version), group in data.groupby(["regimen", "version"]):
        for variable in ("latencia_ms", "gpu_ms", "red_ms", "tam_kb"):
            x = group[variable].dropna()
            rows.append(dict(regimen=regimen, version=version, variable=variable,
                             n=len(x), media=x.mean(), mediana=x.median(),
                             minimo=x.min(), maximo=x.max(), rango=x.max()-x.min(),
                             q1=x.quantile(.25), q3=x.quantile(.75),
                             rango_intercuartil=x.quantile(.75)-x.quantile(.25)))
    out = ROOT / "outputs" / "A3"
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "resumen_parcial.csv", index=False)
    print(f"Resumen parcial A3: {len(rows)} combinaciones; faltan varianza, asimetría y curtosis")


if __name__ == "__main__":
    main()
