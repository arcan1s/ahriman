.PHONY: archive archive_directory archlinux check clean directory push tests version
.DEFAULT_GOAL := archlinux

PROJECT := ahriman

FILES := AUTHORS COPYING CONFIGURING.md README.md package src setup.py
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
	sed -i "s/pkgver=[0-9.]*/pkgver=$(VERSION)/" package/archlinux/PKGBUILD

check: clean mypy
	find "src/$(PROJECT)" "tests/$(PROJECT)" -name "*.py" -execdir autopep8 --exit-code --max-line-length 120 -aa -i {} +
	cd src && pylint --rcfile=../.pylintrc "$(PROJECT)"
	cd src && bandit -c ../.bandit.yml -r "$(PROJECT)"
	cd tests && bandit -c ../.bandit-test.yml -r "$(PROJECT)"

clean:
	find . -type f -name "$(PROJECT)-*-src.tar.xz" -delete
	rm -rf "$(PROJECT)"

directory: clean
	mkdir "$(PROJECT)"

mypy:
	cd src && echo y | mypy --implicit-reexport --strict -p "$(PROJECT)" --install-types || true
	cd src && mypy --implicit-reexport --strict -p "$(PROJECT)"

push: archlinux
	git add package/archlinux/PKGBUILD src/ahriman/version.py
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
