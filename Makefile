.PHONY: architecture archive archive_directory archlinux check clean directory man push tests version
.DEFAULT_GOAL := archlinux

PROJECT := ahriman

FILES := AUTHORS COPYING README.md docs package src setup.cfg setup.py
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
	sed -i "s/pkgver=[0-9.]*/pkgver=$(VERSION)/" package/archlinux/PKGBUILD

check: clean mypy
	autopep8 --exit-code --max-line-length 120 -aa -i -j 0 -r "src/$(PROJECT)" "tests/$(PROJECT)"
	pylint --rcfile=.pylintrc "src/$(PROJECT)"
	bandit -c .bandit.yml -r "src/$(PROJECT)"
	bandit -c .bandit-test.yml -r "tests/$(PROJECT)"

clean:
	find . -type f -name "$(PROJECT)-*-src.tar.xz" -delete
	rm -rf "$(PROJECT)"

directory: clean
	mkdir "$(PROJECT)"

man:
	cd src &&  PYTHONPATH=. argparse-manpage --module ahriman.application.ahriman --function _parser --author "ahriman team" --project-name ahriman --author-email "" --url https://github.com/arcan1s/ahriman --output ../docs/ahriman.1

mypy:
	cd src && mypy --implicit-reexport --strict -p "$(PROJECT)" --install-types --non-interactive || true
	cd src && mypy --implicit-reexport --strict -p "$(PROJECT)"

push: architecture man archlinux
	git add package/archlinux/PKGBUILD src/ahriman/version.py docs/ahriman-architecture.svg docs/ahriman.1
	git commit -m "Release $(VERSION)"
	git tag "$(VERSION)"
	git push
	git push --tags

tests: clean
	python setup.py test

version:
ifndef VERSION
	$(error VERSION is required, but not set)
endif
	sed -i '/__version__ = "[0-9.]*/s/[^"][^)]*/__version__ = "$(VERSION)"/' src/ahriman/version.py
