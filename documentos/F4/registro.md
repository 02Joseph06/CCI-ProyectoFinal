# Actualización vigente — S = 2279892322

Para n=20 y p=0,01, cobertura exacta Wald=0.18205, Wilson=0.98314; nivel 95 %.

Fuente: ../../outputs/F4/. Confianza 95 %.

## Registro histórico — semilla anterior; no vigente

# F4 - Cobertura de Wald y Wilson

Para $X\sim\mathrm{Binomial}(n,p)$, Wald es $\hat p\pm z_{.95}\sqrt{\hat p(1-\hat p)/n}$. Wilson tiene centro $(\hat p+z^2/(2n))/(1+z^2/n)$ y semiancho $z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}/(1+z^2/n)$. Se realizan 10.000 réplicas por configuración, con n=20,50,200,1000 y p=.01,.05,.15,.5, y se reporta el error Monte Carlo $\sqrt{\hat c(1-\hat c)/R}$.

Evidencia: `outputs/F4/cobertura_wald_wilson_F4.csv` y `figura_8_cobertura_proporciones.png`. Para n=20 y p=.01, Wald da 0,1761 y Wilson 0,8227. Esto contradice la afirmación previa de que Wilson alcanza al menos 0,89 para todas las configuraciones; la discreción binomial impide garantizar esa cobertura puntual. El grupo confirmó que prevalecen los resultados recalculados con los datos y la semilla; no se afirma esa garantía. Implementado y ejecutado.

Verificación exacta: con $n=20$, $p=.01$ y Wilson al 90 %, solo el resultado $X=0$ incluye $p$, por lo cual la cobertura es $0.99^{20}=0.8179069376$. La desviación respecto al Monte Carlo es compatible con su error muestral.
