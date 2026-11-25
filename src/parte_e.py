"""Parte E: monitoreo; las frecuencias provienen del CSV de pruebas.

Las decisiones de inferencia y la recomendación final requieren revisión del grupo.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
try:
    from .parametros import S as SEED, CONFIANZA as CONFIDENCE, PREVALENCIA as PREVALENCE, KMAX
except ImportError:
    from parametros import S as SEED, CONFIANZA as CONFIDENCE, PREVALENCIA as PREVALENCE, KMAX

ROOT = Path(__file__).resolve().parents[1]
RULES = ("D1", "D2", "D1_y_D2", "D1_o_D2")


def wilson(successes, total, confidence=CONFIDENCE):
    """Intervalo de Wilson bilateral para una proporción binomial."""
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Conteos binomiales inválidos")
    z = stats.norm.ppf((1 + confidence) / 2)
    p = successes / total
    denominator = 1 + z*z/total
    center = (p + z*z/(2*total)) / denominator
    radius = z*np.sqrt(p*(1-p)/total + z*z/(4*total*total))/denominator
    return (0. if successes == 0 else max(0., center-radius),
            1. if successes == total else min(1., center+radius))


def ppv(tpr, fpr, prevalence):
    numerator = prevalence*tpr
    denominator = numerator + (1-prevalence)*fpr
    return numerator / denominator if denominator else np.nan


def analyze(df, seed=SEED, output_root=None, simulations=200_000):
    required = {"minuto", "D1", "D2", "incidente"}
    if not required.issubset(df.columns) or df[list(required)].isna().any().any():
        raise ValueError("Faltan columnas o hay valores nulos en monitoreo")
    if any(not df[c].isin([0, 1]).all() for c in ("D1", "D2", "incidente")):
        raise ValueError("Las alertas y el estado deben ser binarios")
    if df.minuto.duplicated().any():
        raise ValueError("El minuto de monitoreo debe ser único")
    df = df.copy()
    df["D1_y_D2"] = df.D1 & df.D2
    df["D1_o_D2"] = df.D1 | df.D2
    incident = df.incidente == 1
    positive = int(incident.sum())
    negative = int((~incident).sum())
    if not positive or not negative:
        raise ValueError("Se requieren minutos con y sin incidente")
    test_prevalence = positive/len(df)
    rng = np.random.default_rng(seed)
    e1, e2, e4 = [], [], []
    for rule in RULES:
        hits = int(df.loc[incident, rule].sum())
        false = int(df.loc[~incident, rule].sum())
        tpr, fpr = hits/positive, false/negative
        tlo, thi = wilson(hits, positive)
        flo, fhi = wilson(false, negative)
        e1.append(dict(regla=rule, incidentes=positive, verdaderos_positivos=hits,
                       sin_incidente=negative, falsos_positivos=false, sensibilidad=tpr,
                       sensibilidad_ic_inf=tlo, sensibilidad_ic_sup=thi,
                       fpr=fpr, fpr_ic_inf=flo, fpr_ic_sup=fhi, metodo_ic=f"Wilson {CONFIDENCE:.0%}"))
        e2.append(dict(regla=rule, prevalencia_pruebas_observada=test_prevalence,
                       prevalencia_produccion=PREVALENCE, vpp_produccion=ppv(tpr, fpr, PREVALENCE),
                       vpp_pruebas=ppv(tpr, fpr, test_prevalence),
                       vpp_directo=float(df.loc[df[rule] == 1, "incidente"].mean())))
        prob = (1-PREVALENCE)*fpr
        lower_prob = (1-PREVALENCE)*flo
        upper_prob = (1-PREVALENCE)*fhi
        samples = rng.binomial(1440, prob, size=simulations)
        mc_hits = int(np.count_nonzero(samples <= KMAX))
        mc_lo, mc_hi = wilson(mc_hits, simulations)
        e4.append(dict(regla=rule, minutos=1440, kmax=KMAX, fpr=fpr,
                       prob_falsa_alarma_minuto=prob, media_falsas_diarias=1440*prob,
                       prob_hasta_k=stats.binom.cdf(KMAX, 1440, prob),
                       prob_hasta_k_con_fpr_ic_sup=stats.binom.cdf(KMAX, 1440, upper_prob),
                       prob_hasta_k_con_fpr_ic_inf=stats.binom.cdf(KMAX, 1440, lower_prob),
                       mc_replicas=simulations, mc_prob_hasta_k=mc_hits/simulations,
                       mc_ic_inf=mc_lo, mc_ic_sup=mc_hi,
                       condicion="Binomial: minutos independientes y tasa constante"))
    # E3: las combinaciones se evalúan con las probabilidades conjuntas observadas
    # y, como comparación, el resultado hipotético de independencia condicional.
    e3 = []
    for state in (0, 1):
        group = df[df.incidente == state]
        table = pd.crosstab(group.D1, group.D2).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
        chi, pvalue, dof, expected = stats.chi2_contingency(table, correction=False)
        p1, p2 = group.D1.mean(), group.D2.mean()
        for rule, joint, product in [("D1_y_D2", group.D1_y_D2.mean(), p1*p2),
                                     ("D1_o_D2", group.D1_o_D2.mean(), p1+p2-p1*p2)]:
            e3.append(dict(incidente=state, n=len(group), regla=rule,
                           p_observada=joint, p_bajo_independencia=product,
                           diferencia=joint-product, chi2=chi, gl=dof, p_valor_chi2=pvalue,
                           esperado_minimo=expected.min(),
                           chi2_aproximacion_frecuencias_adecuadas=bool((expected >= 5).all())))
    e1, e2, e3, e4 = map(pd.DataFrame, (e1, e2, e3, e4))
    for rule in ("D1_y_D2", "D1_o_D2"):
        rows = e3[e3.regla == rule].set_index("incidente")
        independent_ppv = ppv(rows.loc[1, "p_bajo_independencia"],
                              rows.loc[0, "p_bajo_independencia"], PREVALENCE)
        e2.loc[e2.regla == rule, "vpp_independencia_hipotetica"] = independent_ppv
        e2.loc[e2.regla == rule, "diferencia_vpp_independencia_menos_observado"] = (
            independent_ppv - e2.loc[e2.regla == rule, "vpp_produccion"])
    if output_root is not None:
        output_root = Path(output_root)
        for part, frame, name in [("E1", e1, "metricas_E1.csv"), ("E2", e2, "bayes_E2.csv"),
                                  ("E3", e3, "independencia_condicional_E3.csv"),
                                  ("E4", e4, "decision_guardia_E4.csv")]:
            folder = output_root / part
            folder.mkdir(parents=True, exist_ok=True)
            frame.to_csv(folder/name, index=False)
        fig, ax = plt.subplots(figsize=(9, 4.8))
        x = np.arange(0, 31)
        for _, row in e4.iterrows():
            ax.plot(x, stats.binom.pmf(x, 1440, row.prob_falsa_alarma_minuto), label=row.regla)
        ax.axvline(KMAX, color="black", linestyle="--", label=f"Límite: {KMAX} falsas alarmas")
        ax.set(xlabel="Falsas alarmas en un día (número)", ylabel="Probabilidad",
               title="Figura 6. Falsas alarmas diarias bajo independencia temporal")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_root/"E4"/"figura_6_alertas.png", dpi=180)
        plt.close(fig)
    return {"E1": e1, "E2": e2, "E3": e3, "E4": e4}


if __name__ == "__main__":
    results = analyze(pd.read_csv(ROOT/"data"/"raw"/"monitoreo.csv"), output_root=ROOT/"outputs")
    for part, frame in results.items():
        print(f"\n{part}\n{frame.to_string(index=False)}")
