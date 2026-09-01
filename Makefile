# Distroless runtime benchmark — GNU Make entrypoint
# Usage: make | make bench | make report | make help

.PHONY: all bench report help

PYTHON ?= python3
SCRIPTS := scripts

all: bench

bench:
	$(PYTHON) $(SCRIPTS)/benchmark.py

report:
	$(PYTHON) $(SCRIPTS)/regenerate_cve_breakdown.py

help:
	@echo "Targets:"
	@echo "  make / make bench  — полный прогон (build → smoke → grype → report)"
	@echo "  make report        — пересобрать reports/latest.md из reports/raw"
	@echo "  make help          — эта справка"
	@echo ""
	@echo "Env: PLATFORM PORT SMOKE_RETRIES SMOKE_SLEEP (пробрасываются в benchmark.py)"
