# kellumjones.com

The website of Kellum Jones, double bassist. A small static site: plain HTML, one stylesheet, one short script, no framework.

## How it works

`build.py` reads the files in `content/` and `assets/` and writes the finished site into `public/`. The `public/` folder is what gets published. It is rewritten on every build, so never edit it by hand.

```
python3 build.py            # build the site into public/
python3 build.py --check    # build, then list every [placeholder] and every missing translation
```

Every build also follows each link on the finished site and prints a warning if one leads nowhere.

The build needs Python 3 and one package: `pip install -r requirements.txt`.

To look at the site on your own computer after building:

```
cd public && python3 -m http.server 8000
```

then open http://localhost:8000.

## What lives where

| Path | What it holds |
| --- | --- |
| `content/site.json` | Email, YouTube and Instagram links, photographer credit, press kit link, the signup text, form addresses |
| `content/performances.json` | Upcoming performances, past performances, videos |
| `content/posts/` | One Markdown file per post |
| `assets/images/` | Photos as shown on the pages (about 1600 pixels on the long side) |
| `assets/images/press/` | Larger copies offered as downloads on the Biography page and packed into the press kit |
| `assets/css/site.css` | Fonts, page basics, the menu, and the styles for post text |
| `assets/js/site.js` | Menu behavior and the contact form hand-off. The site works without it |
| `build.py` | The page templates and the fixed text of each page (biography, teaching, duo, contact) |
| `i18n.py` | Turns each English page into the other nine languages |
| `content/i18n/` | One translation file per language, plus the translators' guide |
| `public/` | The finished site |

## Writing a post

Add a file to `content/posts/`. The name starts with a number, then the address of the post:

```
05-my-new-post.md   ->   kellumjones.com/writing/my-new-post/
```

The file starts with a short header between two `---` lines, then the post in Markdown:

```
---
title: My new post
topic: Practice lab
date: 2026-11-02
summary: One sentence shown in lists and in search results.
standfirst: One sentence shown large under the title.
sources:
- [A book or article](https://example.com)
---

First paragraph.

## A subheading

> A sentence to pull out and set large.
```

- `topic` is one of: The German bow, Practice lab, New music. To add a topic, add it to `TOPICS` near the top of `build.py`.
- Posts are listed newest first by `date`. If any post has no date, they are ordered by the number at the start of the file name instead (highest first).
- Add `draft: true` to the header to keep a post off the site.

Then run `python3 build.py` and publish (below).

## Adding a performance

Edit `content/performances.json`. Dates are written year-month-day.

```json
{
  "upcoming": [
    {"date": "2026-11-14", "composer": "Giovanni Bottesini", "work": "Concerto No. 2 in B minor",
     "with": "Hsin Yeh, piano", "venue": "Legacy Hall, Columbus", "time": "7:30 pm",
     "admission": "Free admission", "link": "https://example.com/tickets"}
  ],
  "past": [
    {"date": "2026-03-02", "composer": "J.S. Bach", "work": "Suite No. 3", "venue": "Studio Theatre, Columbus"}
  ],
  "videos": [
    {"youtube_id": "abc123XYZ", "title": "Bottesini: Elegy", "caption": "Recorded in Columbus, 2026"}
  ]
}
```

`time`, `with`, `admission` and `link` are optional; leave any of them out and the row simply omits it. The home page shows the next two upcoming performances. The "Watch and listen" section and every YouTube link stay off the site until `youtube` is set in `content/site.json` or a video is added here; after that they appear on the next build. The first video is shown large. When a list is empty the page shows bracketed placeholders, so the layout can be judged before the real dates exist. When a performance has happened, move it from `upcoming` to `past`.

## Adding a commission

The Understory Duo page has a Commissions section that stays hidden while the list is empty. To show it, add the first piece to `commissions` in `content/performances.json`:

```json
"commissions": [
  {"year": 2027, "composer": "Composer's name", "work": "Title of the piece", "premiere": "Premiere: venue, city"}
]
```

## Languages

The site is written in English and published in ten languages: English at the root, and Spanish, German, French, Italian, Portuguese, Japanese, Korean, Traditional Chinese and Simplified Chinese under `/es/`, `/de/`, `/fr/`, `/it/`, `/pt/`, `/ja/`, `/ko/`, `/zh-hant/` and `/zh-hans/`. Every page links to itself in each language from the globe in the header, the menu and the footer. An "Other languages" link sends the page through Google's automatic translation for anyone else.

A visitor whose browser is set to one of the nine other languages is offered that language once, on a small card at the bottom of the page ("Read this page in ..."). Nothing redirects by itself. Choosing a language, or closing the card, is remembered in that browser and the card does not come back.

How it works:

- `build.py` builds each page in English. `i18n.py` then makes the other nine versions by looking up every piece of text in `content/i18n/<code>.json`, rewriting dates and times in the language's own format, and pointing links at the same language.
- **Text with no translation stays in English** on the translated pages. `python3 build.py --check` lists what is missing for each language, so run it after changing any wording, adding a performance, or adding a post.
- To translate new text, add the English string and its translation to each `content/i18n/<code>.json`. `python3 build.py --strings` rewrites `content/i18n/_english.json`, the full list of English text in use. `content/i18n/README.md` is the guide for translators: voice, names, and the agreed musical terms.
- **Posts** are translated as whole files. Put the translated post at `content/posts/<code>/<same file name>.md` with `title`, `summary` and `standfirst` translated in its header. A post with no translated file is shown in English under a one-line notice in the reader's language.
- Anything in `[square brackets]` is never translated.
- `reply_time` in `content/site.json` completes the sentence "I reply within ... ." on the Contact page. "a few days" is already translated. For any other wording, add the whole sentence ("I reply within two days.") to each translation file; `--check` lists it until that is done.
- Each language also gets its own not-found page (`/es/404.html`), its own feed of posts (`/es/writing/feed.xml`) and its own biography sheet in the press kit. All three are made from the same translation files, so there is nothing extra to keep up.
- The sentence on the offer card and each language's name live in `LANGS` at the top of `i18n.py`.

The translations were written and then independently reviewed, but not by native speakers. Before relying on a language for something important, ask a native-speaking musician to read it.

## Publishing

The site is meant for Cloudflare Pages, connected to this repository:

- Production branch: `main`
- Framework preset: None
- Build command: leave empty
- Build output directory: `public`

With that set up, every push to `main` publishes whatever is in `public/`. So the routine is: edit, run `python3 build.py`, commit everything including `public/`, push.

## Before launch

Run `python3 build.py --check`. It lists every bracketed placeholder still on the site and every empty setting in `content/site.json`. The site is ready when that list is empty. The main items:

- [ ] Fill in `content/site.json`: email, YouTube, Instagram, photographer
- [ ] Set `newsletter_action` in `content/site.json` to the form address from the email newsletter service. Until then the signup form only leads to the contact page
- [ ] Read and correct the biography and short biography in `build.py` (they are drafts), and add the performance highlights
- [ ] Have Hsin read her biography on the Understory Duo page (`HSIN_BIO` near the top of `build.py`), in English and in Chinese
- [ ] Add real performances and videos
- [ ] Write the first posts and give them dates

The contact form opens the visitor's mail app with the message filled in. To have messages sent from the page instead, set `contact_form_action` in `content/site.json` to the address a form service gives you.

## Photos

Photos are lightly retouched (skin only) and saved at 86 dpi or less. Each photo exists twice: a page copy in `assets/images/` and a larger copy in `assets/images/press/`. To replace one, save the new file under the same name in both places and rebuild. Hsin's portrait on the Understory Duo page, `assets/images/hsin-yeh.jpg`, has a page copy only: the press folder is Kellum's press kit.

Photos are blended into the page in three ways, all in `assets/css/site.css`:

- The header band uses the color of the dark studio backdrop (`#081918`), and a photo that rises into the band fades into it along its top and sides (`.p-fade`).
- On a phone, the bottom of the home photo fades into the band that holds the name (`.d-hero-fade`).
- Photos with the grey backdrop keep crisp top and side edges and dissolve into the eggshell ground at the bottom (`.feather`).

## Press kit

Every build writes `public/press/kellum-jones-press-kit.zip`: both biographies as a text file in English, the same sheet in each of the nine other languages (in `biography-translations/`), plus everything in `assets/images/press/`. Unfinished biography paragraphs (the ones still in square brackets) are left out. To use a different file, set `press_kit` in `content/site.json` to its address.

## Design

Eggshell ground (`#f0ead6`), black ink (`#000807`), oxblood accent (`#6d1f2b` panels, `#7a2531` links and numerals). Cardo for display type, Jost for text. The line drawing of a German bow appears on the home header only; every other page has one small notation mark above its title. Layouts are slightly asymmetric on wide screens and stack into one column on phones.

## Fonts

Cardo by David J. Perry and Jost by Owen Earl, both under the SIL Open Font License. The Cardo files are subset to Latin characters.
