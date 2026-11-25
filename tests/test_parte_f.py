import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
from scipy import stats
import parte_f

class TestParteF(unittest.TestCase):
    def test_tramos_sin_salto(self):
        df=pd.DataFrame({'t_llegada_s':[0,667.9,668,837.9,838,1200]})
        a,b=parte_f.estable(df)
        self.assertEqual(a.t_llegada_s.tolist(),[0,667.9])
        self.assertEqual(b.t_llegada_s.tolist(),[838,1200])

    def test_wilson_limites(self):
        lo,hi=parte_f.wilson(np.array([0,50,100]),100,1.6448536269514722)
        self.assertTrue(np.all(lo>=-1e-15) and np.all(hi<=1+1e-15))
        self.assertAlmostEqual(lo[0],0)
        self.assertAlmostEqual(hi[-1],1)

    def test_f1_error_monte_carlo_para_ambas_convenciones(self):
        with tempfile.TemporaryDirectory() as td:
            df=pd.DataFrame({'latencia_ms':np.arange(1, 101, dtype=float)})
            with patch.object(parte_f,'ROOT',Path(td)):
                parte_f.f1(df,np.random.default_rng(42),replicas=100)
            out=pd.read_csv(Path(td)/'outputs/F1/distribucion_muestral_F1.csv')
            for suffix in ('s_muestral','sigma_empirica'):
                coverage=out[f'cobertura_ic_normal_z_con_{suffix}']
                error=out[f'error_mc_cobertura_con_{suffix}']
                self.assertTrue(np.allclose(error,np.sqrt(coverage*(1-coverage)/100)))
            self.assertTrue((out.ic_mc_cobertura_inferior <= out.cobertura_ic_normal_z_con_s_muestral).all())
            self.assertTrue((out.cobertura_ic_normal_z_con_s_muestral <= out.ic_mc_cobertura_superior).all())
            resumen=pd.read_csv(Path(td)/'outputs/F1/resumen_cobertura_F1.csv').iloc[0]
            candidatos=out.loc[out.cobertura_ic_normal_z_con_s_muestral >= parte_f.CONFIANZA-.01, 'n']
            if not candidatos.empty:
                self.assertEqual(resumen.n_minimo_en_rejilla,candidatos.min())

    def test_f3_ic_conjuntos(self):
        with tempfile.TemporaryDirectory() as td:
            df=pd.DataFrame({'version':['A']*4+['B']*4,'cache_hit':[0]*8,'gpu_ms':[1,2,3,4,2,3,4,5],
                            'intentos':[1,1,1,2,1,1,2,2],'latencia_ms':[10,10,10,220,10,10,220,220],
                            'tam_kb':[1,2,3,4,2,3,4,5]})
            with patch.object(parte_f,'ROOT',Path(td)):
                parte_f.f3(df)
            out=pd.read_csv(Path(td)/'outputs/F3/comparacion_AB_F3.csv')
            self.assertEqual(len(out),3)
            self.assertTrue(np.allclose(out.nivel_conjunto_minimo,parte_f.CONFIANZA))
            self.assertTrue(np.all(out.ic_bonferroni_inferior<=out.diferencia_B_menos_A))
            self.assertTrue(np.all(out.diferencia_B_menos_A<=out.ic_bonferroni_superior))
            self.assertTrue(np.allclose(
                out.ic_bonferroni_superior-out.diferencia_B_menos_A,
                stats.norm.ppf(1-parte_f.ALPHA/6)*out.error_estandar))
            self.assertTrue(np.allclose(
                out.ic_individual_superior-out.diferencia_B_menos_A,
                stats.norm.ppf(1-parte_f.ALPHA/2)*out.error_estandar))
            self.assertTrue(out.metodo.str.contains('Welch').all())

if __name__=='__main__': unittest.main()
