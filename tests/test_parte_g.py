import numpy as np
import pandas as pd
import unittest

from src.parte_g import (simular_fifo, mmc_espera, evaluar_escenarios_g3,
                         generar_escenarios_g3, mmc_cola_latencia, ejecutar_g3)


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
    def test_g3_muestreo_reproducible_y_restricciones(self):
        datos = pd.DataFrame({"cache_hit": [1, 0, 1, 0],
                              "gpu_ms": [0., 10., 0., 20.],
                              "red_ms": [20., 21., 22., 23.]})
        a = generar_escenarios_g3(datos, np.random.default_rng(9), 12)
        b = generar_escenarios_g3(datos, np.random.default_rng(9), 12)
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(len(a), 12)
        self.assertTrue(((a.prob_cache >= 0) & (a.prob_cache <= 1)).all())
        self.assertTrue((a.tasa_s > 0).all() and (a.sigma_log > 0).all())
        self.assertTrue((a.red_media == 21.5).all())
        with self.assertRaises(ValueError):
            generar_escenarios_g3(datos.assign(gpu_ms=0.), np.random.default_rng(1))

    def test_g3_duracion_total_incluye_calentamiento(self):
        from unittest.mock import patch
        datos = pd.DataFrame({"cache_hit": [1, 0, 1, 0],
                              "gpu_ms": [0., 10., 0., 10.1],
                              "red_ms": [20., 21., 22., 23.]})
        datos = pd.concat([datos]*100, ignore_index=True)
        from src import parte_g
        original = parte_g.evaluar_escenarios_g3
        with patch("src.parte_g.evaluar_escenarios_g3", wraps=original) as evaluador:
            ejecutar_g3(datos, seed=9, n_escenarios=2, replicas=2,
                        duracion_s=400, calentamiento_s=20, capacidades=(2,), guardar=False)
        self.assertEqual(evaluador.call_args.args[4:6], (380, 20))
        with self.assertRaises(ValueError):
            ejecutar_g3(datos, duracion_s=20, calentamiento_s=20, guardar=False)

    def test_g3_mmc_con_red_y_cache_compara_con_monte_carlo(self):
        from scipy import stats
        rng = np.random.default_rng(764)
        tasa, cache, media_ms, c = 7., .3, 100., 2
        rho, p_espera, _ = mmc_espera(tasa*(1-cache), media_ms, c)
        cantidad = 300000
        hit = rng.random(cantidad) < cache
        red = rng.normal(30, 5, cantidad)
        espera = (rng.random(cantidad) < p_espera)*rng.exponential(
            1000/(c*1000/media_ms-tasa*(1-cache)), cantidad)
        servicio = rng.exponential(media_ms, cantidad)
        cola_mc = np.mean(red + (~hit)*(espera+servicio) > 210)
        _, cola_analitica = mmc_cola_latencia(
            tasa, cache, np.log(media_ms), 1e-8, 30, 5, c)
        self.assertLess(abs(cola_mc-cola_analitica), .003)

    def test_g3_mmc_cola_y_sin_estabilidad(self):
        from scipy.stats import norm
        rho, valor = mmc_cola_latencia(1, 1, np.log(100), .01, 30, 5, 2, 40)
        self.assertAlmostEqual(rho, 0)
        self.assertAlmostEqual(valor, norm.sf(2))
        rho, valor = mmc_cola_latencia(100, 0, np.log(1000), .01, 30, 5, 2)
        self.assertGreater(rho, 1)
        self.assertTrue(np.isnan(valor))

    def test_g3_distribucion_incluye_todos_los_escenarios(self):
        datos = pd.DataFrame({"cache_hit": [1, 0, 1, 0],
                              "gpu_ms": [0., 10., 0., 20.],
                              "red_ms": [20., 21., 22., 23.]})
        escenarios, detalle, dist, resumen = ejecutar_g3(
            datos, seed=9, n_escenarios=4, replicas=2, duracion_s=20000,
            calentamiento_s=0, capacidades=(2, 3), guardar=False)
        self.assertEqual(len(escenarios), 4)
        self.assertEqual(len(detalle), 8)
        self.assertEqual(dist.escenarios.sum(), 4)
        self.assertAlmostEqual(dist.proporcion.sum(), 1)
        self.assertTrue((resumen.escenarios == 4).all())

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

    def test_g3_busca_minimo_por_escenario_y_no_usa_colas_inestables(self):
        escenario = dict(tasa_s=2, prob_cache=0, mu_log=np.log(1000),
                         sigma_log=.01, red_media=30, red_desv=1)

        def simulador(_rng, tasa, cache, mu, sigma, red, desv, c, duracion, calor):
            return np.full(10, 250. if c == 3 else 100.)

        resultado = evaluar_escenarios_g3([escenario], [4, 1, 3],
                                         np.random.default_rng(123), 2, 1, 0,
                                         210, .01, "estimacion", simulador)
        self.assertEqual(resultado.gpus.tolist(), [1, 3, 4])
        self.assertFalse(resultado.loc[0, "estable"])
        self.assertTrue(np.isnan(resultado.loc[0, "violacion"]))
        self.assertEqual(resultado.c_optimo_entre_capacidades_evaluadas.tolist(), [4, 4, 4])

    def test_g3_sin_capacidad_apta_y_validacion_de_entrada(self):
        escenario = dict(tasa_s=1, prob_cache=.4, mu_log=3.7,
                         sigma_log=.65, red_media=30, red_desv=4.6)
        simulador = lambda *args: np.full(10, 300.)
        salida = evaluar_escenarios_g3([escenario, escenario], [2],
                                       np.random.default_rng(7), 2, 1, 0,
                                       210, .01, "limite_superior_90", simulador)
        self.assertTrue(salida.c_optimo_entre_capacidades_evaluadas.isna().all())
        with self.assertRaises(ValueError):
            evaluar_escenarios_g3([escenario], [2], np.random.default_rng(7),
                                  2, 1, 0, 210, .01, "automatica", simulador)

    def test_g3_cruce_de_criterios_y_reproducibilidad(self):
        escenario = dict(tasa_s=1, prob_cache=.4, mu_log=3.7,
                         sigma_log=.65, red_media=30, red_desv=4.6)

        def simular_con_alternancia():
            valores = iter([np.zeros(100), np.r_[np.full(2, 300.), np.zeros(98)]])
            return lambda *args: next(valores)

        def ejecutar(regla):
            return evaluar_escenarios_g3([escenario], [2], np.random.default_rng(7),
                                        2, 1, 0, 210, .01, regla,
                                        simular_con_alternancia())

        puntual = ejecutar("estimacion")
        superior = ejecutar("limite_superior_90")
        self.assertEqual(puntual.loc[0, "violacion"], .01)
        self.assertTrue(puntual.loc[0, "cumple"])
        self.assertFalse(superior.loc[0, "cumple"])
        np.testing.assert_equal(ejecutar("estimacion").to_numpy(), puntual.to_numpy())
