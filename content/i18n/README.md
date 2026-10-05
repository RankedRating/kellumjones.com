# Translation guide

The site is written in English. Each other language has one file here, `<code>.json`, that maps every piece of English text on the site to its translation. `_english.json` is the list of English text to translate (the value beside each entry is the page where it first appears). It is rewritten by `python3 build.py --strings`.

`python3 build.py --check` lists, for each language, any English text that has no translation yet. Untranslated text is shown in English on the site.

Posts are translated as whole files: `content/posts/<code>/<same file name>.md`, with the same header fields (`title`, `summary`, `standfirst`) translated.

## What the site is

The personal website of Kellum Jones, an American double bassist and teacher based in Columbus, Georgia, USA. He is a student building a solo career. The site has a biography, a list of performances, a teaching page, a blog ("Writing"), a page for his duo with the pianist Hsin Yeh (Understory Duo), and a contact page.

## Voice

Plain, warm and direct. No sales language, no exclamation marks, no flourishes that are not in the English. Biography and duo pages are in the third person. Teaching and contact pages are in the first person ("I teach...").

Translate the meaning faithfully. Do not add, drop or embellish. Buttons and menu items must stay short.

## Rules for the files

- Keep every key exactly as it is in `_english.json`, and give every key a value.
- Keep the markers `{n}`, `{name}` and `{time}` in the translation; the site fills them in.
- Anything in `[square brackets]` is a note to Kellum, not site text. Leave it exactly as it is, in English, even inside a translated sentence.
- A value may equal the English when that is correct (a name, for example).
- "I reply within {time}." is only a fallback. The length of time is ordinary words, so the sentence Kellum actually uses ("I reply within a few days.") has its own entry, translated whole.

## Names

Keep in Latin letters, unchanged: Kellum Jones, Hsin Yeh, Understory Duo, Schwob School of Music, LaGrange Youth Symphony Orchestra, Dr. Luca Lombardi, Ludwig Streicher, Studio Theatre, RiverCenter. Do not guess native-script spellings for Kellum Jones or Hsin Yeh.

In Hsin Yeh's biography, also keep in Latin letters, unchanged: Pan-An Chen, Joanna Ting, Esther Park, Alexei Volodin, Allison Franzetti, InterHarmony International Music Festival, Living Grace Church, Schwob Concerto Competition, and Music Teachers National Association (MTNA). Do not guess native-script spellings for the people. Translate the titles (Professor, Dr.) the way the language does for teachers. Kaohsiung and Taiwan take the language's own form. Her two schools in Taiwan, National Feng-Hsin High School and the University of Taipei, stay in English in every language except Chinese, where they take their own names: 國立鳳新高級中學 and 臺北市立大學 (Simplified: 国立凤新高级中学 and 台北市立大学). The MTNA competition has a state round; hers was the round for the US state of Georgia. A collaborative pianist is one who plays with other musicians (what used to be called an accompanist).

Use the language's own usual form for: place names (Columbus, Georgia is the US state, not the country), the Milan Conservatory, and composers (Reinhold Glière). The soloist Mikyung Sung is written 성미경 in Korean and stays in Latin letters, Mikyung Sung, in every other language. Hsin Yeh and Mikyung Sung are both women.

## Register

| Language | Address the reader as |
| --- | --- |
| Spanish (`es`), neutral international Spanish | tú |
| German (`de`) | Sie |
| French (`fr`) | vous |
| Italian (`it`) | tu |
| Portuguese (`pt`), Brazilian | você |
| Japanese (`ja`) | です・ます |
| Korean (`ko`) | polite formal (합니다 / 습니다) |
| Traditional Chinese (`zh-hant`), Taiwan usage | 你, polite |
| Simplified Chinese (`zh-hans`), Mainland usage | 你, polite |

## Terms

Use the term working bassists and teachers use in the language, and use it the same way everywhere.

- **double bass**: the instrument.
- **German bow**: the bow held underhand, as opposed to the French bow. A type of bow and bow hold, not a nationality.
- **bow hold**: how the hand holds the bow.
- **Viennese tradition** (of Ludwig Streicher): a school of bass playing.
- **shifting**: the left hand changing position along the fingerboard.
- **hand frame**: the shape of the left hand.
- **contact point**: where the bow meets the string.
- **string crossings**: moving the bow from one string to another.
- **commission new work**: pay a composer to write a new piece.
- **presenters**: people and organizations who put on concerts.
- **booking**: engaging Kellum for a concert.
- **understory**: the layer of new growth beneath the canopy of a forest. The duo's name stays "Understory Duo", but the sentence that explains the name must use the language's own word for this forest layer so the explanation makes sense. Add the English word once in brackets after it, for example "sous-bois (« understory » en anglais)", so the reader can connect the explanation to the name. This is the one place where a short addition is wanted.
- **Practice lab**, **The German bow**, **New music**: the three blog topics. **From the notebook** and **Notes from the practice room** are headings for the blog.
- **Landscape / Portrait**: photo orientation. **dark backdrop / grey backdrop**: the studio background.
- **Where / Who / Length / Rates**: labels for lesson details (location, who lessons are for, lesson length, prices).
- **Home**: the home page, in the menu. **Main** and **Pages**: labels read aloud by screen readers for the main menu and the list of page links.
- **Free admission**: no charge to attend.
