SHELL := /bin/bash

.PHONY: example-api-testing example-unified-testing \
       example-wikipedia example-flipkart example-google \
       examples examples-api examples-e2e help

##@ API Examples

example-api-testing: ## Run API testing example (no browser needed)
	cd api-testing && npm install && npx playwright test

##@ E2E Examples

example-wikipedia: ## Run Wikipedia example
	cd wikipedia && npm install && npx playwright install chromium && npx playwright test

example-flipkart: ## Run Flipkart example
	cd flipkart && npm install && npx playwright install chromium && npx playwright test

example-google: ## Run Google example
	cd google && npm install && npx playwright install chromium && npx playwright test

##@ Unified Examples

example-unified-testing: ## Run unified (E2E + API) testing example
	cd unified-testing && npm install && npx playwright install chromium && npx playwright test

##@ Run All

examples-api: example-api-testing ## Run all API examples

examples-e2e: example-wikipedia example-flipkart example-google ## Run all E2E examples

examples: example-api-testing example-unified-testing example-wikipedia example-flipkart example-google ## Run all examples

##@ Help

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } \
		/^[a-zA-Z_-]+:.*?## / { printf "  \033[36m%-25s\033[0m %s\n", $$1, substr($$0, index($$0, "## ") + 3) }' $(MAKEFILE_LIST)
