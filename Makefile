.PHONY: architecture archive archive_directory archlinux check clean directory docs docs-source man push tests version
.DEFAULT_GOAL := archlinux

PROJECT := ahriman

FILES := AUTHORS COPYING README.md docs package src setup.py tox.ini web.png
TARGET_FILES := $(addprefix $(PROJECT)/, $(FILES))
IGNORE_FILES := package/archlinux src/.mypy_cache

$(TARGET_FILES) : $(addprefix $(PROJECT), %) : $(addprefix ., %) directory version
	@cp -rp $< $@

architecture:
	cd src && pydeps ahriman -o ../docs/ahriman-architecture.svg --no-show --cluster

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
	find docs/source -type f -name "$(PROJECT)*.rst" -delete
	rm -rf docs/html docs/source/modules.rst

directory: clean
	mkdir "$(PROJECT)"

docs: docs-source
	sphinx-build -b html -a -j auto docs/source docs/html

docs-source: clean
	SPHINX_APIDOC_OPTIONS=members,no-undoc-members,show-inheritance sphinx-apidoc --force --private -o docs/source src

man:
	cd src &&  PYTHONPATH=. argparse-manpage --module ahriman.application.ahriman --function _parser --author "ahriman team" --project-name ahriman --author-email "" --url https://github.com/arcan1s/ahriman --output ../docs/ahriman.1

push: architecture docs-source man archlinux
	git add package/archlinux/PKGBUILD src/ahriman/version.py docs/ahriman-architecture.svg docs/ahriman.1
	git commit -m "Release $(VERSION)"
	git tag "$(VERSION)"
	git push
	git push --tags

tests: clean
	tox -e tests

version:
ifndef VERSION
	$(error VERSION is required, but not set)
endif
	sed -i '/__version__ = .*/s/[^"][^)]*/__version__ = "$(VERSION)"/' src/ahriman/version.py
