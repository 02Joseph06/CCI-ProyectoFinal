# Fórmulas y cálculos vigentes — C y D

Grupo: C1=1137978133, C2=1141914189, S=2279892322; confianza 95 %, clases de 100 y 450 KB y N=14. Las observaciones proceden de los CSV confirmados por el grupo. Las deducciones manuscritas B3, C1, D3 y F5 siguen siendo responsabilidad del grupo.

## C1 — Distribución mixta de G

Sea $p=P(C=1)$ el acierto en caché, $G_+$ el tiempo de GPU sin caché en ms, $\mu_+=E[G_+]$ en ms y $\sigma_+^2=Var(G_+)$ en ms². Para $g<0$, $F_G(g)=0$; para $g\ge0$, $F_G(g)=p+(1-p)F_+(g)$.

$$E[G]=(1-p)\mu_+,\qquad Var(G)=(1-p)\sigma_+^2+p(1-p)\mu_+^2.$$

Con $\hat p=0,4111236$ y $\hat\mu_+=53,288026$ ms, $E[G]=31,380062$ ms; la varianza empírica con divisor n es $1491,774994$ ms² y coincide con la identidad. La varianza muestral con n−1 es $1491,834773$ ms². Implementación: [tiempos_cd.py](../../src/tiempos_cd.py); salida: [C1](../../outputs/C1/).

## C2 — Ajuste de G positivo

Para $g_i>0$, Gamma $(k,\theta)$ con $\theta$ en ms y lognormal $(\mu,\sigma)$ sobre $\log(g_i)$ usan:

$$\ell_\Gamma=(k-1)\sum_i\log g_i-\frac{1}{\theta}\sum_i g_i-n[\log\Gamma(k)+k\log\theta],$$
$$\ell_{LN}=-\sum_i\log g_i-n\log(\sigma\sqrt{2\pi})-\frac{\sum_i(\log g_i-\mu)^2}{2\sigma^2}.$$

Las funciones objetivo y sus gradientes se normalizan por n y se optimizan mediante BFGS. Gamma: k=2,52566, θ=21,09866 ms, KS descriptivo=0,03976. Lognormal: μ=3,76487, σ=0,65929, KS descriptivo=0,01072. Son ajustes marginales: no demuestran independencia ni invariancia si cambia la mezcla de tamaños. Fuente: [tiempos_c2.py](../../src/tiempos_c2.py) y [C2](../../outputs/C2/).

## C3 — Red

Con $R$ en ms, media $\hat\mu_R=29,61061$ y desviación muestral $s_R=4,60587$, la cola normal es $P(R>x)=1-\Phi((x-\hat\mu_R)/s_R)$. KS p=0,6773 es nominal por usar parámetros estimados. Anderson–Darling: A²=0,59109 y crítico al 5 % de SciPy=0,752. El percentil 99,9 empírico es 43,33 ms, con IC bootstrap percentil al 95 % [42,96; 43,819] ms. Fuente: [C3](../../outputs/C3/).

## C4 — Suma de N tiempos sin caché

Con $N=14$, $T_N=\sum_{i=1}^{N}G_{+,i}$ y umbral $u=N(\hat\mu_++15)=956,0324$ ms. Bajo independencia se comparan la aproximación normal con media $N\hat\mu_+$ y varianza $Ns_+^2$, la Gamma con forma $N\hat k$ y el remuestreo i.i.d. Los resultados son 0,06443, 0,05555 y 0,07538, respectivamente; IC Monte Carlo 95 % [0,07422; 0,07654]. El remuestreo no comprueba independencia temporal. Fuente: [C4](../../outputs/C4/resultados.json).

## D1 — Distribución conjunta de clase y caché

Clases: pequeña $x<100$, mediana $100\le x<450$ y grande $x\ge450$ KB. Para cada clase, $\hat p_c=n_{c,1}/n_c$ e IC Wald 95 % $\hat p_c\pm z_{0,975}\sqrt{\hat p_c(1-\hat p_c)/n_c}$. Las estimaciones son 0,58155, 0,38525 y 0,25675; χ²=933,2784, p≈2,194×10⁻²⁰³. Fuente: [D1](../../outputs/D1/).

## D2 — Esperanza y varianza total

Con $C$ la clase de tamaño, $E[G]=\sum_cP(C=c)E[G\mid C=c]$ y $Var(G)=E[Var(G\mid C)]+Var(E[G\mid C])$. Usando frecuencias y varianzas empíricas con divisor n: $1180,71903+311,05596=1491,77499$ ms²; la fracción entre clases es 20,8514 %. Para $G_+$ es 33,9251 %. El método continuo usa 25 cuantiles y LOWESS de fracción 0,15. Fuente: [D2](../../outputs/D2/).

## D3 — Regresión matricial

Para tamaño $x$ en KB y GPU $y$ en ms, OLS resuelve $X^TX\hat\beta=X^Ty$; WLS usa $W=diag(1/x_i^2)$ y resuelve $X^TWX\hat\beta_W=X^TWy$. OLS: $\hat G=15,09985+0,145269x$; WLS: $\hat G=14,94877+0,144704x$. IC 95 %: $\hat\beta_j\pm t_{0,975;14694}SE_j$, crítico 1,960125. Con HC3, WLS: intercepto [12,96768; 16,92986] ms y pendiente [0,131237; 0,158170] ms/KB. Los pesos son un supuesto; HC3 no resuelve toda dependencia. Fuente: [D3](../../outputs/D3/intervalos_coeficientes.csv).

## D4 — Covarianza y correlación

$s_{xG}=\sum_i(x_i-\bar x)(G_i-\bar G)/(n-1)$ y $r=s_{xG}/(s_xs_G)$. Entre solicitudes no cacheadas: covarianza 4526,5613 KB·ms, r=0,69384 y R²=0,48141. La asociación no demuestra causalidad. Fuente: [D4](../../outputs/D4/).

Los registros previos se conservan identificados como históricos en las carpetas de cada apartado. Esta guía digital no sustituye las deducciones manuscritas exigidas por el proyecto.
