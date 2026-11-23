"""Parte F. Cálculos reproducibles; no altera los datos originales ni las partes A–D."""
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SEED = 2046185499
ALPHA = .1
TAU = 210


def guardar(df, punto, nombre):
    folder = ROOT / 'outputs' / punto
    folder.mkdir(parents=True, exist_ok=True)
    df.to_csv(folder / nombre, index=False)
    return folder


def estable(df):
    d = df.sort_values('t_llegada_s')
    a = d[(d.t_llegada_s >= 0) & (d.t_llegada_s < 668)].copy()
    b = d[(d.t_llegada_s >= 838) & (d.t_llegada_s <= 1200)].copy()
    return a, b


def f1(df, rng, replicas=20000):
    x = df.latencia_ms.to_numpy(); mu = x.mean(); resultados = []
    z = stats.norm.ppf(.95)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, n in zip(axes.flat, (5, 30, 200, 2000)):
        medias, stds = [], []
        for start in range(0, replicas, 250):
            a = rng.choice(x, size=(min(250, replicas-start), n), replace=True)
            medias.extend(a.mean(axis=1)); stds.extend(a.std(axis=1, ddof=1))
        medias, stds = np.asarray(medias), np.asarray(stds)
        coverage = np.mean(np.abs(medias-mu) <= z*stds/np.sqrt(n))
        fixed_coverage = np.mean(np.abs(medias-mu) <= z*x.std(ddof=0)/np.sqrt(n))
        # Intervalo Wilson del error de simulación, no intervalo de la media.
        mc_lo, mc_hi = wilson(int(round(coverage * replicas)), replicas, z)
        resultados.append({'n':n,'replicas':replicas,'media_poblacion_ms':mu,
                           'media_de_medias_ms':medias.mean(), 'desviacion_ms':medias.std(ddof=1),
                           'asimetria':stats.skew(medias,bias=False),
                           'exceso_curtosis':stats.kurtosis(medias,bias=False),
                           'cobertura_ic_normal_z_con_s_muestral':coverage,
                           'error_mc_cobertura_con_s_muestral':np.sqrt(coverage*(1-coverage)/replicas),
                           'ic90_mc_cobertura_inferior':mc_lo,
                           'ic90_mc_cobertura_superior':mc_hi,
                           'cobertura_ic_normal_z_con_sigma_empirica':fixed_coverage,
                           'error_mc_cobertura_con_sigma_empirica':np.sqrt(fixed_coverage*(1-fixed_coverage)/replicas),
                           'umbral_cobertura':.89})
        ax.hist(medias, bins=50, density=True, alpha=.7, label='Media muestral')
        ax.set(title=f'n = {n}', xlabel='Media de latencia (ms)', ylabel='Densidad (1/ms)')
        ax.legend()
    # La decisión solicitada usa s de cada réplica; sigma fija se conserva
    # únicamente como análisis de sensibilidad. Es una estimación Monte Carlo.
    candidatos = [r['n'] for r in resultados if r['cobertura_ic_normal_z_con_s_muestral'] >= .89]
    menor_n = min(candidatos) if candidatos else np.nan
    for resultado in resultados:
        resultado['criterio_principal'] = 'normal z con s de cada réplica'
        resultado['menor_n_evaluado_cobertura_al_menos_089'] = menor_n
    fig.suptitle('Figura 7. Distribución muestral empírica de la media'); fig.tight_layout()
    folder=guardar(pd.DataFrame(resultados),'F1','distribucion_muestral_F1.csv')
    pd.DataFrame([{'criterio':'cobertura estimada >= 0.89; z con s por réplica',
                   'n_minimo_en_rejilla':menor_n, 'rejilla':'5, 30, 200, 2000',
                   'replicas_por_n':replicas,
                   'advertencia':'La selección usa la estimación puntual; revisar IC Monte Carlo.'}]
                ).to_csv(folder/'resumen_cobertura_F1.csv',index=False)
    fig.savefig(folder/'figura_7_tcl_latencia.png',dpi=160); plt.close(fig)


def f2(partes, rng, replicas=20000, longitud=20):
    xs = [p.latencia_ms.to_numpy() for p in partes]; x = np.concatenate(xs)
    m=x.mean(); se=x.std(ddof=1)/np.sqrt(len(x)); t=stats.t.ppf(.95,len(x)-1)
    sims=np.empty(replicas)
    # Los bloques no cruzan el incidente; cada tramo conserva su tamaño original.
    for k in range(replicas):
        total=0.
        for v in xs:
            nb=int(np.ceil(len(v)/longitud)); starts=rng.integers(0,len(v)-longitud+1,nb)
            indices=(starts[:,None]+np.arange(longitud)).ravel()[:len(v)]
            total += v[indices].sum()
        sims[k]=total/len(x)
    lo,hi=np.quantile(sims,[.05,.95])
    guardar(pd.DataFrame([{'metodo':'t clásico','estimacion_ms':m,'inferior_ms':m-t*se,'superior_ms':m+t*se,'nivel':.9,'replicas':0,'longitud_bloque':0},
        {'metodo':'percentiles bootstrap de bloques móviles por tramo','estimacion_ms':m,'inferior_ms':lo,'superior_ms':hi,'nivel':.9,'replicas':replicas,'longitud_bloque':longitud}]),'F2','ic_latencia_F2.csv')


    autocorrelaciones=[]
    for nombre,v in zip(('inicial','posterior'),xs):
        for lag in (1,5,20,100):
            autocorrelaciones.append({'tramo':nombre,'n':len(v),'rezago_solicitudes':lag,
                                      'correlacion':np.corrcoef(v[:-lag],v[lag:])[0,1]})
    pd.DataFrame(autocorrelaciones).to_csv(ROOT/'outputs/F2/autocorrelacion_F2.csv',index=False)


def f3(df):
    a=df[df.version=='A']; b=df[df.version=='B']; out=[]
    # Bonferroni garantiza cobertura conjunta >= 90 % para las tres comparaciones.
    for metric, aa, bb in [ ('GPU sin caché (ms)',a.loc[a.cache_hit==0,'gpu_ms'].to_numpy(),b.loc[b.cache_hit==0,'gpu_ms'].to_numpy()),
                           ('reintento (>1)',(a.intentos>1).to_numpy(dtype=float),(b.intentos>1).to_numpy(dtype=float)),
                           ('violación SLO >210 ms',(a.latencia_ms>TAU).to_numpy(dtype=float),(b.latencia_ms>TAU).to_numpy(dtype=float)) ]:
        na,nb=len(aa),len(bb); va=aa.var(ddof=1)/na; vb=bb.var(ddof=1)/nb
        se=np.sqrt(va+vb); dof=(va+vb)**2/(va**2/(na-1)+vb**2/(nb-1))
        # El grupo escogió críticos normales para los intervalos. Se mantiene
        # el contraste t de Welch como prueba nominal separada de los IC.
        d=bb.mean()-aa.mean(); critical=stats.norm.ppf(1-ALPHA/(2*3))
        critical_individual=stats.norm.ppf(1-ALPHA/2)
        out.append({'metrica':metric,'n_A':na,'n_B':nb,'media_A':aa.mean(),'media_B':bb.mean(),'diferencia_B_menos_A':d,
                    'ic_bonferroni_inferior':d-critical*se,'ic_bonferroni_superior':d+critical*se,
                    'ic_individual_inferior':d-critical_individual*se,'ic_individual_superior':d+critical_individual*se,
                    'nivel_conjunto_minimo':.9,'p_sin_ajustar':2*stats.t.sf(abs(d/se),dof),
                    'metodo':'IC normal z con Bonferroni; p nominal t de Welch',
                    'error_estandar':se,'gl_welch':dof,'critico_z_bonferroni':critical,
                    'critico_z_individual':critical_individual})
    folder=guardar(pd.DataFrame(out),'F3','comparacion_AB_F3.csv')
    balance=[]
    for var in ['tam_kb','cache_hit']:
        x=a[var].dropna(); y=b[var].dropna(); test=stats.ttest_ind(x,y,equal_var=False)
        balance.append({'variable':var,'n_A':len(x),'n_B':len(y),'media_A':x.mean(),'media_B':y.mean(),'diferencia_B_A':y.mean()-x.mean(),'p_nominal_Welch':test.pvalue})
    # Balance adicional: KS de dos muestras para tamaño y chi-cuadrado para caché.
    ks=stats.ks_2samp(a.tam_kb.dropna(),b.tam_kb.dropna())
    table=pd.crosstab(df.version,df.cache_hit).reindex(index=['A','B'],columns=[0,1],fill_value=0)
    if (table.sum(axis=0)==0).any() or (table.sum(axis=1)==0).any():
        chi_stat,chi_p,chi_yates_stat,chi_yates_p=np.nan,np.nan,np.nan,np.nan
    else:
        chi=stats.chi2_contingency(table,correction=False)
        chi_yates=stats.chi2_contingency(table,correction=True)
        chi_stat,chi_p=chi.statistic,chi.pvalue
        chi_yates_stat,chi_yates_p=chi_yates.statistic,chi_yates.pvalue
    for var,metodo,stat,pval in [('tam_kb','KS dos muestras',ks.statistic,ks.pvalue),
                                 ('cache_hit','chi-cuadrado sin correccion',chi_stat,chi_p),
                                 ('cache_hit','chi-cuadrado con Yates',chi_yates_stat,chi_yates_p)]:
        balance.append({'variable':var,'prueba':metodo,'estadistico':stat,'p_nominal':pval})
    pd.DataFrame(balance).to_csv(folder/'balance_grupos_F3.csv',index=False)


def wilson(k,n,z):
    p=k/n; denom=1+z*z/n; center=(p+z*z/(2*n))/denom
    margin=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return center-margin,center+margin


def f4(rng,replicas=10000):
    z=stats.norm.ppf(.95); out=[]
    for n in (20,50,200,1000):
        for p in (.01,.05,.15,.5):
            k=rng.binomial(n,p,size=replicas); ph=k/n; error=z*np.sqrt(ph*(1-ph)/n)
            for name,(lo,hi) in [('Wald',(ph-error,ph+error)),('Wilson',wilson(k,n,z))]:
                covered=((lo<=p)&(p<=hi)).mean()
                counts=np.arange(n+1); observed=counts/n
                if name=='Wald':
                    err=z*np.sqrt(observed*(1-observed)/n); exact_lo,exact_hi=observed-err,observed+err
                else:
                    exact_lo,exact_hi=wilson(counts,n,z)
                exact_coverage=stats.binom.pmf(counts[(exact_lo<=p)&(p<=exact_hi)],n,p).sum()
                out.append({'n':n,'p_real':p,'metodo':name,'replicas':replicas,'cobertura':covered,'nivel_nominal':.9,
                            'error_mc':np.sqrt(covered*(1-covered)/replicas),'cobertura_binomial_exacta':exact_coverage})
    data=pd.DataFrame(out); folder=guardar(data,'F4','cobertura_wald_wilson_F4.csv')
    fig,axs=plt.subplots(1,4,figsize=(15,3.8),sharey=True)
    for ax,p in zip(axs,(.01,.05,.15,.5)):
        for metodo,g in data[data.p_real==p].groupby('metodo'):
            ax.plot(g.n,g.cobertura,marker='o',label=metodo)
        ax.axhline(.9,linestyle='--',color='black',label='Nominal 90 %'); ax.set(xscale='log',title=f'p = {p}',xlabel='Tamaño muestral n',ylabel='Cobertura')
        ax.legend()
    fig.suptitle('Figura 8. Cobertura simulada de intervalos de proporción');fig.tight_layout();fig.savefig(folder/'figura_8_cobertura_proporciones.png',dpi=160);plt.close(fig)


def f5(df,rng,replicas=1000):
    a=df[(df.version=='A') & (df.cache_hit==0)].gpu_ms.to_numpy()
    b=df[(df.version=='B') & (df.cache_hit==0)].gpu_ms.to_numpy(); varsum=a.var(ddof=1)+b.var(ddof=1)
    out=[]
    for name,q in [('individual',stats.norm.ppf(.95)),('Bonferroni 3 métricas',stats.norm.ppf(1-.1/6))]:
        n=int(np.ceil(q*q*varsum)); means=[]; half=[]
        for _ in range(replicas):
            aa=rng.choice(a,size=n); bb=rng.choice(b,size=n)
            means.append(bb.mean()-aa.mean()); half.append(q*np.sqrt(aa.var(ddof=1)/n+bb.var(ddof=1)/n))
        out.append({'metodo':name,'n_por_version':n,'varianza_A_ms2':a.var(ddof=1),'varianza_B_ms2':b.var(ddof=1),
                    'semiancho_proyectado_ms':q*np.sqrt(varsum/n),'replicas':replicas,'media_semiancho_simulado_ms':np.mean(half),
                    'fraccion_semiancho_menor_igual_1':np.mean(np.array(half)<=1),'cobertura_simulada':np.mean(np.abs(np.array(means)-(b.mean()-a.mean()))<=np.array(half))})
    guardar(pd.DataFrame(out),'F5','tamano_muestral_F5.csv')


def f6(df):
    # Reutiliza exactamente el auditor A1 dentro de un directorio temporal; no toca sus salidas.
    import auditoria
    source,output=auditoria.SOURCE,auditoria.OUTPUT
    try:
        with tempfile.TemporaryDirectory() as tmp:
            auditoria.SOURCE=ROOT/'data/raw/solicitudes_validacion.csv'; auditoria.OUTPUT=Path(tmp)
            auditoria.audit(); val=pd.read_csv(Path(tmp)/'solicitudes_auditadas.csv')
    finally:
        auditoria.SOURCE, auditoria.OUTPUT=source,output
    rows=[]
    def metrics(x,duration):
        g=x.loc[x.cache_hit==0,'gpu_ms']; failures=(x.intentos-x.exito).sum()
        return {'n':len(x),'tasa_llegadas_s':len(x)/duration,'p_cache':x.cache_hit.mean(),
                'media_gpu_no_cache_ms':g.mean(),'media_red_ms':x.red_ms.mean(),
                'media_latencia_ms':x.latencia_ms.mean(),'p_slo':(x.latencia_ms>TAU).mean(),
                'p_fallo_intento':failures/x.intentos.sum(),'p_reintento':(x.intentos>1).mean()}
    base,validation=metrics(df,1030),metrics(val,1200)
    for key in base:
        rows.append({'parametro':key,'base':base[key],'validacion':validation[key],'diferencia':validation[key]-base[key]})
    folder=guardar(pd.DataFrame(rows),'F6','comparacion_validacion_F6.csv')
    tests=[]
    for name,col in [('latencia','latencia_ms'),('red','red_ms'),('tamaño','tam_kb')]:
        x=df[col].dropna(); y=val[col].dropna(); test=stats.ks_2samp(x,y)
        tests.append({'variable':name,'n_base':len(x),'n_validacion':len(y),'KS':test.statistic,'p_nominal':test.pvalue})
    x=df.loc[df.cache_hit==0,'gpu_ms']; y=val.loc[val.cache_hit==0,'gpu_ms']; test=stats.ks_2samp(x,y)
    tests.append({'variable':'GPU no cacheada','n_base':len(x),'n_validacion':len(y),'KS':test.statistic,'p_nominal':test.pvalue})
    pd.DataFrame(tests).to_csv(folder/'pruebas_distribucionales_F6.csv',index=False)
    # Intervalos separados para los indicadores de C/F. Que una estimación
    # caiga dentro de un IC anterior no demuestra igualdad ni estacionariedad.
    comparison=[]
    z=stats.norm.ppf(.95)
    for label, column, kind, only_gpu in [
        ('caché','cache_hit','proporcion',False),
        ('GPU no cacheada (ms)','gpu_ms','media',True),
        ('red (ms)','red_ms','media',False),
        ('latencia (ms)','latencia_ms','media',False),
        ('violación SLO','latencia_ms','slo',False)]:
        x=df.loc[df.cache_hit==0,column].to_numpy() if only_gpu else df[column].to_numpy()
        y=val.loc[val.cache_hit==0,column].to_numpy() if only_gpu else val[column].to_numpy()
        if kind=='slo': x=(x>TAU).astype(int); y=(y>TAU).astype(int)
        if kind in ('slo','proporcion'):
            lo,hi=wilson(x.sum(),len(x),z)
        else:
            se=x.std(ddof=1)/np.sqrt(len(x)); q=stats.t.ppf(.95,len(x)-1)
            lo,hi=x.mean()-q*se,x.mean()+q*se
        comparison.append({'parametro':label,'metodo_ic_base':'Wilson' if kind!='media' else 't clásico',
                           'n_base':len(x),'n_validacion':len(y),'base':x.mean(),'validacion':y.mean(),
                           'ic_base_inferior':lo,'ic_base_superior':hi,'nivel':.9})
    pd.DataFrame(comparison).to_csv(folder/'comparacion_intervalos_C_F_F6.csv',index=False)
    from regimenes import segmentar
    segments=[]
    for width in (10,30):
        tramos,bics=segmentar(val.t_llegada_s.to_numpy(),width)
        for start,end,count in tramos:
            segments.append({'ancho_s':width,'inicio_s':start,'fin_s':end,'conteo':count,
                             'n_segmentos':len(tramos),'bic_min':min(bics)})
    pd.DataFrame(segments).to_csv(folder/'segmentacion_validacion_F6.csv',index=False)
    # B: comparaciones descriptivas y diagnosticos, no pruebas de equivalencia.
    series=[]
    for label, parts, duration in [('base',estable(df),1030),('validacion',[val.sort_values('t_llegada_s')],1200)]:
        combined=pd.concat(parts,ignore_index=True)
        gaps=np.concatenate([np.diff(part.t_llegada_s.to_numpy()) for part in parts])
        ks=stats.kstest(gaps,'expon',args=(0,gaps.mean()))
        blocks=[]
        for part in parts:
            retry=(part.intentos.to_numpy()>1).astype(int); m=len(retry)//100
            if m: blocks.extend(retry[:100*m].reshape(m,100).sum(axis=1))
        rate=len(combined)/duration; pretry=(combined.intentos>1).mean()
        mu=10*rate*pretry; k=int(np.ceil(mu))+3
        series.append({'conjunto':label,'n_gaps':len(gaps),'media_gap_s':gaps.mean(),
                       'ks_exponencial_nominal':ks.statistic,'ks_p_nominal_parametro_estimado':ks.pvalue,
                       'bloques_100':len(blocks),'media_reintentos_bloque':np.mean(blocks),
                       'varianza_reintentos_bloque':np.var(blocks,ddof=1),
                       'varianza_binomial_esperada':100*pretry*(1-pretry),
                       'p_reintento':pretry,'mu_10s':mu,'k_B4':k,
                       'p_B4_poisson_modelo':stats.poisson.sf(k-1,mu)})
    pd.DataFrame(series).to_csv(folder/'diagnosticos_B_F6.csv',index=False)
    version=[]
    for label,dat in [('base',df),('validacion',val)]:
        for ver in ('A','B'):
            part=dat[dat.version==ver]; g=part.loc[part.cache_hit==0,'gpu_ms']
            version.append({'conjunto':label,'version':ver,'n':len(part),
                            'gpu_no_cache_media_ms':g.mean(), 'n_gpu':len(g),
                            'p_reintento':(part.intentos>1).mean(),
                            'p_slo':(part.latencia_ms>TAU).mean(), 'p_cache':part.cache_hit.mean()})
    pd.DataFrame(version).to_csv(folder/'metricas_version_F6.csv',index=False)
    # Intervalos de B calculados desde la muestra de entrada, sin depender de
    # un archivo de resultados previo de otro modulo.
    from llegadas_intentos import profile_interval
    n=len(df); failure=int((df.intentos-df.exito).sum()); attempts=int(df.intentos.sum())
    rate_interval=[stats.chi2.ppf(.05,2*n)/(2*1030),stats.chi2.ppf(.95,2*(n+1))/(2*1030)]
    failure_interval=profile_interval(failure,attempts,.9)
    pd.DataFrame([{'parametro':'tasa_llegadas_s','estimacion_validacion':validation['tasa_llegadas_s'],'ic_base_inferior':rate_interval[0],'ic_base_superior':rate_interval[1]},
                  {'parametro':'p_fallo_intento','estimacion_validacion':validation['p_fallo_intento'],'ic_base_inferior':failure_interval[0],'ic_base_superior':failure_interval[1]}]).to_csv(folder/'comparacion_intervalos_B_F6.csv',index=False)


def main(seed=SEED):
    rng=np.random.default_rng(seed)
    df=pd.read_csv(ROOT/'outputs/A1/solicitudes_auditadas.csv')
    parts=estable(df); stable=pd.concat(parts,ignore_index=True)
    if len(stable)!=24956: raise ValueError(f'Régimen estable inesperado: {len(stable)} filas')
    f1(stable,rng); f2(parts,rng); f3(stable); f4(rng); f5(stable,rng); f6(stable)

if __name__=='__main__': main()
