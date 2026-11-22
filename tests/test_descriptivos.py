"""Comprueba la unión de tramos y la convención muestral confirmadas para A3."""
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import descriptivos


class DescriptivosTest(unittest.TestCase):
    def test_union_estable_y_varianza_muestral(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "outputs" / "A1"
            folder.mkdir(parents=True)
            data = pd.DataFrame({
                "t_llegada_s": [1, 2, 900, 700], "version": ["A"] * 4,
                "latencia_ms": [1., 2., 4., 99.], "gpu_ms": [1., 2., 4., 99.],
                "red_ms": [1., 2., 4., 99.], "tam_kb": [1., 2., 4., 99.],
            })
            data.to_csv(folder / "solicitudes_auditadas.csv", index=False)
            old_root = descriptivos.ROOT
            try:
                descriptivos.ROOT = root
                descriptivos.main()
            finally:
                descriptivos.ROOT = old_root
            result = pd.read_csv(root / "outputs" / "A3" / "resumen_descriptivo.csv")
            stable = result[(result.regimen == "estable") & (result.variable == "latencia_ms")].iloc[0]
            self.assertEqual(stable["n"], 3)
            self.assertAlmostEqual(stable["media"], 7/3)
            self.assertAlmostEqual(stable["varianza_muestral"], 7/3)
            self.assertAlmostEqual(stable["asimetria_corregida"], pd.Series([1., 2., 4.]).skew())


if __name__ == "__main__":
    unittest.main()
