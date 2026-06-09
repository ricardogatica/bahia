.PHONY: install run test clean help

help:
	@echo "Bahia - Makefile"
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  make install   - Instalar dependencias"
	@echo "  make run       - Ejecutar la app"
	@echo "  make dev       - Ejecutar en modo desarrollo"
	@echo "  make clean     - Limpiar archivos temporales"

install:
	pip install -r requirements.txt

run:
	python3 bahia.py

dev:
	python3 -u bahia.py

clean:
	rm -rf __pycache__ *.pyc .pytest_cache .eggs *.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} +

.DEFAULT_GOAL := help
