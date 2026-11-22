"""Comprueba que el incidente no genera un intervalo artificial en B1."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import llegadas_intentos


class IntervalosEstablesTest(unittest.TestCase):
    def test_no_contar_salto_entre_tramos(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "outputs" / "A1"
            folder.mkdir(parents=True)
            times = np.r_[np.linspace(0.1, 667.9, 1000),
                          np.linspace(668.1, 837.9, 300),
                          np.linspace(838.1, 1199.9, 500)]
            attempts = np.resize(np.array([1, 1, 1, 2, 3]), len(times))
            pd.DataFrame({"t_llegada_s": times, "intentos": attempts,
                          "exito": np.ones(len(times), dtype=int)}).to_csv(
                folder / "solicitudes_auditadas.csv", index=False)
            old_root, old_out = llegadas_intentos.ROOT, llegadas_intentos.OUT
            try:
                llegadas_intentos.ROOT = root
                llegadas_intentos.OUT = root / "outputs" / "B"
                with contextlib.redirect_stdout(io.StringIO()):
                    llegadas_intentos.main(42)  # Semilla exclusiva de la prueba sintética.
                result = json.loads((llegadas_intentos.OUT / "resultados.json").read_text(encoding="utf-8"))
            finally:
                llegadas_intentos.ROOT, llegadas_intentos.OUT = old_root, old_out
            b1 = result["B1"]
            self.assertEqual(b1["n"], 1500)
            self.assertEqual(b1["duration_s"], 1030)
            self.assertEqual(b1["numero_gaps"], 1498)
            self.assertLess(b1["max_gap_s"], 2)
            self.assertEqual(b1["ventanas_completas"], 102)


if __name__ == "__main__":
    unittest.main()
