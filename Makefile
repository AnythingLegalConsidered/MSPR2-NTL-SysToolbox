# NTL-SysToolbox — Commandes de dev
# Usage: make <commande>

.PHONY: setup run test lint clean help

# Setup environment
setup:
	python -m venv venv
	./venv/Scripts/pip install -r requirements.txt
	@echo "Setup OK. Activez le venv: source venv/Scripts/activate (Git Bash) ou venv\\Scripts\\activate (CMD)"

# Setup Linux
setup-linux:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "Setup OK. Activez le venv: source venv/bin/activate"

# Run the CLI
run:
	python src/main.py

# Run tests
test:
	python -m pytest tests/ -v

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
	@echo "  make run          — Lancer le CLI"
	@echo "  make test         — Lancer les tests"
	@echo "  make clean        — Nettoyer les fichiers generes"
