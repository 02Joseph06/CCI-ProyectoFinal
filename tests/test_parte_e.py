import unittest

import numpy as np
import pandas as pd
from scipy import stats

from src.parte_e import analyze, ppv, wilson


class TestParteE(unittest.TestCase):
    def test_wilson_sensible_en_los_extremos(self):
        lo, hi = wilson(0, 100)
        self.assertEqual(lo, 0)
        self.assertTrue(0 < hi < 0.1)
        self.assertTrue(np.isclose(wilson(100, 100)[1], 1))

    def test_conteos_y_bayes_en_tabla_conocida(self):
        df = pd.DataFrame({"minuto": range(8), "incidente": [1]*4+[0]*4,
                           "D1": [1, 1, 0, 0, 1, 0, 0, 0],
                           "D2": [1, 0, 1, 0, 1, 1, 0, 0]})
        result = analyze(df, seed=42, simulations=500)
        a = result["E1"].set_index("regla").loc["D1_y_D2"]
        self.assertEqual((a.verdaderos_positivos, a.falsos_positivos), (1, 1))
        b = result["E2"].set_index("regla").loc["D1_y_D2"]
        self.assertTrue(np.isclose(b.vpp_pruebas, b.vpp_directo))
        self.assertTrue(np.isclose(b.vpp_produccion, ppv(.25, .25, .007)))
        self.assertTrue(np.isclose(b.vpp_produccion, .007))
        daily = result["E4"].set_index("regla").loc["D1_y_D2"]
        self.assertTrue(np.isclose(daily.prob_hasta_k, stats.binom.cdf(8, 1440, .993*.25)))
        self.assertLessEqual(daily.prob_hasta_k_con_fpr_ic_sup, daily.prob_hasta_k)

    def test_rechaza_entradas_invalidas(self):
        df = pd.DataFrame({"minuto": [1, 2], "incidente": [0, 1], "D1": [0, 2], "D2": [0, 1]})
        with self.assertRaises(ValueError):
            analyze(df, simulations=10)


if __name__ == "__main__":
    unittest.main()
