# CCI-ProyectoFinal

Análisis reproducible de telemetría para el proyecto de Ciencia Computacional
Intermedia. Las partes A, B, C y D están implementadas en el notebook
[`notebooks/partes_A_B.ipynb`](notebooks/partes_A_B.ipynb).
El mismo notebook incluye E, F y G1–G2, más un contraste parcial de G3 y un
memorando G4 provisional. Las discrepancias y decisiones pendientes están en
`documentos/calculos/discrepancias_pendientes.md` y deben resolverse antes de
considerar definitivas las recomendaciones.

1. Cree un entorno Python e instale las dependencias con
   `python -m pip install -r requirements.txt`.
2. Abra el notebook desde la raíz del repositorio o desde `notebooks/` y
   ejecútelo de principio a fin con el kernel del entorno.
3. Las tablas y figuras se generan en [`outputs/`](outputs/); los archivos
   originales en [`data/raw/`](data/raw/) no se modifican. El archivo de
   validación se reserva para el punto F6.

El notebook registra las identificaciones y la semilla del grupo; por ello el
repositorio debe permanecer privado. Usa `np.random.default_rng(S)` como fuente
de aleatoriedad. La documentación de trabajo de `documentos/` y `docs/` es
local y está excluida de Git por decisión del grupo.

La selección del régimen estable y las exclusiones aplicadas a la telemetría
son supuestos de análisis. En particular, las tasas obtenidas después de
excluir filas por datos de latencia describen las solicitudes conservadas y
pueden diferir de las tasas del tráfico original.

En C3 se conserva la referencia Anderson–Darling de 0,656 elegida por el
grupo y, por separado, el valor 0,631 calculado por SciPy 1.18.1. Esa versión
se fija en las dependencias porque la interfaz de valores críticos cambia en
versiones posteriores. Las deducciones manuscritas y la interpretación para
el informe siguen siendo responsabilidad del grupo.
