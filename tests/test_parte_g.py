import numpy as np
import unittest

from src.parte_g import simular_fifo, mmc_espera


class RngControlado:
    def poisson(self, _):
        return 3

    def uniform(self, _a, _b, _n):
        return np.array([.02, 0, .01])

    def random(self, n):
        return np.ones(n)

    def normal(self, _mu, _sd, n):
        return np.zeros(n)

    def lognormal(self, _mu, _sd, n):
        return np.full(n, 100.0)


class TestParteG(unittest.TestCase):
    def test_mmc_un_servidor_y_caso_inestable(self):
        rho, prob, espera = mmc_espera(.5, 1000, 1)
        np.testing.assert_allclose([rho, prob, espera], [.5, .5, 1000])
        rho, prob, espera = mmc_espera(1.2, 1000, 1)
        self.assertGreater(rho, 1)
        self.assertTrue(np.isnan(prob) and np.isnan(espera))

    def test_fifo_dos_servidores_y_conversion_unidades(self):
        actual = simular_fifo(RngControlado(), 1, 0, 1, 1, 1, 1, 2, 1)
        np.testing.assert_allclose(actual, [100, 100, 180])


    def test_cola_se_omite_en_cache(self):
        rng = RngControlado()
        rng.random = lambda n: np.zeros(n)
        actual = simular_fifo(rng, 1, 1, 1, 1, 1, 1, 2, 1)
        np.testing.assert_allclose(actual, [0, 0, 0])


    def test_reproducibilidad_y_validacion(self):
        args = (25, .4, 3.7, .65, 30, 4.6, 2, 10, 1)
        np.testing.assert_array_equal(simular_fifo(np.random.default_rng(123), *args),
                                      simular_fifo(np.random.default_rng(123), *args))
        with self.assertRaises(ValueError):
            simular_fifo(np.random.default_rng(123), 0, *args[1:])
