#!/usr/bin/env python3
"""Build course homes and material indexes from course.yml."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

TEXT = {
    "ru": {
        "pending": "Готовится", "language": "Русский", "slides": "Слайды",
        "book": "Книга", "map": "Карточка курса", "program": "Программа курса",
        "materials": "Материалы", "home": "Курс", "other": "English",
        "state": "Лекции и книга готовятся. Учебные материалы ещё не опубликованы.",
        "prerequisite": "Основа —", "prerequisite_link": "статистический курс DN",
        "format": "План: 16 лекций по 90 минут, шесть вычислительных практикумов и итоговый проект.",
        "additional": "Задачи, код, ноутбуки и данные будут добавляться вместе с готовыми лекциями.",
        "book_state": "Книга готовится. Главы ещё не опубликованы.",
    },
    "en": {
        "pending": "In preparation", "language": "English", "slides": "Slides",
        "book": "Book", "map": "Course card", "program": "Course outline",
        "materials": "Materials", "home": "Course", "other": "Русский",
        "state": "The lectures and book are in preparation. Teaching materials have not yet been published.",
        "prerequisite": "The course builds on", "prerequisite_link": "DN's course in statistical data analysis",
        "format": "Plan: 16 lectures of 90 minutes, six computational practicals and a final project.",
        "additional": "Problems, code, notebooks and data will accompany the completed lectures.",
        "book_state": "The book is in preparation. No chapters have been published yet.",
    },
}


def front(title: str, lang: str, *, slides: bool = False) -> str:
    options = {"title": title, "lang": lang, "format": "html", "toc": False}
    if slides:
        options["format"] = {"html": {
            "theme": "cosmo",
            "css": [f"assets/site/{name}" for name in (
                "neutrinohit-tokens.css", "neutrinohit-base.css", "neutrinohit-components.css",
                "neutrinohit-projects.css")] + ["shared/styles/course.css"],
            "include-after-body": "shared/html/cloudflare-web-analytics.html",
        }}
    return yaml.safe_dump(options, allow_unicode=True, sort_keys=False)


def cards(course: dict, lang: str) -> str:
    out = ['<div class="course-card-grid">']
    for lecture in course["lectures"]:
        title = html.escape(lecture["title"][lang])
        out.append(f'<article class="course-card is-planned"><span class="course-card-status">'
                   f'{lecture["n"]:02d} · {TEXT[lang]["pending"]}</span><h3>{title}</h3></article>')
    return "\n".join(out + ["</div>"])


def home(course: dict, lang: str, *, slides: bool = False) -> str:
    t = TEXT[lang]
    other = "en" if lang == "ru" else "ru"
    title = course["title"][lang]
    page_title = f'{title}: {t["slides"]}' if slides else title
    up = "../" if slides else ""
    other_href = f"../../{other}/slides/index.html" if slides else f"../{other}/index.html"
    slide_link = f'<a href="{up}index.html">{t["home"]}</a>' if slides else f'<a href="slides/index.html">{t["slides"]}</a>'
    return f'''---
{front(page_title, lang, slides=slides)}---

```{{=html}}
<div class="course-index">
  <section class="course-intro">
    <p class="course-kicker">{t["pending"]} · {t["language"]}</p>
    <h1>{html.escape(page_title)}</h1>
    <p>{html.escape(course["summary"][lang])}</p>
    <div class="course-links">
      <a href="https://neutrinohit.github.io/">NeutrinoHit</a>
      <a href="https://neutrinohit.github.io/{lang}/courses/global-analysis.html">{t["map"]}</a>
      {slide_link}
      <a href="{other_href}" lang="{other}">{t["other"]}</a>
    </div>
  </section>
  <p class="course-author-note"><a href="https://neutrinohit.github.io/{lang}/index.html">DN · NeutrinoHit</a></p>
  <p>{t["state"]}</p>
  <p>{t["format"]}</p>
  <p>{t["prerequisite"]} <a href="https://neutrinohit.github.io/{lang}/courses/statistical-analysis.html">{t["prerequisite_link"]}</a>.</p>
  <h2 class="course-section-title">{t["program"]}</h2>
  {cards(course, lang)}
  <h2 class="course-section-title">{t["materials"]}</h2>
  <div class="course-material-grid">
    <section class="course-material"><h3>{t["book"]}</h3><p>{t["book_state"]}</p></section>
    <section class="course-material"><p>{t["additional"]}</p></section>
  </div>
</div>
```
'''


def pages(course: dict) -> dict[Path, str]:
    outputs = {}
    outputs[ROOT / "index.qmd"] = '''---
title: "Глобальный анализ данных в физике / Global Data Analysis in Physics"
format: html
toc: false
---

::: {.course-index}
::: {.course-intro}
# Глобальный анализ данных в физике

Global Data Analysis in Physics

Готовится · In preparation
:::

```{=html}
<div class="language-choice-grid">
  <a class="language-choice-card" href="ru/index.html" lang="ru"><strong>Русский</strong><span>Программа курса · слайды и книга готовятся</span></a>
  <a class="language-choice-card" href="en/index.html" lang="en"><strong>English</strong><span>Course outline · slides and book in preparation</span></a>
</div>
```

[NeutrinoHit](https://neutrinohit.github.io/)
:::
'''
    for lang in TEXT:
        outputs[ROOT / lang / "index.qmd"] = home(course, lang)
        outputs[ROOT / lang / "slides/index.qmd"] = home(course, lang, slides=True)
        outputs[ROOT / lang / "book/index.qmd"] = (
            f'# {course["title"][lang]} {{.unnumbered}}\n\n'
            f'{TEXT[lang]["book_state"]}\n\n'
            f'[{TEXT[lang]["home"]}](https://neutrinohit.github.io/global-analysis-course/{lang}/)\n')
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report stale pages without changing them")
    args = parser.parse_args()
    course = yaml.safe_load((ROOT / "course.yml").read_text(encoding="utf-8"))
    stale = []
    for path, content in pages(course).items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if args.check and stale:
        raise SystemExit("Stale course pages: " + ", ".join(stale))
    print(f'{len(stale)} page(s) {"stale" if args.check else "updated"}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
