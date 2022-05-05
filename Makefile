.PHONY: archive archive_directory archlinux check clean directory push spec spec-html tests version
.DEFAULT_GOAL := archlinux

PROJECT := ahriman

FILES := AUTHORS COPYING README.md docs package src setup.py tox.ini web.png
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

push: spec archlinux
	git add package/archlinux/PKGBUILD src/ahriman/version.py docs/ahriman-architecture.svg docs/ahriman.1
	git commit -m "Release $(VERSION)"
	git tag "$(VERSION)"
	git push
	git push --tags

spec:
	# make sure that old files are removed
	find docs -type f -name "$(PROJECT)*.rst" -delete
	rm -f docs/modules.rst
	tox -e docs

spec-html: spec
	rm -rf docs/html
	tox -e docs-html

tests: clean
	tox -e tests

version:
ifndef VERSION
	$(error VERSION is required, but not set)
endif
	sed -i '/__version__ = .*/s/[^"][^)]*/__version__ = "$(VERSION)"/' src/ahriman/version.py
