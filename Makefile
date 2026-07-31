DIST := dist
NAME := 2Do.alfredworkflow
BUILD := $(DIST)/.build

.PHONY: build clean release sync-plist

build: clean
	mkdir -p $(BUILD)/scripts
	cp info.plist $(BUILD)/
	cp icon.png $(BUILD)/
	cp scripts/*.applescript $(BUILD)/scripts/
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
