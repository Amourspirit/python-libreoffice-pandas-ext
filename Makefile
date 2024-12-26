help:
	@echo "Run make build to compile into 'build' folder."
	@echo "Run make diff to write 'changes_since_last_commit.diff into' into 'tmp' folder."

.PHONY: build diff help

build:
	uv run --no-config --link-mode=copy make.py build

create_build_dir:
	mkdir -p tmp

diff: create_build_dir
	git diff > ./tmp/changes_since_last_commit.diff