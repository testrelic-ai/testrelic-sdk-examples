SHELL := /bin/bash

# Include nvm-managed Node.js binaries in PATH
NVM_BIN := $(lastword $(wildcard $(HOME)/.nvm/versions/node/*/bin))
ifneq ($(NVM_BIN),)
export PATH := $(NVM_BIN):$(PATH)
endif

.PHONY: example-api-testing example-unified-testing \
       example-wikipedia example-flipkart example-google example-amazon \
       example-appium example-maestro example-mobile-apps-download \
       examples examples-api examples-e2e examples-mobile help

##@ API Examples

example-api-testing: ## Run API testing example (no browser needed)
	cd playwright/api-testing && npm install && npx playwright test

##@ E2E Examples

example-wikipedia: ## Run Wikipedia example
	cd playwright/wikipedia && npm install && npx playwright install chromium && npx playwright test

example-flipkart: ## Run Flipkart example
	cd playwright/flipkart && npm install && npx playwright install chromium && npx playwright test

example-google: ## Run Google example
	cd playwright/google && npm install && npx playwright install chromium && npx playwright test

example-amazon: ## Run Amazon multi-page crawl example
	cd playwright/amazon && npm install && npx playwright install chromium && npx playwright test

##@ Unified Examples

example-unified-testing: ## Run unified (E2E + API) testing example
	cd playwright/unified-testing && npm install && npx playwright install chromium && npx playwright test

##@ Mobile Examples (require ../mobile-apps/wikipedia.apk + Android device/emulator)

example-mobile-apps-download: ## Download Wikipedia APK into mobile-apps/ (F-Droid production)
	cd mobile-apps && node download-wikipedia-apk.mjs

example-appium: ## Run Appium + WebdriverIO Wikipedia smoke (APK required)
	cd appium && npm install && npx appium driver install uiautomator2 2>/dev/null || true && npm test

example-maestro: ## Run Maestro flows with TestRelic wrapper (APK installed on device)
	cd maestro && npm install && npm test

##@ Run All

examples-api: example-api-testing ## Run all API examples

examples-e2e: example-wikipedia example-flipkart example-google example-amazon ## Run all Playwright E2E examples

examples-mobile: example-appium example-maestro ## Run mobile examples (device + APK required)

examples: example-api-testing example-unified-testing example-wikipedia example-flipkart example-google example-amazon ## Run all Playwright examples

##@ Help

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
		/^[a-zA-Z_-]+:.*?## / { printf "  \033[36m%-25s\033[0m %s\n", $$1, substr($$0, index($$0, "## ") + 3) }' $(MAKEFILE_LIST)
