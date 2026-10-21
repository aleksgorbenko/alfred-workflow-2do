DIST := dist
NAME := 2Do.alfredworkflow
BUILD := $(DIST)/.build
APPLESCRIPTS := $(shell git ls-files '*.applescript')
export HOMEBREW_NO_AUTO_UPDATE := 1

.PHONY: setup icons lint lint-applescript lint-data lint-md lint-actions check ci build clean release sync-plist link-live

setup:
	brew bundle --quiet

icons:
	icon-symbol.sh --batch tools/icons.txt --outdir icons --fg "#FFFFFF" --size 256

lint: lint-applescript lint-data lint-md lint-actions

lint-applescript:
ifdef CI
	@echo "lint-applescript: skipped in CI, compiling needs the target app installed"
else
	@mkdir -p $(BUILD)
	$(foreach script,$(APPLESCRIPTS),osacompile -o $(BUILD)/lint.scpt $(script) &&) rm -f $(BUILD)/lint.scpt
endif

lint-data:
	plutil -lint info.plist

lint-md:
	markdownlint-cli2 "**/*.md"

lint-actions:
	actionlint

check: lint

ci: check

build: clean check
	mkdir -p $(BUILD)/scripts
	cp info.plist $(BUILD)/
	cp icon.png $(BUILD)/
	cp -R icons $(BUILD)/
	cp scripts/*.applescript $(BUILD)/scripts/
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
	rm -rf "$(WORKFLOW_DIR)/scripts"
	ln -sfn "$(CURDIR)/scripts" "$(WORKFLOW_DIR)/scripts"
	ln -sfn "$(CURDIR)/icons" "$(WORKFLOW_DIR)/icons"
	ln -sfn "$(CURDIR)/icon.png" "$(WORKFLOW_DIR)/icon.png"
	@echo "linked $(WORKFLOW_DIR) to this repo"
