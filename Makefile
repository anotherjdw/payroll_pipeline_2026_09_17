.PHONY: install test test-unit test-integration test-e2e lint format typecheck check fmt plan package catalog-apply clean

install:
	pip install -e ".[dev]"

test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-e2e:
	pytest -m end_to_end

lint:
	ruff check src/

format:
	ruff format src/

typecheck:
	mypy src/

check: lint typecheck test

fmt:
	terraform fmt -recursive infra/terraform/

plan:
	terraform -chdir=infra/terraform plan

package:
	mkdir -p dist && \
	cd src && find payroll_pipeline_2026_09_17 -type f \
		! -path "*/__pycache__/*" \
		! -path "*/tests/*" \
		! -path "*/jobs/*/*.yaml" \
		| grep -vE 'jobs/([^/]+)/\1\.py$$' \
		| zip -q ../dist/payroll_pipeline_2026_09_17.zip -@

catalog-apply:   ## Create or update the Iceberg sink tables from infra/catalog/*.sql
	@scripts/apply_catalog.sh

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
