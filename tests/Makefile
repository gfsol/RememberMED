# Variables
PYTHON = python
FLASK_APP = app.py
TEST_DIR = tests

# Comandos
install:
    @echo "Instalando dependencias..."
    pip install -r requirements.txt

run:
    @echo "Iniciando la aplicación..."
    $(PYTHON) $(FLASK_APP)

test:
    @echo "Ejecutando tests..."
    $(PYTHON) -m unittest discover $(TEST_DIR)

coverage:
    @echo "Generando reporte de cobertura..."
    coverage run -m unittest discover $(TEST_DIR)
    coverage report -m

clean:
    @echo "Limpiando archivos temporales..."
    rm -rf __pycache__ .coverage

.PHONY: install run test coverage clean