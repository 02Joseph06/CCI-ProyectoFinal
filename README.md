# CCI-ProyectoFinal

Análisis reproducible de telemetría para el proyecto de Ciencia Computacional
Intermedia. Las partes A y B están implementadas en el notebook
[`notebooks/partes_A_B.ipynb`](notebooks/partes_A_B.ipynb).

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
