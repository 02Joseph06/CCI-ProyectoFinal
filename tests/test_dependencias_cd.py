"""Verifica límites de clases, probabilidades y covarianza en C/D."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import dependencias_d1
import dependencias_d4


class DependenciasTest(unittest.TestCase):
    def test_d1_limites_y_probabilidades(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "outputs" / "A1"
            folder.mkdir(parents=True)
            pd.DataFrame({"t_llegada_s": [1, 2, 3, 4, 900, 901],
                          "tam_kb": [99.99, 99.99, 100, 100, 450, 450],
                          "cache_hit": [0, 1, 0, 1, 0, 1]}).to_csv(
                folder / "solicitudes_auditadas.csv", index=False)
            old_root, old_out = dependencias_d1.ROOT, dependencias_d1.OUT
            try:
                dependencias_d1.ROOT, dependencias_d1.OUT = root, root / "outputs" / "D1"
                with contextlib.redirect_stdout(io.StringIO()):
                    dependencias_d1.main()
                counts = pd.read_csv(dependencias_d1.OUT / "conteos.csv", index_col=0)
                joint = pd.read_csv(dependencias_d1.OUT / "conjunta.csv", index_col=0)
                conditional = pd.read_csv(dependencias_d1.OUT / "cache_dada_clase.csv", index_col=0)
            finally:
                dependencias_d1.ROOT, dependencias_d1.OUT = old_root, old_out
            self.assertTrue((counts.to_numpy() == 1).all())
            self.assertAlmostEqual(joint.to_numpy().sum(), 1)
            for total in conditional.sum(axis=1):
                self.assertAlmostEqual(total, 1)

    def test_d4_covarianza_muestral_y_filtro_estable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "outputs" / "A1"
            folder.mkdir(parents=True)
            pd.DataFrame({"t_llegada_s": [1, 2, 900, 700],
                          "tam_kb": [1, 2, 4, 500], "gpu_ms": [2, 4, 8, 1],
                          "cache_hit": [0, 0, 0, 0]}).to_csv(
                folder / "solicitudes_auditadas.csv", index=False)
            old_root, old_out = dependencias_d4.ROOT, dependencias_d4.OUT
            try:
                dependencias_d4.ROOT, dependencias_d4.OUT = root, root / "outputs" / "D4"
                with contextlib.redirect_stdout(io.StringIO()):
                    result = dependencias_d4.main()
            finally:
                dependencias_d4.ROOT, dependencias_d4.OUT = old_root, old_out
            self.assertEqual(result["n"], 3)
            self.assertAlmostEqual(result["covarianza_muestral_kb_ms"], 14/3)
            self.assertAlmostEqual(result["pearson_r"], 1)


if __name__ == "__main__":
    unittest.main()
