# Convenience targets. On Windows without `make`, run the commands directly
# (see README) or use:  python verify ...  /  python seed_runs.py.

PY ?= python

.PHONY: install install-evals install-appium app test ui mobile evals verify seed seed-mock browsers

install:            ## core install (testrelic-pytest + playwright reporter + app)
	$(PY) -m pip install -r requirements.txt

install-evals:      ## add the DeepEval suite deps
	$(PY) -m pip install -r requirements-evals.txt

install-appium:     ## add the Appium suite deps
	$(PY) -m pip install -r requirements-appium.txt

browsers:           ## download the Playwright browser
	$(PY) -m playwright install chromium

app:                ## run the ShopRelic API locally
	$(PY) -m shoprelic_api.run

test:               ## run the protocol suite (needs a key, or use verify for offline)
	$(PY) -m pytest tests -q

ui:                 ## run the Playwright suite (needs: make browsers)
	$(PY) -m pytest ui -q

mobile:             ## run the Appium suite (auto-skips without a device)
	$(PY) -m pytest mobile -q

evals:              ## run the DeepEval suite (needs: make install-evals)
	$(PY) -m pytest evals -q -p no:testrelic_pytest

verify:             ## offline end-to-end proof (no key, no network) — asserts all metrics
	$(PY) verification/verify.py

seed:               ## seed the 15-run regression arc to the real cloud (needs TESTRELIC_API_KEY)
	$(PY) seed_runs.py

seed-mock:          ## seed the arc against a local mock server (dry run)
	$(PY) seed_runs.py --mock
