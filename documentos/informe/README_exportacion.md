# Regenerar el informe Word y PDF

Ejecuten estos comandos desde la raíz del proyecto en PowerShell, con el entorno virtual del proyecto creado y sus dependencias de análisis instaladas (entre ellas `matplotlib`):

```powershell
.\.venv\Scripts\python.exe -m pip install -r documentos/informe/requirements-informe.txt
.\.venv\Scripts\python.exe documentos/informe/exportar_informe.py
```

El exportador lee `informe_A_G.md`, las figuras locales, `outputs/G4/memorando_ejecutivo_G4.md` y `declaracion_uso_ia.md`. Escribe `outputs/informe/informe_A_G.docx` y `outputs/informe/informe_A_G.pdf`, incorporando el memorando y la declaración como anexos independientes. Vuelve a abrir el Word y comprueba que el PDF tenga como máximo 14 páginas de cuerpo y una de memorando. Si faltan una figura, el memorando o la declaración, hay que generarlos antes de exportar.

`python-docx` y `pypdf` son dependencias **opcionales para la exportación y su comprobación**, no se utilizan en los análisis estadísticos. El archivo principal de requisitos del proyecto no se modifica. La paginación del Word puede variar según la aplicación y las fuentes instaladas; revisen visualmente ambos documentos antes de entregarlos. El informe y la declaración siguen siendo borradores para revisión y firma del grupo.
