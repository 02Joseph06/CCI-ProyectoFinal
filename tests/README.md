# Pruebas

Desde la raíz del proyecto, con el entorno virtual preparado:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q -b
```

La opción `-b` oculta la salida de las pruebas exitosas y la muestra si alguna falla. Para ver cada prueba, reemplaza `-q` por `-v`.

Las pruebas cubren auditoría y tramos, parámetros del grupo, distribuciones y regresión, alertas e inferencia, simulación FIFO y capacidad, generación del memorando y búsqueda de CSV en Drive. La prueba de Drive usa un servicio simulado; no comprueba el acceso real a la cuenta.
