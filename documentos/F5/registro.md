# F5 - Tamaño de muestra por versión

Para tamaños iguales, desviaciones $s_A,s_B$ observadas en las no cacheadas y semiancho objetivo $h=1$ ms: $n=\left\lceil z_{1-\alpha_*/2}^2(s_A^2+s_B^2)/h^2\right\rceil$. Para el intervalo individual $\alpha_*=0,10$; para protección simultánea de tres métricas, $\alpha_*=0,10/3$. Esta aproximación usa z y varianzas tratadas como valores de planificación; no garantiza que el semiancho de todas las muestras futuras sea menor que 1 ms.

Se verifican 1.000 pares de muestras empíricas con reemplazo por método; se registran cobertura, semiancho medio y fracción de semianchos ≤1. Evidencia: `outputs/F5/tamano_muestral_F5.csv`. Los resultados calculados son 7.392 y 12.372 por versión, frente a 7.388 y 12.325 suministrados; no se declaran equivalentes. El grupo confirmó la prioridad del cálculo desde el CSV. La deducción manuscrita corresponde al grupo y no se afirma como hecha.
