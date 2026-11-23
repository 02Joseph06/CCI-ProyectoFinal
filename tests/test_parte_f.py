import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pandas as pd
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

    def test_f3_ic_conjuntos(self):
        with tempfile.TemporaryDirectory() as td:
            df=pd.DataFrame({'version':['A']*4+['B']*4,'cache_hit':[0]*8,'gpu_ms':[1,2,3,4,2,3,4,5],
                            'intentos':[1,1,1,2,1,1,2,2],'latencia_ms':[10,10,10,220,10,10,220,220],
                            'tam_kb':[1,2,3,4,2,3,4,5]})
            with patch.object(parte_f,'ROOT',Path(td)):
                parte_f.f3(df)
            out=pd.read_csv(Path(td)/'outputs/F3/comparacion_AB_F3.csv')
            self.assertEqual(len(out),3)
            self.assertTrue(np.allclose(out.nivel_conjunto_minimo,.9))
            self.assertTrue(np.all(out.ic_bonferroni_inferior<=out.diferencia_B_menos_A))
            self.assertTrue(np.all(out.diferencia_B_menos_A<=out.ic_bonferroni_superior))

if __name__=='__main__': unittest.main()
