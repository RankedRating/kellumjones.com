"""Languages for kellumjones.com.

The site is written once, in English, by build.py. This module turns each finished English page
into the same page in another language:

  * every piece of visible text is looked up in content/i18n/<code>.json (English -> translation)
  * dates, times and counts are rewritten in the language's own format
  * links between pages are pointed at the same language
  * a post is replaced by its translated file, content/posts/<code>/<same file name>.md, when one exists

Text that has no translation yet is left in English and listed by `python3 build.py --check`.
Anything in [square brackets] is a note for Kellum, not site text, and is never translated.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

# code:  the folder in the address (kellumjones.com/<code>/) and the name of the translation file
# tag:   the language tag written into the page, which browsers use to pick fonts and hyphenation
# offer: "Read this page in <language>", in that language. Shown once to a visitor whose browser is set to it.
# reach: who search engines should send to this version, when that is wider than the tag
#        (the Portuguese is Brazilian, and is still the right version for every Portuguese reader)
LANGS = [
    {'code': 'en', 'tag': 'en', 'name': 'English', 'og': 'en_US', 'offer': 'Read this page in English'},
    {'code': 'es', 'tag': 'es', 'name': 'Español', 'og': 'es_ES', 'offer': 'Leer esta página en español'},
    {'code': 'de', 'tag': 'de', 'name': 'Deutsch', 'og': 'de_DE', 'offer': 'Diese Seite auf Deutsch lesen'},
    {'code': 'fr', 'tag': 'fr', 'name': 'Français', 'og': 'fr_FR', 'offer': 'Lire cette page en français'},
    {'code': 'it', 'tag': 'it', 'name': 'Italiano', 'og': 'it_IT', 'offer': 'Leggi questa pagina in italiano'},
    {'code': 'pt', 'tag': 'pt-BR', 'name': 'Português', 'og': 'pt_BR', 'offer': 'Ler esta página em português', 'reach': 'pt'},
    {'code': 'ru', 'tag': 'ru', 'name': 'Русский', 'og': 'ru_RU', 'offer': 'Читать эту страницу на русском'},
    {'code': 'ja', 'tag': 'ja', 'name': '日本語', 'og': 'ja_JP', 'offer': 'このページを日本語で読む'},
    {'code': 'ko', 'tag': 'ko', 'name': '한국어', 'og': 'ko_KR', 'offer': '이 페이지를 한국어로 보기'},
    {'code': 'zh-hant', 'tag': 'zh-Hant', 'name': '繁體中文', 'og': 'zh_TW', 'offer': '以繁體中文閱讀本頁'},
    {'code': 'zh-hans', 'tag': 'zh-Hans', 'name': '简体中文', 'og': 'zh_CN', 'offer': '用简体中文阅读本页'},
]
for _l in LANGS:
    _l.setdefault('reach', _l['tag'])
BY_CODE = {l['code']: l for l in LANGS}
CJK = {'ja', 'ko', 'zh-hant', 'zh-hans'}
# Cardo has no Chinese, Japanese or Korean letters, so display type falls back to a serif the reader's device already has.
CJK_SERIF = {
    'ja': "Cardo, 'Hiragino Mincho ProN', 'Yu Mincho', 'Noto Serif CJK JP', 'Noto Serif JP', serif",
    'ko': "Cardo, AppleMyungjo, 'Nanum Myeongjo', Batang, 'Noto Serif CJK KR', 'Noto Serif KR', serif",
    'zh-hant': "Cardo, 'Songti TC', PMingLiU, 'Noto Serif CJK TC', 'Noto Serif TC', serif",
    'zh-hans': "Cardo, 'Songti SC', SimSun, 'Noto Serif CJK SC', 'Noto Serif SC', serif",
}

# Addresses that are the same file for every language.
SHARED = ('/images/', '/fonts/', '/css/', '/js/', '/press/', '/favicon.svg')

# Names that stay as they are in every language.
KEEP = {
    'Kellum Jones', 'Kellum', 'Jones', 'Hsin Yeh', 'Understory Duo', 'Understory', 'Duo', 'Instagram', 'YouTube', 'tr',
} | {l['name'] for l in LANGS}

# Sentences with a changing part. The translation file gives each one once, with the same {marker}.
TEMPLATES = [
    '{n} minute read',
    '{n} posts',
    'Photo: {name}',
    'Free to use for press and concert programs. Please credit {name}.',
    'I reply within {time}.',
]
# Strings used by this module itself (not found on the English pages).
EXTRA = [
    'Language',
    'Other languages (automatic translation)',
    '1 post',
    'This post has not been translated yet. It is shown in English.',
    # text that appears once there is more than one post, or a performance has passed
    'All posts', 'Previous', 'Next', 'More writing', 'Past performances',
]

# ------------------------------------------------------------------ dates and times
EN_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS = {
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    'fr': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
    'it': ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'],
    'pt': ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'],
    # Russian months in the form used after a day number ("19 ноября")
    'ru': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'],
}


def full_date(code, y, m, d):
    """19 November 2026, written the way each language writes it."""
    if code in ('ja', 'zh-hant', 'zh-hans'):
        return f'{y}年{m}月{d}日'
    if code == 'ko':
        return f'{y}년 {m}월 {d}일'
    name = MONTHS[code][m - 1]
    if code == 'de':
        return f'{d}. {name} {y}'
    if code in ('es', 'pt'):
        return f'{d} de {name} de {y}'
    if code == 'fr':
        return f'{"1er" if d == 1 else d} {name} {y}'
    return f'{d} {name} {y}'                      # it


def month_year(code, y, m):
    if code in ('ja', 'zh-hant', 'zh-hans'):
        return f'{y}年{m}月'
    if code == 'ko':
        return f'{y}년 {m}월'
    name = MONTHS[code][m - 1]          # always shown under a day number, so Russian keeps the form used after a day
    return f'{name} de {y}' if code in ('es', 'pt') else f'{name} {y}'


def day_month(code, m, d):
    if code in ('ja', 'zh-hant', 'zh-hans'):
        return f'{m}月{d}日'
    if code == 'ko':
        return f'{m}월 {d}일'
    name = MONTHS[code][m - 1]
    if code == 'de':
        return f'{d}. {name}'
    if code in ('es', 'pt'):
        return f'{d} de {name}'
    if code == 'fr':
        return f'{"1er" if d == 1 else d} {name}'
    return f'{d} {name}'


def clock(code, hour12, minute, ampm):
    """5:00 pm, written the way each language writes it."""
    h24 = hour12 % 12 + (12 if ampm == 'pm' else 0)
    mm = f'{minute:02d}'
    if code == 'de':
        return f'{h24}:{mm} Uhr'
    if code == 'es':
        return f'{h24}:{mm} h'
    if code == 'fr':
        return f'{h24} h' if minute == 0 else f'{h24} h {mm}'
    if code == 'it':
        return f'ore {h24}:{mm}'
    if code == 'pt':
        return f'{h24}h' if minute == 0 else f'{h24}h{mm}'
    if code in ('ja', 'ru'):
        return f'{h24}:{mm}'
    if code == 'ko':
        half = '오전' if ampm == 'am' else '오후'
        return f'{half} {hour12}시' if minute == 0 else f'{half} {hour12}시 {minute}분'
    half = '上午' if ampm == 'am' else '下午'       # Chinese
    return f'{half} {hour12}:{mm}'


_MON = '|'.join(EN_MONTHS)
_ABBR = '|'.join(m[:3] for m in EN_MONTHS)
RE_FULL = re.compile(rf'^({_MON}) (\d{{1,2}}), (\d{{4}})$')
RE_MY = re.compile(rf'^({_ABBR}) (\d{{4}})$')
RE_DM = re.compile(rf'^({_ABBR}) (\d{{1,2}})$')
RE_TIME = re.compile(r'^(\d{1,2}):(\d{2})\s(am|pm)$')
RE_PLAIN = re.compile(r'^[\d\s.,:;·©/()\-–—+]*$')           # numbers and punctuation only
RE_NOTE = re.compile(r'^\[[^\[\]]*\]$')                      # a [note for Kellum]
RE_MOVEMENT = re.compile(r'^[IVX]+\. [A-Z][a-z]+(?: [a-z]+)*$')   # a numbered movement, I. Andante moderato: the same in every language
ABBR_INDEX = {m[:3]: i + 1 for i, m in enumerate(EN_MONTHS)}


def template_regex(key):
    pattern = re.escape(key)
    pattern = re.sub(r'\\\{n\\\}', r'(?P<n>\\d+)', pattern)
    pattern = re.sub(r'\\\{(name|time)\\\}', r'(?P<\1>.+?)', pattern)
    return re.compile('^' + pattern + '$')


TEMPLATE_RES = [(key, template_regex(key)) for key in TEMPLATES]


class Translator:
    """Turns English text into one language, remembering what it could not translate."""

    def __init__(self, code):
        self.code = code
        self.lang = BY_CODE[code]
        path = os.path.join(ROOT, 'content', 'i18n', f'{code}.json')
        self.catalog = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        self.missing = {}                                     # English text -> first page it was seen on
        self.page = ''

    def text(self, s):
        """Translate one piece of text. Unknown text comes back unchanged and is noted."""
        if '\x00' in s:                                        # held-back markup sits inside this text: translate around it
            return ''.join(part if part.startswith('\x00') else self.text(part) for part in re.split(r'(\x00\d+\x00)', s))
        core = s.strip().replace('\xa0', ' ')
        if not core:
            return s
        out = self._lookup(core)
        if '\xa0' in s and RE_TIME.match(core):               # keep a time on one line
            out = out.replace(' ', '\xa0')
        lead = s[:len(s) - len(s.lstrip())]
        tail = s[len(s.rstrip()):]
        return lead + out + tail

    def _lookup(self, core):
        if core in self.catalog and self.catalog[core]:
            return self.catalog[core]
        if core in KEEP or RE_PLAIN.match(core) or RE_NOTE.match(core) or RE_MOVEMENT.match(core) or '@' in core or core.startswith('©') or '%%' in core:
            return core
        if ' · ' in core:
            return ' · '.join(self._lookup(part) for part in core.split(' · '))
        if self.code == 'en' and (RE_FULL.match(core) or RE_MY.match(core) or RE_DM.match(core) or RE_TIME.match(core)):
            return core
        m = RE_FULL.match(core)
        if m:
            return full_date(self.code, int(m.group(3)), EN_MONTHS.index(m.group(1)) + 1, int(m.group(2)))
        m = RE_MY.match(core)
        if m:
            return month_year(self.code, int(m.group(2)), ABBR_INDEX[m.group(1)])
        m = RE_DM.match(core)
        if m:
            return day_month(self.code, ABBR_INDEX[m.group(1)], int(m.group(2)))
        m = RE_TIME.match(core)
        if m:
            return clock(self.code, int(m.group(1)), int(m.group(2)), m.group(3))
        for key, rx in TEMPLATE_RES:
            m = rx.match(core)
            if m:
                if 'time' in m.groupdict() and not RE_NOTE.match(m.group('time')):
                    # A length of time is ordinary words, and they change form inside a sentence in most
                    # languages, so the whole sentence needs its own translation. Until it has one, say so.
                    self.missing.setdefault(core, self.page)
                pattern = self.catalog.get(key)
                if not pattern:
                    self.missing.setdefault(key, self.page)
                    return core
                for name, value in m.groupdict().items():
                    pattern = pattern.replace('{' + name + '}', value)
                return pattern
        self.missing.setdefault(core, self.page)
        return core


# ------------------------------------------------------------------ rewriting a page
PROTECT = re.compile(r'<(script|style|svg)\b.*?</\1>|<!--notr-->.*?<!--/notr-->|<(\w+)\b[^>]*\btranslate="no"[^>]*>.*?</\2>', re.S)
TEXT_NODE = re.compile(r'>([^<>]+)<')
ATTRS = re.compile(r'\b(alt|aria-label|placeholder)="([^"]*)"')
META = re.compile(r'(<meta (?:name="description"|property="og:(?:title|description)") content=")([^"]*)(")')
HREF = re.compile(r'\b(href|action)="(/[^"#]*)')
HEADING = re.compile(r'<(h[1-3])\b([^>]*)>(.*?)</\1>', re.S)
HAS_CJK = re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\uff00-\uffef]')


def mark_latin_headings(doc):
    """On a Chinese, Japanese or Korean page, mark headings that are still in Latin letters (a name, the duo).
    They keep the tight line spacing drawn for Cardo; the taller spacing in site.css is for CJK characters."""
    def mark(m):
        if 'data-latin' in m.group(2) or HAS_CJK.search(re.sub(r'<[^>]+>', '', m.group(3))):
            return m.group(0)
        return f'<{m.group(1)}{m.group(2)} data-latin>{m.group(3)}</{m.group(1)}>'
    return HEADING.sub(mark, doc)


LANG_LINK = re.compile(r'<a\b[^>]*\bhreflang="[^>]*>')


def localise_links(doc, code):
    """Point the page's own links at the same language. Links to another language already say where they go."""
    def swap(m):
        path = m.group(2)
        if path.startswith(SHARED) or path.startswith(f'/{code}/'):
            return m.group(0)
        return f'{m.group(1)}="/{code}{path}'
    out, last = [], 0
    for m in LANG_LINK.finditer(doc):
        out.append(HREF.sub(swap, doc[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(HREF.sub(swap, doc[last:]))
    return ''.join(out)


def translate_page(doc, tr, page_path):
    """Return the English page `doc` in the translator's language."""
    tr.page = page_path
    kept = []

    def hold(m):
        kept.append(m.group(0))
        return f'\x00{len(kept) - 1}\x00'

    work = PROTECT.sub(hold, doc)
    work = TEXT_NODE.sub(lambda m: '>' + html.escape(tr.text(html.unescape(m.group(1))), quote=False) + '<', work)
    work = ATTRS.sub(lambda m: f'{m.group(1)}="{html.escape(tr.text(html.unescape(m.group(2))), quote=True)}"', work)
    work = META.sub(lambda m: m.group(1) + html.escape(tr.text(html.unescape(m.group(2))), quote=True) + m.group(3), work)
    work = re.sub(r'\x00(\d+)\x00', lambda m: kept[int(m.group(1))], work)
    work = localise_links(work, tr.code)
    if tr.code in CJK:
        work = work.replace('font-style: italic', 'font-style: normal')      # slanted CJK text is hard to read
        work = work.replace('font-family: Cardo, Georgia, serif', 'font-family: ' + CJK_SERIF[tr.code])
        work = mark_latin_headings(work)
    return work


def collect_strings(pages):
    """Every English string the pages use, with the page it first appears on. For building the translation files."""
    probe = Translator('en')
    probe.catalog = {}
    for path, doc in pages:
        translate_page(doc, probe, path)
    found = dict(probe.missing)
    for key in TEMPLATES + EXTRA:
        found.setdefault(key, '(used on several pages)')
    return found
