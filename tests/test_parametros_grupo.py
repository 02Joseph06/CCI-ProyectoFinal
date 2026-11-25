"""Comprueba los parámetros derivados y su propagación entre módulos."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import parametros
import dependencias_d1
import esperanza_d2
import parte_e
import parte_f
import parte_g
import tiempos_cd


class ParametrosGrupoTest(unittest.TestCase):
    def test_formulas_del_enunciado(self):
        self.assertEqual(parametros.S, 2279892322)
        self.assertEqual((parametros.TAU_MS, parametros.T1_KB, parametros.T2_KB), (190, 100, 450))
        self.assertEqual((parametros.KMAX, parametros.R, parametros.N), (6, 4, 14))
        self.assertAlmostEqual(parametros.CONFIANZA, .95)
        self.assertAlmostEqual(parametros.EPSILON, .02)
        self.assertAlmostEqual(parametros.CRECIMIENTO, 1.5)
        self.assertAlmostEqual(parametros.PREVALENCIA, .008)

    def test_parametros_en_modulos(self):
        self.assertEqual((dependencias_d1.T1_KB, dependencias_d1.T2_KB), (100, 450))
        self.assertEqual((esperanza_d2.T1_KB, esperanza_d2.T2_KB), (100, 450))
        self.assertEqual(parte_e.KMAX, 6)
        self.assertEqual(parte_f.TAU, 190)
        self.assertEqual(parte_g.TAU_MS, 190)
        self.assertAlmostEqual(parte_g.EPSILON, .02)
        self.assertEqual(tiempos_cd.c4.__defaults__[-1], 14)


if __name__ == '__main__':
    unittest.main()
