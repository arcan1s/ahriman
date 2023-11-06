.PHONY: archive archlinux check clean directory html release specification tests version
.DEFAULT_GOAL := archlinux

PROJECT := ahriman

FILES := AUTHORS CONTRIBUTING.md COPYING README.md SECURITY.md package pyproject.toml src web.png
TARGET_FILES := $(addprefix $(PROJECT)/, $(FILES))
IGNORE_FILES := package/archlinux src/.mypy_cache

$(TARGET_FILES) : $(addprefix $(PROJECT), %) : $(addprefix ., %) directory version
	@cp -rp $< $@

archive: archive_directory
	tar cJf "$(PROJECT)-$(VERSION)-src.tar.xz" "$(PROJECT)"
	rm -rf "$(PROJECT)"

archive_directory: $(TARGET_FILES)
	rm -fr $(addprefix $(PROJECT)/, $(IGNORE_FILES))
	find "$(PROJECT)" -type f -name "*.pyc" -delete
	find "$(PROJECT)" -depth -type d -name "__pycache__" -execdir rm -rf {} +
	find "$(PROJECT)" -depth -type d -name "*.egg-info" -execdir rm -rf {} +

archlinux: archive
	sed -i "s/pkgver=.*/pkgver=$(VERSION)/" package/archlinux/PKGBUILD

check: clean
	tox -e check

clean:
	find . -type f -name "$(PROJECT)-*-src.tar.xz" -delete
	rm -rf "$(PROJECT)"

directory: clean
	mkdir "$(PROJECT)"

html: specification
	rm -rf docs/html
	tox -e docs-html

release: specification archlinux
	git add package/archlinux/PKGBUILD src/ahriman/__init__.py docs/ahriman-architecture.svg package/share/man/man1/ahriman.1 package/share/bash-completion/completions/_ahriman package/share/zsh/site-functions/_ahriman
	git commit -m "Release $(VERSION)"
	git tag "$(VERSION)"
	git push
	git push --tags

specification:
	# make sure that old files are removed
	find docs -type f -name "$(PROJECT)*.rst" -delete
	tox -e docs

tests: clean
	tox -e tests

version:
ifndef VERSION
	$(error VERSION is required, but not set)
endif
	sed -i 's/^__version__ = .*/__version__ = "$(VERSION)"/' src/ahriman/__init__.py
