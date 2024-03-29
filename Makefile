VERSION ?= 1.0.0
REPO_URL = https://github.com/kotazzz/krpg

all: build changelog release push

build:
	python tools.py version $(VERSION)
	black .
	python tools.py hashes
	python tools.py version --show

changelog:
	head -n 7 CHANGELOG.md > TEMP_CHANGELOG.md
	echo "## [$(VERSION)] - $(shell date +%Y-%m-%d)" >> TEMP_CHANGELOG.md
	echo "" >> TEMP_CHANGELOG.md
	echo "[$(VERSION)]: $(REPO_URL)/compare/$(shell git describe --abbrev=0 --tags `git rev-list --tags --skip=0 --max-count=1`)...$(VERSION)" >> TEMP_CHANGELOG.md
	echo "" >> TEMP_CHANGELOG.md
	tail -n +10 CHANGELOG.md >> TEMP_CHANGELOG.md
	mv TEMP_CHANGELOG.md CHANGELOG.md
	
release:
	git commit -am "Release version $(VERSION)"
	git tag -a $(VERSION) -m "$(VERSION)"


push:
	git push origin master --tags

