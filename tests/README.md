# RememberMed - Manual de Ejecución

## Requisitos
1. **Python 3.8+**: Asegúrate de tener Python instalado en tu sistema.
2. **Pip**: El gestor de paquetes de Python.
3. **Dependencias**: Todas las dependencias necesarias están listadas en `requirements.txt`.

## Instalación
1. Clona el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_REPOSITORIO>
2. Crea un entorno virtual
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
3. Instala las dependencias
    make install

## Ejecución
1. Inicia la aplicación
    make run
2. Accede a la aplicación en tu navegador en http://127.0.0.1:5000.

## Tests
1. Ejecuta todos los tests:
    make test
2. Genera un reporte de cobertura:
    make coverage