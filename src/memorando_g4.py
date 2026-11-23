"""Construye un memorando provisional a partir de las salidas rastreables.

No convierte hipótesis ni resultados pendientes en decisiones definitivas.
"""
import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "G4"


def main():
    b = json.loads((ROOT / "outputs/B/resultados.json").read_text(encoding="utf-8"))
    c = json.loads((ROOT / "outputs/C1/resultados.json").read_text(encoding="utf-8"))
    f2 = pd.read_csv(ROOT / "outputs/F2/ic_latencia_F2.csv")
    f3 = pd.read_csv(ROOT / "outputs/F3/comparacion_AB_F3.csv").set_index("metrica")
    f6 = pd.read_csv(ROOT / "outputs/F6/comparacion_validacion_F6.csv").set_index("parametro")
    e2 = pd.read_csv(ROOT / "outputs/E2/bayes_E2.csv").set_index("regla")
    e4 = pd.read_csv(ROOT / "outputs/E4/decision_guardia_E4.csv").set_index("regla")
    g1 = pd.read_csv(ROOT / "outputs/G1/validacion_simulador_G1.csv").set_index("metrica")
    g2 = pd.read_csv(ROOT / "outputs/G2/capacidad_proyeccion_G2.csv").set_index("gpus")
    gpu = f3.loc["GPU sin caché (ms)"]
    retry = f3.loc["reintento (>1)"]
    slo = f3.loc["violación SLO >210 ms"]
    base_tail = g1.loc["proporcion_mayor_210_ms"]
    block = f2[f2.metodo.str.contains("bloques móviles", regex=False)].iloc[0]
    incident = e4.loc["D1_y_D2"]
    vpp = e2.loc["D1_y_D2", "vpp_produccion"]
    v6 = f6.loc["p_fallo_intento"]
    robustness = ROOT / "outputs/G3/robustez_c_G3.csv"
    status = "Hay salida de robustez; debe revisarse su método." if robustness.exists() else (
        "La propagación G3 y la recomendación final están pendientes de las decisiones del grupo.")

    paragraphs = [
        ("MEMORANDO EJECUTIVO — BORRADOR PARA REVISIÓN", True),
        ("Para: Dirección Técnica (CTO), Andes Vision AI | De: Equipo SRE y Datos", False),
        ("Fecha: 22 de noviembre de 2026 | Asunto: confiabilidad, versiones y capacidad", False),
        ("ESTADO: cifras calculadas con hipótesis y discrepancias pendientes; no es una recomendación validada.", False),
        ("1. SERVICIO OBSERVADO", True),
        (f"En 1.030 s estables se retuvieron {format(b['B1']['n'], ',').replace(',', '.')} solicitudes: tasa {b['B1']['rate_s']:.3f}/s "
         f"(IC 90 % [{b['B1']['rate_interval'][0]:.3f}; {b['B1']['rate_interval'][1]:.3f}]) y caché {c['p_cache']:.2%}. "
         f"La latencia media es {block.estimacion_ms:.2f} ms; el bootstrap por bloques da "
         f"[{block.inferior_ms:.2f}; {block.superior_ms:.2f}] ms. La tasa se refiere a filas conservadas tras auditoría.", False),
        (f"La proporción observada de latencias superiores a 210 ms es {base_tail.observado:.2%}. "
         f"En F6, la estimación de fallos por intento cambia de {v6.base:.2%} a {v6.validacion:.2%}; "
         "la estabilidad de todas las distribuciones y la causa del cambio no están demostradas.", False),
        ("2. COMPARACIÓN B − A", True),
        (f"GPU sin caché: {gpu.diferencia_B_menos_A:+.3f} ms; IC conjunto 90 % "
         f"[{gpu.ic_bonferroni_inferior:.3f}; {gpu.ic_bonferroni_superior:.3f}] ms. "
         f"Reintentos: {100*retry.diferencia_B_menos_A:+.3f} puntos porcentuales; "
         f"violación del SLO: {100*slo.diferencia_B_menos_A:+.3f} puntos porcentuales. "
         "La decisión sobre la versión debe considerar los intervalos completos; no rechazar una diferencia no prueba equivalencia.", False),
        ("3. CAPACIDAD Y ALERTAS: RESULTADOS CONDICIONALES", True),
        (f"Con el tráfico multiplicado por 1,5, G2 estima violaciones de {g2.loc[2,'violacion']:.2%}, "
         f"{g2.loc[3,'violacion']:.2%} y {g2.loc[4,'violacion']:.2%} para 2, 3 y 4 GPU. "
         f"En G1 la cola simulada ({base_tail.simulado:.2%}) difiere de la observada ({base_tail.observado:.2%}); "
         "los intervalos de G2 miden error de simulación con parámetros fijos.", False),
        (f"Para D1 y D2, E estima {incident.media_falsas_diarias:.2f} falsas alarmas/día y "
         f"{vpp:.1%} de probabilidad de incidente por alerta en producción, bajo transportabilidad de tasas. "
         "La distribución diaria supone minutos independientes y tasa constante.", False),
        (status + " El significado de los reintentos en la tasa observada sigue sin comprobarse.", False),
    ]
    lines = ["# " + paragraphs[0][0], "", *[p for p, _ in paragraphs[1:]], "",
             "Fuentes: salidas reproducibles B, C1, E2, E4, F2, F3, F6 y G1–G2; ver `documentos/calculos/discrepancias_pendientes.md`. ",
             "Las cifras propuestas por el grupo están conservadas en `documentos/G4/memorando_aportado_por_el_grupo.md`."]
    OUT.mkdir(parents=True, exist_ok=True)
    md = "\n\n".join(lines) + "\n"
    (OUT / "memorando_ejecutivo_G4.md").write_text(md, encoding="utf-8")
    local = ROOT / "documentos/G4"
    local.mkdir(parents=True, exist_ok=True)
    (local / "memorando_ejecutivo_G4.md").write_text(md, encoding="utf-8")
    (local / "registro.md").write_text(
        "# G4 — Memorando ejecutivo\n\n"
        "El memorando es un borrador generado de salidas calculadas, no una recomendación final. "
        "Incluye diferencias de validación G1, supuestos de E4 y bloqueos de G3. "
        "El texto previo del grupo se conserva por separado. Fórmulas y discrepancias: "
        "`../calculos/discrepancias_pendientes.md`. Salidas MD/PDF: `../../outputs/G4/`.\n",
        encoding="utf-8")
    # Una sola página; cada párrafo incluye sus unidades y procedencia general.
    fig = plt.figure(figsize=(8.27, 11.69))
    y = .965
    for paragraph, heading in paragraphs:
        chunks = textwrap.wrap(paragraph, width=92 if not heading else 76,
                               break_long_words=False, break_on_hyphens=False) or [""]
        font_size = 10 if heading else 8.6
        for line in chunks:
            fig.text(.07, y, line, fontsize=font_size, weight="bold" if heading else "normal", va="top")
            y -= .0155
        y -= .006 if heading else .012
    if y < .04:
        raise RuntimeError("El memorando no cabe en una página")
    fig.savefig(OUT / "memorando_ejecutivo_G4.pdf", format="pdf")
    plt.close(fig)
    print("Memorando G4 provisional generado en Markdown y PDF de una página")
    return {"estado": "borrador pendiente de decisiones", "pdf": str(OUT / "memorando_ejecutivo_G4.pdf")}


if __name__ == "__main__":
    main()
