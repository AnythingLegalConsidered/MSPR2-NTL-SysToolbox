# NTL-SysToolbox — Commandes de dev
# Usage: make <commande>

.PHONY: setup setup-linux setup-dev run test lint typecheck clean help

# Setup environment (Windows)
setup:
	python -m venv venv
	./venv/Scripts/pip install -r requirements.txt
	@echo "Setup OK. Activez le venv: source venv/Scripts/activate (Git Bash) ou venv\\Scripts\\activate (CMD)"

# Setup environment (Linux)
setup-linux:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "Setup OK. Activez le venv: source venv/bin/activate"

# Install dev dependencies (linters, test tools)
setup-dev:
	pip install -r requirements-dev.txt

# Run the CLI
run:
	python src/main.py

# Run tests with coverage
test:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Lint (ruff)
lint:
	ruff check src/ tests/

# Type check (mypy)
typecheck:
	mypy src/ --ignore-missing-imports

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf output/logs/* output/backups/* output/reports/*

# Show help
help:
	@echo "Commandes disponibles:"
	@echo "  make setup        — Creer le venv + installer les deps (Windows)"
	@echo "  make setup-linux  — Creer le venv + installer les deps (Linux)"
	@echo "  make setup-dev    — Installer les deps de dev (ruff, mypy, pytest-cov)"
	@echo "  make run          — Lancer le CLI"
	@echo "  make test         — Lancer les tests avec couverture"
	@echo "  make lint         — Verifier le code avec ruff"
	@echo "  make typecheck    — Verifier les types avec mypy"
	@echo "  make clean        — Nettoyer les fichiers generes"
