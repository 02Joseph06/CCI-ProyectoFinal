"""Verifica que el memorando provisional no oculte una G3 pendiente."""
import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import memorando_g4


class MemorandoTest(unittest.TestCase):
    def test_borrador_sin_robustez_y_pdf_de_una_pagina(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def table(part, name, rows):
                folder = root / "outputs" / part
                folder.mkdir(parents=True, exist_ok=True)
                pd.DataFrame(rows).to_csv(folder / name, index=False)
            for part, payload in (("B", {"B1":{"n": 24956, "rate_s": 24., "rate_interval": [23., 25.]}}),
                                  ("C1", {"p_cache": .41})):
                folder = root / "outputs" / part
                folder.mkdir(parents=True, exist_ok=True)
                (folder / "resultados.json").write_text(json.dumps(payload), encoding="utf8")
            table("F2", "ic_latencia_F2.csv", [{"metodo":"bloques móviles", "estimacion_ms":65., "inferior_ms":64., "superior_ms":66.}])
            table("F3", "comparacion_AB_F3.csv", [
                {"metrica":name, "diferencia_B_menos_A":.01, "ic_bonferroni_inferior":-.1, "ic_bonferroni_superior":.1}
                for name in ("GPU sin caché (ms)", "reintento (>1)", "violación SLO >210 ms")])
            table("F6", "comparacion_validacion_F6.csv", [{"parametro":"p_fallo_intento", "base":.15, "validacion":.2}])
            table("E2", "bayes_E2.csv", [{"regla":"D1_y_D2", "vpp_produccion":.7}])
            table("E4", "decision_guardia_E4.csv", [{"regla":"D1_y_D2", "media_falsas_diarias":2.4}])
            table("G1", "validacion_simulador_G1.csv", [{"metrica":"proporcion_mayor_210_ms", "observado":.011, "simulado":.014}])
            table("G2", "capacidad_proyeccion_G2.csv", [{"gpus":c, "violacion":p} for c,p in ((2,.03),(3,.01),(4,.009))])
            with patch.object(memorando_g4, "ROOT", root), \
                 patch.object(memorando_g4, "OUT", root / "outputs/G4"), \
                 contextlib.redirect_stdout(io.StringIO()):
                memorando_g4.main()
            text=(root / "outputs/G4/memorando_ejecutivo_G4.md").read_text(encoding="utf8")
            pdf=(root / "outputs/G4/memorando_ejecutivo_G4.pdf").read_bytes()
            self.assertIn("BORRADOR", text)
            self.assertIn("La propagación G3 y la recomendación final están pendientes", text)
            self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", pdf)), 1)


if __name__ == "__main__":
    unittest.main()
