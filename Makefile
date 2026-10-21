DIST := dist
NAME := 2Do.alfredworkflow
BUILD := $(DIST)/.build
RUN := uv run --no-sync
SHELL_SCRIPTS := $(wildcard src/*.sh)
JXA_SCRIPTS := $(wildcard src/*.js)
export HOMEBREW_NO_AUTO_UPDATE := 1

.PHONY: setup icons test lint lint-python lint-shell lint-jxa lint-data lint-md lint-actions format format-check audit check ci build clean release sync-plist link-live

setup:
	brew bundle --quiet
	uv sync --group dev

icons:
	icon-symbol.sh --batch tools/icons.txt --outdir icons --fg "#FFFFFF" --size 256

test:
	$(RUN) pytest

lint: lint-python lint-shell lint-jxa lint-data lint-md lint-actions

lint-python:
	$(RUN) ruff check .

lint-shell:
	shellcheck $(SHELL_SCRIPTS)

lint-jxa:
	@mkdir -p $(BUILD)
	$(foreach script,$(JXA_SCRIPTS),osacompile -l JavaScript -o $(BUILD)/lint.scpt $(script) &&) rm -f $(BUILD)/lint.scpt

lint-data:
	plutil -lint info.plist

lint-md:
	markdownlint-cli2 "**/*.md"

lint-actions:
	actionlint

format:
	$(RUN) ruff format .

format-check:
	$(RUN) ruff format --check .

audit:
	$(RUN) pip-audit --skip-editable

check: lint format-check test

ci: check audit

build: clean check
	mkdir -p $(BUILD)/src
	cp info.plist icon.png $(BUILD)/
	cp -R icons $(BUILD)/
	cp src/todo.py src/python.sh src/bridge.js $(BUILD)/src/
	cp -R src/todolib $(BUILD)/src/
	find $(BUILD) -name '__pycache__' -prune -exec rm -rf {} +
	mkdir -p $(BUILD)/images
	cp -R images/about $(BUILD)/images/
	cd $(BUILD) && zip -r -q ../$(NAME) .
	rm -rf $(BUILD)
	@echo "built $(DIST)/$(NAME)"

clean:
	rm -rf $(DIST)
	mkdir -p $(DIST)

release: build
	@test -n "$(VERSION)" || (echo "usage: make release VERSION=v1.0.0" && exit 1)
	git tag $(VERSION)
	git push origin $(VERSION)
	gh release create $(VERSION) $(DIST)/$(NAME) --generate-notes

# pulls info.plist + icon.png from the live Alfred workflow bundle after
# editing keywords/hotkeys/icons etc in the Alfred UI. WORKFLOW_DIR is
# machine-specific, never hardcoded here - pass it at invocation.
sync-plist:
	@test -n "$(WORKFLOW_DIR)" || (echo "usage: make sync-plist WORKFLOW_DIR=/path/to/bundle" && exit 1)
	cp "$(WORKFLOW_DIR)/info.plist" info.plist
	cp "$(WORKFLOW_DIR)/icon.png" icon.png
	@echo "synced info.plist + icon.png from $(WORKFLOW_DIR)"

link-live:
	@test -n "$(WORKFLOW_DIR)" || (echo "usage: make link-live WORKFLOW_DIR=/path/to/bundle" && exit 1)
	ln -sfn "$(CURDIR)/images" "$(WORKFLOW_DIR)/images"
	ln -sfn "$(CURDIR)/src" "$(WORKFLOW_DIR)/src"
	ln -sfn "$(CURDIR)/icons" "$(WORKFLOW_DIR)/icons"
	ln -sfn "$(CURDIR)/icon.png" "$(WORKFLOW_DIR)/icon.png"
	@echo "linked $(WORKFLOW_DIR) to this repo"
