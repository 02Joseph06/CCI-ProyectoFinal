# Proyecto final — Andes Vision AI

Análisis de telemetría, alertas y capacidad GPU para Ciencia Computacional Intermedia. Los CSV del grupo corresponden a la semilla **S = 2279892322**, con confianza del 95 %, umbral de 190 ms y tolerancia del 2 %.

## Dónde está cada cosa

- [Notebook para Colab, sin `src/` externo](notebooks/Proyecto_Final_Colab_Sin_Src.ipynb): contiene el código y carga los CSV de Drive después de la autorización. Crea módulos temporales durante la ejecución y también admite CSV locales.
- [Notebook modular, dependiente de `src/`](notebooks/Proyecto_Final_Modular.ipynb): ejecuta las partes A–G con los módulos de [`src/`](src/) y los CSV de [`data/raw/`](data/raw/).
- [Resultados](outputs/README.md): tablas y figuras por apartado, informe y memorando.
- [Documentación](documentos/README.md): cálculos, decisiones, informe editable y guía de deducciones.
- [Pruebas](tests/README.md): verificaciones de auditoría, modelos, simulación y carga de datos.

## Ejecutar localmente

Desde la raíz, con el entorno virtual del proyecto y las dependencias de [requirements.txt](requirements.txt):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -q -b
```

Después abre el notebook modular y ejecuta todas sus celdas. Las salidas se generan en `outputs/`; los CSV originales no se modifican. Para el notebook de Colab, usa la cuenta con acceso a la carpeta de Drive configurada o cambia la fuente a `local` en la celda de preparación.

## Alcance de los resultados

El modelo principal selecciona 3 GPU bajo los supuestos documentados; el contraste M/M/c no cumple el mismo SLO con esa capacidad. En E4, la regla conjunta cumple el criterio puntual, pero no al usar el extremo superior conservador del intervalo de falsos positivos. Ambos resultados requieren interpretación del grupo y no son garantías operativas.

El informe y la declaración de IA son borradores para revisión; las deducciones manuscritas deben prepararse y verificarse por el grupo. Por decisión del grupo, `.gitignore` excluye `docs/` y `documentos/`; conserva el repositorio privado por los datos y las identificaciones del grupo.
