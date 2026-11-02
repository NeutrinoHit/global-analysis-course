.DEFAULT_GOAL := help

QUARTO ?= quarto
PYTHON ?= $(shell pyenv which python 2>/dev/null || command -v python3)
export QUARTO_PYTHON := $(PYTHON)

.PHONY: help ci-setup pages site home ru-slides en-slides ru-html en-html ru-pdf en-pdf ru-epub en-epub sync-shared check-shared clean

help: ## Показать цели сборки
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

ci-setup: ## Установить зависимости сайта; TeX не требуется
	$(PYTHON) -m pip install -r requirements.txt

pages: ## Обновить страницы по course.yml
	$(PYTHON) scripts/build_course_pages.py

site: pages ## Собрать сайт курса и индексы слайдов RU/EN
	rm -rf _site
	$(QUARTO) render
	$(MAKE) ru-slides en-slides
	test -s _site/index.html
	test -s _site/ru/index.html
	test -s _site/en/index.html
	test -s _site/ru/slides/index.html
	test -s _site/en/slides/index.html
	test ! -e _site/ru/book
	test ! -e _site/en/book
	test -z "$$(find _site -type d -name planned -print -quit)"

home: pages ## Собрать главные страницы курса
	$(QUARTO) render

ru-slides: pages ## Собрать русский индекс HTML и готовые лекции RevealJS

en-slides: pages ## Собрать английский индекс HTML и готовые лекции RevealJS

ru-slides en-slides:
	$(QUARTO) render $(@:-slides=)/slides

ru-html: pages ## Собрать локальную русскую HTML-книгу в _book/ru
	$(QUARTO) render ru/book --to html

en-html: pages ## Собрать локальную английскую HTML-книгу в _book/en
	$(QUARTO) render en/book --to html

ru-pdf: pages ## Собрать локальную русскую PDF-книгу
	$(QUARTO) render ru/book --to pdf

en-pdf: pages ## Собрать локальную английскую PDF-книгу
	$(QUARTO) render en/book --to pdf

ru-epub: pages ## Собрать локальную русскую EPUB-книгу
	$(QUARTO) render ru/book --to epub

en-epub: pages ## Собрать локальную английскую EPUB-книгу
	$(QUARTO) render en/book --to epub

sync-shared: ## Обновить канонические стили и компоненты из neutrinohit-map
	$(PYTHON) scripts/sync_shared_assets.py
	$(PYTHON) ../neutrinohit-map/scripts/nh_media.py extension .

check-shared: ## Проверить соответствие каноническим стилям
	$(PYTHON) scripts/sync_shared_assets.py --check

clean: ## Удалить результаты сборки
	rm -rf _site _book .quarto ru/slides/.quarto en/slides/.quarto ru/book/.quarto en/book/.quarto
