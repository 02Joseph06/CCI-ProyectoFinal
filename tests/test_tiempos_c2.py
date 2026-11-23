"""Comprobaciones analíticas independientes para las optimizaciones de C2."""
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy.special import digamma

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tiempos_c2 import estimar_gamma, estimar_lognormal


class AjustesTest(unittest.TestCase):
    def test_lognormal_coincide_con_maximo_analitico(self):
        x = np.array([1.0, 1.7, 2.8, 4.1, 7.3, 10.0])
        result = estimar_lognormal(x)
        self.assertTrue(result["convergencia"])
        self.assertAlmostEqual(result["mu_log_ms"], np.log(x).mean(), places=8)
        self.assertAlmostEqual(result["sigma_log"], np.log(x).std(ddof=0), places=8)

    def test_gamma_satisface_ecuacion_de_verosimilitud(self):
        x = np.array([1.0, 1.7, 2.8, 4.1, 7.3, 10.0])
        result = estimar_gamma(x)
        self.assertTrue(result["convergencia"])
        k, theta = result["k"], result["theta_ms"]
        self.assertAlmostEqual(k * theta, x.mean(), places=6)
        self.assertAlmostEqual(np.log(k) - digamma(k), np.log(x.mean()) - np.log(x).mean(), places=6)

    def test_rechaza_valores_no_positivos(self):
        for function in (estimar_gamma, estimar_lognormal):
            with self.assertRaises(ValueError):
                function([0, 1, 2])


if __name__ == "__main__":
    unittest.main()
