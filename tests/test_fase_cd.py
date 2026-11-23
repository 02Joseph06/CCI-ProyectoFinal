"""Comprobaciones de las identidades y procedimientos de la fase C/D."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import tiempos_cd
import esperanza_d2
import regresion_d3


class FaseCDTest(unittest.TestCase):
    def test_c1_varianza_empirica_y_masa_en_cero(self):
        df = pd.DataFrame({"cache_hit": [1, 1, 0, 0, 0, 0],
                           "gpu_ms": [0., 0., 1., 2., 4., 8.]})
        with tempfile.TemporaryDirectory() as path:
            with patch.object(tiempos_cd, "datos_estables", return_value=df), \
                 patch.object(tiempos_cd, "OUT", Path(path)), \
                 contextlib.redirect_stdout(io.StringIO()):
                result = tiempos_cd.c1()
        self.assertEqual(result["n_cache"], 2)
        self.assertAlmostEqual(result["p_cache"], 1/3)
        self.assertAlmostEqual(result["var_modelo_ddof0_ms2"], np.var(df.gpu_ms, ddof=0))
        self.assertAlmostEqual(result["var_muestral_ddof1_ms2"], np.var(df.gpu_ms, ddof=1))

    def test_d2_identidades_por_clases(self):
        df = pd.DataFrame({"clase": ["a", "a", "b", "b", "b"],
                           "gpu_ms": [0., 2., 1., 3., 5.]})
        result = esperanza_d2.descomponer(df)
        self.assertAlmostEqual(result["media_ms"], result["comprobacion_media_ms"])
        self.assertAlmostEqual(result["var_empirica_ddof0_ms2"], result["suma_componentes_ms2"])

    def test_lowess_reproduce_una_recta(self):
        x = np.linspace(1., 100., 100)
        y = 7. + 2.5*x
        grid = np.array([2., 15., 50., 85., 99.])
        predicted = esperanza_d2.lowess_local(x, y, grid, frac=.15)
        np.testing.assert_allclose(predicted, 7.+2.5*grid, rtol=1e-10, atol=1e-10)

    def test_d3_sistema_ponderado_y_hc3(self):
        size = np.array([1., 2., 3., 4., 5., 6.])
        y = np.array([2., 4.1, 5.8, 8.3, 9.7, 12.4])
        X = np.column_stack([np.ones(len(size)), size])
        weights = 1/size**2
        result = regresion_d3.regresion(X, y, weights)
        beta_independent = np.linalg.lstsq(np.sqrt(weights)[:, None]*X,
                                           np.sqrt(weights)*y, rcond=None)[0]
        np.testing.assert_allclose(result["beta"], beta_independent, rtol=1e-12)
        inv = np.linalg.inv(X.T @ (weights[:, None]*X))
        meat = sum((weights[i]*result["residuos"][i]/(1-result["leverage"][i]))**2 *
                   np.outer(X[i], X[i]) for i in range(len(y)))
        expected = np.sqrt(np.diag(inv@meat@inv))
        np.testing.assert_allclose(result["se_hc3"], expected, rtol=1e-12)

    def test_c4_remuestreo_sembrado_reproducible(self):
        df = pd.DataFrame({"cache_hit": [0] * 6, "gpu_ms": [1., 1.7, 2.8, 4.1, 7.3, 10.]})
        with tempfile.TemporaryDirectory() as path:
            with patch.object(tiempos_cd, "datos_estables", return_value=df), \
                 patch.object(tiempos_cd, "OUT", Path(path)), \
                 contextlib.redirect_stdout(io.StringIO()):
                first = tiempos_cd.c4(seed=12, replicas=1000, N=2)
                second = tiempos_cd.c4(seed=12, replicas=1000, N=2)
        self.assertEqual(first["prob_remuestreo_iid"], second["prob_remuestreo_iid"])
        self.assertEqual(first["N"], 2)

    def test_c3_conserva_referencia_y_valor_de_scipy_por_separado(self):
        df = pd.DataFrame({"red_ms": np.linspace(20., 40., 100)})
        with tempfile.TemporaryDirectory() as path:
            with patch.object(tiempos_cd, "datos_estables", return_value=df), \
                 patch.object(tiempos_cd, "OUT", Path(path)), \
                 contextlib.redirect_stdout(io.StringIO()):
                result = tiempos_cd.c3(seed=12, replicas=20)
        self.assertEqual(result["AD_referencia_10_indicada_por_estudiante"], .656)
        index = result["AD_significancias_pct"].index(10.0)
        self.assertEqual(result["AD_critico_10_scipy_instalado"], result["AD_valores_criticos"][index])


if __name__ == "__main__":
    unittest.main()
