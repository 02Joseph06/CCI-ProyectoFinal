# Guía digital de las deducciones B3, C1, D3 y F5

**Propósito.** Recopilar las fórmulas, pasos y resultados disponibles para que el grupo los revise y pueda preparar su propio trabajo manuscrito. Este archivo es digital: no acredita que las deducciones manuscritas estén realizadas. El enunciado oficial, sección 6, entregable E3, pide deducciones manuscritas legibles, escaneadas o fotografiadas, con los números del grupo. La sección 7 también establece restricciones al uso de IA; el grupo debe verificar su aplicación y poder explicar el trabajo.

Los apuntes de clase proporcionados tratan probabilidad, esperanza y varianza total, distribución normal y estimación; la formulación matricial y la verosimilitud específicas se cotejan con el procedimiento indicado por el estudiante y la implementación existente. Esta guía no sustituye la deducción que el grupo debe comprender y escribir. Los resultados se refieren a la base auditada y al régimen estable escogido: $[0,668)\cup[838,1200]$ s. En las salidas actuales hay $n=24\,956$ solicitudes estables; $14\,696$ no cacheadas. Semilla de grupo $S=2046185499$, nivel de confianza $90\%$.

**Origen de los pasos.** El estudiante aportó las fórmulas de C1, el sistema matricial de D3 y la fórmula de planificación F5; B3 está documentado en los registros anteriores. Los pasos intermedios de diferenciación y expansión mostrados aquí son una reconstrucción digital a partir de esas fórmulas y del código, no una transcripción verificada de una deducción manuscrita del estudiante. No consta en los materiales consultados una deducción manuscrita específica y completa de cada uno de estos cuatro puntos. El grupo debe cotejar, completar y elaborar sus propios pasos manuscritos.

## B3 — Máxima verosimilitud con hasta tres intentos

**Definiciones y supuestos.** Para la solicitud $i$, $K_i\in\{1,2,3\}$ es el número de intentos y $E_i\in\{0,1\}$ indica éxito final. Cada intento falla con probabilidad común $q$, independientemente de los demás, y se detiene al primer éxito o tras tres fallos. Estos supuestos son parte del modelo, no una propiedad demostrada por la fórmula. $q$ es adimensional.

**Datos generados.** Si $E_i=1$, los primeros $K_i-1$ intentos fallaron y el último tuvo éxito; si $E_i=0$, hubo tres fallos. Por tanto, los fallos observados para la solicitud son $K_i-E_i$ y los éxitos observados son $E_i$. El número total de intentos observados es $A=\sum_iK_i$ y el total de fallos $F=\sum_i(K_i-E_i)$.

La contribución de una solicitud es $q^{K_i-E_i}(1-q)^{E_i}$ y, bajo independencia entre solicitudes,

$$L(q)=q^F(1-q)^{A-F},\qquad
\ell(q)=F\log q+(A-F)\log(1-q).$$

Para $0<F<A$, derivando e igualando a cero:

$$\ell'(q)=\frac{F}{q}-\frac{A-F}{1-q}=0
\quad\Longrightarrow\quad \widehat q=\frac{F}{A},$$

$$\ell''(q)=-\frac{F}{q^2}-\frac{A-F}{(1-q)^2}<0,$$

lo que verifica un máximo interior. En los casos de borde $F=0$ o $F=A$ el máximo está respectivamente en $q=0$ o $q=1$.

**Sustitución y verificación.** En la salida vigente, $F=4501$, $A=29360$, por tanto $\hat q=0,1533038$ y el intervalo al $90\%$ por perfil de verosimilitud es $[0,1498666;0,1567836]$. La comparación mediante 1.000 simulaciones calibradas y el estimador inmediato constan en [B3](../B3/registro.md) y [resultados de B](../../outputs/B/resultados.json). La adecuación de los supuestos y la valoración del estimador inmediato deben discutirse con esa evidencia, no deducirse solo de la expresión de $\hat q$.

## C1 — FDA y momentos de la mezcla de GPU

**Definiciones.** Sea $C=1$ si hay caché y $C=0$ si no. $p=P(C=1)$; $G$ es tiempo de GPU en ms; $G_+=G\mid C=0$ es positivo bajo el modelo elegido y tiene FDA $F_+$, media $\mu_+$ en ms y varianza $\sigma_+^2$ en ms². Con caché $G=0$.

Por probabilidad total, $G$ tiene una masa puntual en cero y una parte positiva continua según el modelo elegido:

$$F_G(g)=\begin{cases}
0,&g<0,\\
p+(1-p)F_+(g),&g\ge 0.
\end{cases}$$

La FDA es mixta cuando $0<p<1$ y la parte positiva es continua; la representación empírica de $F_+$ es escalonada por ser una distribución de la muestra.

Condicionando en $C$,

$$E[G]=p\,E[G\mid C=1]+(1-p)E[G\mid C=0]=(1-p)\mu_+.$$

Asimismo, $E[G^2]=(1-p)(\sigma_+^2+\mu_+^2)$. Al restar $E[G]^2$:

$$\operatorname{Var}(G)
=(1-p)\sigma_+^2+p(1-p)\mu_+^2.$$

**Comprobación con frecuencias empíricas.** $\hat p=10260/24956=0,41112358$, $\hat\mu_+=53,288026$ ms y $\hat\sigma^2_{+,n}=1365,824299$ ms². Usando divisor $n$ coherentemente en las varianzas de la distribución empírica, la media es $31,380062$ ms y ambos lados de la identidad de varianza dan $1491,774994$ ms². La varianza muestral global con divisor $n-1$ es $1491,834773$ ms²: es una convención distinta, no una discrepancia de la identidad. Ver [C1](../C1/registro.md) y [salida numérica](../../outputs/C1/resultados.json).

## D3 — Sistema matricial de mínimos cuadrados

**Definiciones.** Solo para solicitudes sin caché, $x_i$ es tamaño en KB y $y_i=G_i$ en ms. La matriz $X$ tiene una primera columna de unos y una segunda con los $x_i$; $\boldsymbol y=(y_1,\ldots,y_n)^T$ y $\boldsymbol\beta=(\beta_0,\beta_1)^T$. Las unidades son ms para $\beta_0$ y ms/KB para $\beta_1$.

El objetivo ordinario es

$$Q(\boldsymbol\beta)=(\boldsymbol y-X\boldsymbol\beta)^T(\boldsymbol y-X\boldsymbol\beta).$$

Expandiendo y derivando respecto a $\boldsymbol\beta$ se obtiene

$$\nabla Q=-2X^T\boldsymbol y+2X^TX\boldsymbol\beta=0,
\qquad X^TX\widehat{\boldsymbol\beta}=X^T\boldsymbol y.$$

Si $X$ tiene rango completo, la solución única es

$$\widehat{\boldsymbol\beta}=(X^TX)^{-1}X^T\boldsymbol y.$$

La implementación resuelve el sistema lineal numéricamente, sin invertir explícitamente la matriz para calcular los coeficientes. Con estos datos: $\hat\beta_0=15,099850$ ms y $\hat\beta_1=0,145269$ ms/KB. Los residuos son $e_i=y_i-\hat\beta_0-\hat\beta_1x_i$.

**Ponderación indicada por el estudiante.** Para $x_i>0$, $w_i=1/x_i^2$ y $W=\operatorname{diag}(w_i)$, minimizar $Q_W=(\boldsymbol y-X\boldsymbol\beta)^TW(\boldsymbol y-X\boldsymbol\beta)$ conduce a

$$X^TWX\widehat{\boldsymbol\beta}_W=X^TW\boldsymbol y,
\qquad \widehat{\boldsymbol\beta}_W=(X^TWX)^{-1}X^TW\boldsymbol y.$$

En los resultados vigentes $\hat\beta_{0,W}=14,948771$ ms y $\hat\beta_{1,W}=0,144704$ ms/KB. Los intervalos al $90\%$ se expresan como $\hat\beta_j\pm t_{0,95;n-2}\operatorname{SE}(\hat\beta_j)$, con $n=14696$ y $t_{0,95;14694}=1,6449573$. Los errores clásicos y HC3 son distintos y se muestran separados en [intervalos](../../outputs/D3/intervalos_coeficientes.csv). La ponderación depende de la forma de varianza supuesta; HC3 ofrece una corrección aproximada ante heterocedasticidad, no elimina todas las fuentes de dependencia o sesgo. Ver [D3](../D3/registro.md) y [resultados](../../outputs/D3/resultados.json).

## F5 — Tamaño muestral por versión

**Planteamiento.** Se busca un semiancho objetivo $h=1$ ms para un intervalo de la diferencia de medias $\mu_B-\mu_A$ de tiempos GPU sin caché. Para muestras independientes de igual tamaño $n$ por versión y varianzas de planificación $s_A^2$ y $s_B^2$ en ms², la aproximación normal produce

$$H=z_{1-\alpha_*/2}\sqrt{\frac{s_A^2}{n}+\frac{s_B^2}{n}}
=z_{1-\alpha_*/2}\sqrt{\frac{s_A^2+s_B^2}{n}}.$$

Al requerir $H\le h$ y despejar $n$:

$$n\ge\frac{z_{1-\alpha_*/2}^{\,2}(s_A^2+s_B^2)}{h^2},\qquad
n_{\text{plan}}=\left\lceil\frac{z_{1-\alpha_*/2}^{\,2}(s_A^2+s_B^2)}{h^2}\right\rceil.$$

Para el intervalo individual al $90\%$, $\alpha_*=0,10$. Para la protección conjunta Bonferroni de tres métricas con error familiar $0,10$, $\alpha_*=0,10/3$. El techo redondea hacia arriba. El cálculo es de planificación con varianzas consideradas fijas; no garantiza ese semiancho en cada muestra futura.

**Discrepancia pendiente.** La [salida reproducida](../../outputs/F5/tamano_muestral_F5.csv) usa $s_A^2=1377,882032$ y $s_B^2=1354,072309$ ms² y registra **7392** por versión para el intervalo individual y **12372** con Bonferroni. El aporte del estudiante indica **7388** y **12325**, respectivamente. No se han conciliado los valores, cuantiles o convenciones que producen ambas parejas; se mantiene pendiente la elección para el informe. La misma salida contiene una comprobación por 1000 remuestreos, cuyo propósito y limitaciones figuran en [F5](../F5/registro.md).

## Comprobaciones y pendientes del grupo

- Revisar las cuatro deducciones, sus supuestos y las unidades con los resultados del notebook; resolver la discrepancia F5 antes de presentar una cifra final.
- Realizar, escanear o fotografiar las cuatro deducciones manuscritas exigidas en E3; este Markdown no se presenta como sustituto.
- Mantener la trazabilidad a los apuntes y a las salidas del grupo; una verificación algebraica o numérica no demuestra por sí misma independencia, ajuste o validez de las hipótesis del modelo.
