# FreeNIC Anu replication package — run targets
# (make lives in anu/; run `make -C anu <target>` from the repo root)

.PHONY: all fetch construct validate registry check clean help

PY ?= python
S := scripts

help:
	@echo "Targets:"
	@echo "  make fetch        run all keyless public fetchers (L01, L05) + input checks"
	@echo "  make construct    P01-P06 (dictionary, ingest, catalogs, panels, recon, export)"
	@echo "  make validate     V01 --remote (registry vs served release + spot checks)"
	@echo "  make validate-local  V01 --local (offline)"
	@echo "  make registry     regenerate series_registry.json from the release manifest"
	@echo "  make check        input presence checks only (no downloads)"

fetch:
	$(PY) $(S)/L01_fetch_fdic.py
	$(PY) $(S)/L05_fetch_fred.py
	$(PY) $(S)/L02_fetch_ffiec_cdr.py --check
	$(PY) $(S)/L03_fetch_bhcf_mdrm.py --check
	$(PY) $(S)/L04_fetch_nic.py --check
	$(PY) $(S)/L06_fetch_occ_luck.py --check
	$(PY) $(S)/L07_fetch_ncua.py --check
	$(PY) $(S)/L08_fetch_supervisory.py --check
	$(PY) $(S)/L09_fetch_crosswalks.py --check
	$(PY) $(S)/L10_fetch_failing_banks.py --check

check:
	$(PY) $(S)/L01_fetch_fdic.py --check
	$(PY) $(S)/L05_fetch_fred.py --check
	$(PY) $(S)/L02_fetch_ffiec_cdr.py --check
	$(PY) $(S)/L03_fetch_bhcf_mdrm.py --check
	$(PY) $(S)/L04_fetch_nic.py --check
	$(PY) $(S)/L06_fetch_occ_luck.py --check
	$(PY) $(S)/L07_fetch_ncua.py --check
	$(PY) $(S)/L08_fetch_supervisory.py --check
	$(PY) $(S)/L09_fetch_crosswalks.py --check
	$(PY) $(S)/L10_fetch_failing_banks.py --check

construct:
	$(PY) $(S)/P01_ingest_dictionary.py
	$(PY) $(S)/P02_ingest_sources.py
	$(PY) $(S)/P03_build_catalogs.py
	$(PY) $(S)/P04_build_panels.py
	$(PY) $(S)/P05_build_reconstruction.py
	$(PY) $(S)/P06_export_release.py

validate:
	$(PY) $(S)/V01_validate.py --remote

validate-local:
	$(PY) $(S)/V01_validate.py --local

registry:
	$(PY) $(S)/make_registry.py --remote

all: registry validate
	@echo "Package validated against the served release. Run fetch+construct to rebuild."

clean:
	rm -rf data/raw data/processed data/outputs
