#!/usr/bin/env python3
"""Build kellumjones.com.

    python3 build.py            # writes the finished site into public/
    python3 build.py --check    # same, then lists every [placeholder] still on the site

What lives where:
    content/site.json           email, social links, photographer credit, form addresses
    content/performances.json   upcoming and past performances, videos
    content/posts/*.md          one Markdown file per post (see README.md)
    assets/                     stylesheet, script, fonts, images (copied as they are)
    build.py                    this file: the page templates and their fixed text
    public/                     the finished site. Never edit by hand; it is rewritten on every build.
"""
import datetime
import html
import json
import os
import re
import shutil
import sys

import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')
SITE = json.load(open(os.path.join(ROOT, 'content', 'site.json'), encoding='utf-8'))
PERF = json.load(open(os.path.join(ROOT, 'content', 'performances.json'), encoding='utf-8'))
BASE = SITE.get('base_url', '').rstrip('/')
YEAR = datetime.date.today().year

# ------------------------------------------------------------------ design constants
EGG, INK, MUTED, HAIR, CTL = '#f0ead6', '#000807', '#5c584b', '#b7b09a', '#857f6b'
OX, OXINK, RED, FOOT, BACKDROP, RAISED, FIELDBG = '#6d1f2b', '#7a2531', '#b4505c', '#e6dfc8', '#081918', '#e6dfc8', '#faf7ec'

PAD = 'clamp(16px, 2.5cqw, 32px)'
SERIF = 'Cardo, Georgia, serif'
WRAP = 'box-sizing: border-box; width: 100%; max-width: 1280px; margin-left: auto; margin-right: auto'
SECPAD = f'padding: clamp(96px, 12.5cqw, 160px) {PAD} 0'
H2 = f'margin: 0; font-family: {SERIF}; font-size: clamp(40px, 4.4cqw, 56px); line-height: 1.08; font-weight: 400; letter-spacing: -0.01em'
H2S = f'margin: 0; font-family: {SERIF}; font-size: 32px; line-height: 38px; font-weight: 400'
H3 = f'margin: 0; font-family: {SERIF}; font-size: 28px; line-height: 34px; font-weight: 400'
LEAD = f'margin: 0; max-width: 640px; font-family: {SERIF}; font-size: clamp(26px, 2.5cqw, 32px); line-height: 1.3'
P = 'margin: 0; max-width: 600px'
META = f'font-size: 15px; line-height: 20px; font-weight: 500; color: {MUTED}'
LINK = 'display: inline-flex; align-items: center; min-height: 44px; font-size: 15px; line-height: 20px; font-weight: 500'
BTN = f'display: inline-flex; align-items: center; min-height: 48px; box-sizing: border-box; padding: 12px 24px; border: 0; border-radius: 3px; background: {INK}; color: {EGG}; text-decoration: none; font-family: inherit; font-size: 15px; line-height: 20px; font-weight: 500; cursor: pointer'
BTN_LIGHT = BTN.replace(f'background: {INK}; color: {EGG}', f'background: {EGG}; color: {INK}')
RULE = f'1px solid {HAIR}'
FIELD = f'min-height: 48px; box-sizing: border-box; width: 100%; padding: 12px 16px; border: 1px solid {CTL}; border-radius: 3px; background: {FIELDBG}; color: {INK}; font-family: inherit; font-size: 18px; line-height: 24px'
LABEL = 'font-size: 15px; line-height: 20px; font-weight: 500'
PANEL_PAD = f'padding: 56px clamp(16px, 3.75cqw, 48px) 56px max({PAD}, calc(50cqw - 608px))'
PANEL_PAD_R = f'padding: 56px max({PAD}, calc(50cqw - 608px)) 56px clamp(16px, 3.75cqw, 48px)'

URL = {
    'home': '/', 'bio': '/biography/', 'perf': '/performances/', 'teach': '/teaching/',
    'writing': '/writing/', 'duo': '/understory-duo/', 'contact': '/contact/',
}
PRESS = '/images/press/'   # the larger files offered as downloads
FADE = '<div class="p-fade" aria-hidden="true"></div>'   # melts the top of a rising photo into the header band
IMG = {
    'hero': '/images/kellum-jones-hero.jpg',
    'lean': '/images/kellum-jones-leaning-forward.jpg',
    'stand': '/images/kellum-jones-standing.jpg',
    'up': '/images/kellum-jones-standing-looking-up.jpg',
    'duo': '/images/understory-duo.jpg',
    'think': '/images/kellum-jones-thinking.jpg',
}
TOPICS = [
    ('The German bow', 'The hold, the sound, and why I chose it.'),
    ('Practice lab', 'Experiments on my own practice, with the results.'),
    ('New music', 'Commissions and pieces worth knowing.'),
]


def esc(text):
    return html.escape(text or '', quote=True)


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


# ------------------------------------------------------------------ biography text (used on the page and in the press kit)
BIO_LEAD = 'Kellum Jones is a double bassist based in Columbus, Georgia, building a career as a soloist and teacher.'
BIO_PARAS = [
    'He studies double bass performance at the Schwob School of Music with Dr. Luca Lombardi of the Milan Conservatory, and has taken summer lessons with the soloist Mikyung Sung. He plays the German bow in the Viennese tradition of Ludwig Streicher.',
    '[Performance highlights: two or three sentences on recitals, concerto appearances, competitions and festivals.]',
    'Kellum is on the double bass faculty of the LaGrange Youth Symphony Orchestra, where he teaches beginning and intermediate players, and he leads weekly sessions on technique and musicianship for students at Schwob.',
    'With the pianist Hsin Yeh he performs as Understory Duo, which commissions new work for double bass and piano from living composers. He writes about practice and the German bow in the notebook on this site.',
]
BIO_SHORT = 'Kellum Jones is a double bassist based in Columbus, Georgia. He studies at the Schwob School of Music with Dr. Luca Lombardi and plays the German bow in the Viennese tradition. He teaches on the double bass faculty of the LaGrange Youth Symphony Orchestra and performs with the pianist Hsin Yeh as Understory Duo, commissioning new work for double bass and piano from living composers.'
KIT_URL = '/press/kellum-jones-press-kit.zip'

# ------------------------------------------------------------------ site settings with placeholders
EMAIL = SITE.get('email', '').strip()
EMAIL_LABEL = esc(EMAIL) if EMAIL else '[your email address]'
EMAIL_HREF = f'mailto:{esc(EMAIL)}' if EMAIL else URL['contact']
YOUTUBE = esc(SITE.get('youtube', '').strip())      # empty until there is a channel: the YouTube links and the video section stay off the site
INSTAGRAM = esc(SITE.get('instagram', '').strip()) or URL['contact']
PRESS_KIT = esc(SITE.get('press_kit', '').strip()) or KIT_URL
PHOTOGRAPHER = esc(SITE.get('photographer', '').strip()) or '[photographer]'
REPLY_TIME = esc(SITE.get('reply_time', '').strip()) or '[a few days]'
NEWS_TEXT = esc(SITE.get('newsletter_text', '').strip()) or 'Posts on practice, the German bow and new music for bass.'
NEWS_ACTION = esc(SITE.get('newsletter_action', '').strip())
FORM_ACTION = esc(SITE.get('contact_form_action', '').strip())
HAS_VIDEO = bool(YOUTUBE or PERF.get('videos'))


def yt_link(style, label='YouTube'):
    """A link to the YouTube channel, or nothing while there is no channel."""
    return f'<a href="{YOUTUBE}" style="{style}">{label}</a>' if YOUTUBE else ''

# ------------------------------------------------------------------ drawings
BOW_G = """<g transform="matrix(0 1 1 0 10 0)">
<path d="M58 10 C250 30 380 46 470 46 S700 38 790 31 L915 21"></path>
<path d="M62 17 C250 38 380 55 470 56 S700 50 790 44 L915 33"></path>
<path d="M58 10 Q48 6 41 4 L2 31 L3 36 L50 47 Q52 28 62 17"></path>
<path d="M7 33 L49 43"></path>
<path stroke="#b7b09a" d="M47 45.5 L784 85 M49 47 L784 91"></path>
<path d="M689 36.5 L689 50.5 M694 36.2 L694 50.2 M699 35.9 L699 49.9 M704 35.6 L704 49.6 M709 35.3 L709 49.3 M714 35 L714 49 M719 34.7 L719 48.7 M724 34.4 L724 48.4 M729 34.1 L729 48.1 M734 33.8 L734 47.8 M739 33.5 L739 47.5 M744 33.2 L744 47.2 M749 32.9 L749 46.9 M754 32.6 L754 46.6"></path>
<path fill="#b4505c" stroke="#b4505c" d="M758 31.6 L784 30 L784 45.4 L758 47 Z"></path>
<path d="M794 45 L884 37 L870 92 Q869 94 866 94 L809 94 L809 82 L818 82 C836 80 846 70 842 62 C839 54 828 52 796 52 Z"></path>
<path d="M809 82 L784 83 L784 93 L809 94"></path>
<path d="M813 90 L866 90"></path>
<circle cx="858" cy="67" r="4"></circle>
<path d="M915 19.5 L990 13.5 Q1000 14 1000 20.5 Q1000 27.5 992 28.5 L915 34.5 Z"></path>
<path d="M922 19 L922 34 M928 18.5 L928 33.5"></path>
</g>"""


def _mark(w, h, body):
    return f'<svg aria-hidden="true" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" stroke="{RED}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="display: block">{body}</svg>'


# One small notation mark sits above each inner page title, like an articulation over a note.
MARKS = {
    'fermata': _mark(56, 36, f'<path d="M4 32 A24 24 0 0 1 52 32"></path><circle cx="28" cy="27" r="3" fill="{RED}" stroke="none"></circle>'),
    'bowing': _mark(76, 36, f'<path d="M6 32 V9 H30 V32"></path><rect x="6" y="6" width="24" height="5" fill="{RED}" stroke="none"></rect><path d="M46 8 L57 32 L68 8"></path>'),
    'tie': _mark(100, 36, '<ellipse cx="16" cy="26" rx="9.5" ry="6.5" transform="rotate(-20 16 26)"></ellipse><ellipse cx="84" cy="26" rx="9.5" ry="6.5" transform="rotate(-20 84 26)"></ellipse><path d="M17 13 C35 2 65 2 83 13"></path>'),
    'clef': _mark(46, 46, f'<circle cx="9" cy="17" r="3.5" fill="{RED}" stroke="none"></circle><path d="M9 17 C9 6 30 2 31 17 C32 29 20 39 6 43"></path><circle cx="40" cy="11" r="2.2" fill="{RED}" stroke="none"></circle><circle cx="40" cy="22" r="2.2" fill="{RED}" stroke="none"></circle>'),
    'segno': _mark(40, 44, f'<path d="M30 11 C30 4 14 2 12 12 C10 22 30 22 28 32 C26 42 10 40 10 33"></path><path d="M35 4 L5 40"></path><circle cx="8" cy="19" r="2.2" fill="{RED}" stroke="none"></circle><circle cx="32" cy="25" r="2.2" fill="{RED}" stroke="none"></circle>'),
    'trill': _mark(104, 36, f'<text x="0" y="29" font-family="Cardo, Georgia, serif" font-style="italic" font-size="34" fill="{RED}" stroke="none">tr</text><path d="M32 20 q5 -9 10 0 t10 0 t10 0 t10 0 t10 0 t10 0"></path>'),
}
# A final barline closes a post.
END_MARK = f'<svg aria-hidden="true" width="14" height="40" viewBox="0 0 14 40" fill="none" style="display: block"><rect x="0" y="0" width="1.5" height="40" fill="{OX}"></rect><rect x="6" y="0" width="6" height="40" fill="{OX}"></rect></svg>'
MENU_ICON = '<svg aria-hidden="true" width="32" height="20" viewBox="0 0 32 20" fill="none" stroke="currentColor" stroke-width="2"><line x1="0" y1="2" x2="32" y2="2"></line><line x1="0" y1="10" x2="32" y2="10"></line><line x1="0" y1="18" x2="32" y2="18"></line></svg>'
CLOSE_ICON = '<svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="2" y1="2" x2="22" y2="22"></line><line x1="22" y1="2" x2="2" y2="22"></line></svg>'
PLAY_ICON = '<svg aria-hidden="true" width="40" height="40" viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2"><circle cx="20" cy="20" r="18"></circle><path d="M16 12 L29 20 L16 28 Z"></path></svg>'

# ------------------------------------------------------------------ shared pieces
MENU_BUTTON = f'<a href="#menu" data-menu-open aria-label="Open menu" style="display: inline-flex; align-items: center; gap: 12px; min-height: 44px; padding: 0 4px; color: {EGG}; text-decoration: none; font-size: 15px; line-height: 20px; font-weight: 500"><span>Menu</span>{MENU_ICON}</a>'

TOPBAR = f"""<div style="position: relative; {WRAP}; padding: 22px {PAD} 0; display: flex; justify-content: space-between; align-items: center; gap: 16px">
<a href="{URL['home']}" style="display: inline-flex; align-items: center; min-height: 44px; color: {EGG}; text-decoration: none; font-family: {SERIF}; font-size: 26px; line-height: 32px">Kellum Jones</a>
{MENU_BUTTON}
</div>"""


def band(title_html, lede=None, mark=None):
    """The dark header band of an inner page: name, menu, one notation mark, the page title."""
    mark_html = MARKS[mark] + '\n' if mark else ''
    lede_html = f'\n<p style="margin: 0; max-width: 520px; font-family: {SERIF}; font-style: italic; font-size: 26px; line-height: 34px">{lede}</p>' if lede else ''
    return f"""<header id="top" class="p-band on-dark" style="position: relative; display: flex; flex-direction: column; background: {BACKDROP}; color: {EGG}; overflow: hidden">
{TOPBAR}
<div style="position: relative; {WRAP}; margin-top: auto; padding: 96px {PAD} 48px; display: flex; flex-direction: column; gap: 20px">
{mark_html}<h1 style="margin: 0; display: flex; flex-direction: column; font-family: {SERIF}; font-size: clamp(56px, 7.5cqw, 96px); line-height: 0.95; font-weight: 400; letter-spacing: -0.02em">{title_html}</h1>{lede_html}
</div>
</header>"""


BAR = f"""<header id="top" class="on-dark" style="background: {BACKDROP}; color: {EGG}; padding-bottom: 22px">
{TOPBAR}
</header>"""

FLINK = f'display: inline-flex; align-items: center; min-height: 44px; color: {EGG}; text-decoration: none; font-family: {SERIF}; font-size: 22px; line-height: 30px'
FOOTER = f"""<footer class="on-dark" style="margin-top: auto; padding-top: clamp(96px, 12.5cqw, 160px)">
<div style="background: {INK}; color: {EGG}">
<div style="{WRAP}; padding: 72px {PAD} 28px; display: flex; flex-direction: column; gap: 56px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 40px 64px">
<a href="{URL['home']}" style="display: flex; flex-direction: column; color: {EGG}; text-decoration: none; font-family: {SERIF}; font-size: clamp(64px, 8cqw, 104px); line-height: 0.92; letter-spacing: -0.02em">
<span>Kellum</span>
<span>Jones</span>
</a>
<nav aria-label="Pages" style="display: flex; gap: 0 clamp(32px, 6cqw, 80px)">
<div style="display: flex; flex-direction: column; align-items: flex-start">
<a href="{URL['bio']}" style="{FLINK}">Biography</a>
<a href="{URL['perf']}" style="{FLINK}">Performances</a>
<a href="{URL['teach']}" style="{FLINK}">Teaching</a>
</div>
<div style="display: flex; flex-direction: column; align-items: flex-start">
<a href="{URL['writing']}" style="{FLINK}">Writing</a>
<a href="{URL['duo']}" style="{FLINK}">Understory Duo</a>
<a href="{URL['contact']}" style="{FLINK}">Contact</a>
</div>
</nav>
</div>
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px 32px; padding-top: 16px; border-top: 1px solid #4a463b">
<div style="display: flex; flex-wrap: wrap; gap: 0 32px">
<a href="{EMAIL_HREF}" style="{LINK}; color: {FOOT}">{EMAIL_LABEL}</a>
{yt_link(f'{LINK}; color: {FOOT}')}
<a href="{INSTAGRAM}" style="{LINK}; color: {FOOT}">Instagram</a>
<a href="{PRESS_KIT}" style="{LINK}; color: {FOOT}">Download press kit</a>
</div>
<p style="margin: 0; font-size: 15px; line-height: 24px; color: {HAIR}">© {YEAR} Kellum Jones</p>
</div>
</div>
</div>
</footer>"""

_news_form_open = f'<form action="{NEWS_ACTION}" method="post"' if NEWS_ACTION else f'<form action="{URL["contact"]}" method="get"'
NEWSLETTER = f"""<section aria-label="Newsletter" style="padding-top: clamp(96px, 12.5cqw, 160px)">
<div class="h-news on-dark" style="box-sizing: border-box; background: {OX}; color: {EGG}; {PANEL_PAD}; display: flex; flex-wrap: wrap; gap: 32px; align-items: flex-end">
<div style="flex: 1 1 360px; display: flex; flex-direction: column; gap: 12px">
<h2 style="{H2S}">New writing by email</h2>
<p style="margin: 0; max-width: 480px">{NEWS_TEXT}</p>
</div>
{_news_form_open} style="flex: 1 1 360px; display: flex; flex-direction: column; gap: 12px">
<label for="n-email" style="{LABEL}">Email address</label>
<div style="display: flex; flex-wrap: wrap; gap: 16px">
<input id="n-email" name="email" type="email" autocomplete="email" required style="flex: 1 1 220px; min-height: 48px; box-sizing: border-box; padding: 12px 16px; border: 1px solid {EGG}; border-radius: 3px; background: {FIELDBG}; color: {INK}; font-family: inherit; font-size: 18px">
<button type="submit" class="btn" style="{BTN_LIGHT}">Subscribe</button>
</div>
</form>
</div>
</section>"""


def cta(heading, text, button, href=None):
    """The oxblood panel that closes a page with one thing to do."""
    return f"""<section aria-label="{esc(heading)}" style="padding-top: clamp(96px, 12.5cqw, 160px)">
<div class="h-news on-dark" style="box-sizing: border-box; background: {OX}; color: {EGG}; {PANEL_PAD}; display: flex; flex-wrap: wrap; gap: 32px; align-items: flex-end; justify-content: space-between">
<div style="flex: 1 1 360px; display: flex; flex-direction: column; gap: 12px">
<h2 style="{H2S}">{heading}</h2>
<p style="margin: 0; max-width: 520px">{text}</p>
</div>
<a href="{href or URL['contact']}" class="btn" style="{BTN_LIGHT}">{button}</a>
</div>
</section>"""


def split(left, right, lf='4 1 280px', rf='8 1 520px', sec_id=None, gap='40px 32px', first=False):
    """A heading column on the left and a wider content column on the right."""
    idattr = f' id="{sec_id}"' if sec_id else ''
    pad = f'padding: 96px {PAD} 0' if first else SECPAD
    return f"""<section{idattr} style="{WRAP}; {pad}; display: flex; flex-wrap: wrap; align-items: flex-start; gap: {gap}">
<div style="flex: {lf}; display: flex; flex-direction: column; gap: 16px; align-items: flex-start">
{left}
</div>
<div style="flex: {rf}; min-width: 0; display: flex; flex-direction: column">
{right}
</div>
</section>"""


def photo(src, alt, ratio, caption, pos='50% 50%', download=True, cls=''):
    # download: False for no link, True to offer the displayed file, or the path of a larger file
    target = download if isinstance(download, str) else src
    link = f'\n<a href="{target}" download style="{LINK}">Download</a>' if download else ''
    return f"""<figure style="margin: 0; display: flex; flex-direction: column; gap: 4px">
<img src="{src}" alt="{alt}" loading="lazy"{' class="' + cls + '"' if cls else ''} style="display: block; width: 100%; aspect-ratio: {ratio}; object-fit: cover; object-position: {pos}">
<figcaption style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0 24px; font-size: 15px; line-height: 22px; color: {MUTED}">
<span style="padding: 11px 0">{caption}</span>{link}
</figcaption>
</figure>"""


def video(item=None, label='[Video]', caption='[Composer: work title] · [where and when]'):
    """A video frame. With a YouTube id it links to the video over its thumbnail; without one it is a labelled placeholder."""
    frame = f'aspect-ratio: 16 / 9; box-sizing: border-box; padding: clamp(16px, 2cqw, 24px); display: flex; flex-direction: column; justify-content: space-between; background-color: {INK}; color: {EGG}'
    if item and item.get('youtube_id'):
        vid = esc(item['youtube_id'])
        inner = f"""<a href="https://www.youtube.com/watch?v={vid}" style="{frame}; background-image: linear-gradient(rgba(0,8,7,0.35), rgba(0,8,7,0.35)), url(https://i.ytimg.com/vi/{vid}/hqdefault.jpg); background-size: cover; background-position: center; text-decoration: none">
{PLAY_ICON}
<span style="font-size: 15px; line-height: 22px; font-weight: 500">{esc(item.get('title', 'Watch on YouTube'))}</span>
</a>"""
        caption = esc(item.get('caption', ''))
    else:
        inner = f"""<div style="{frame}">
{PLAY_ICON}
<span style="font-size: 15px; line-height: 22px; font-weight: 500; color: {FOOT}">{label}</span>
</div>"""
    return f"""<figure class="video on-dark" style="margin: 0; display: flex; flex-direction: column; gap: 12px">
{inner}
<figcaption style="font-size: 15px; line-height: 22px; color: {MUTED}">{caption}</figcaption>
</figure>"""


# ------------------------------------------------------------------ performances
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def parse_date(text):
    try:
        return datetime.date.fromisoformat((text or '').strip())
    except ValueError:
        return None


def long_date(d):
    return f'{MONTHS[d.month - 1]} {d.day}, {d.year}' if d else '[Date]'


def perf_row(item=None, last=False):
    bb = f'; border-bottom: {RULE}' if last else ''
    if item:
        d = parse_date(item.get('date'))
        day = str(d.day) if d else '00'
        month = f'{MONTHS[d.month - 1][:3]} {d.year}' if d else '[Month year]'
        composer, work = esc(item.get('composer')), esc(item.get('work'))
        with_ = esc(item.get('with'))
        where = ' · '.join(x for x in [esc(item.get('venue')), esc(item.get('time')).replace(' ', '&nbsp;')] if x)   # the time never breaks across lines
        link = f'<a href="{esc(item["link"])}" style="{LINK}">Tickets and details</a>' if item.get('link') else ''
        if item.get('admission'):        # for example "Free admission"; shown above the ticket link, or in its place
            link = f'<span style="font-size: 15px; line-height: 24px; font-weight: 500">{esc(item["admission"])}</span>' + ('\n' + link if link else '')
    else:
        day, month, composer, work = '00', '[Month year]', '[Composer]', '[Work title]'
        with_, where = '[With: pianist, orchestra or ensemble]', '[Venue, city · time]'
        link = f'<a href="{URL["perf"]}" style="{LINK}">Tickets and details</a>'
    with_html = f'\n<span style="font-size: 15px; line-height: 24px; color: {MUTED}">{with_}</span>' if with_ else ''
    return f"""<div style="display: flex; flex-wrap: wrap; gap: 16px 32px; padding: 32px 0; border-top: {RULE}{bb}">
<div style="flex: 0 0 136px; display: flex; flex-direction: column; gap: 4px">
<span style="font-family: {SERIF}; font-size: 48px; line-height: 48px; color: {OXINK}">{day}</span>
<span style="font-size: 14px; line-height: 18px; font-weight: 500; color: {MUTED}">{month}</span>
</div>
<div style="flex: 2 1 260px; display: flex; flex-direction: column; gap: 8px">
<span style="font-size: 15px; line-height: 22px; font-weight: 500; letter-spacing: 0.01em">{composer}</span>
<span style="font-family: {SERIF}; font-size: 22px; line-height: 30px">{work}</span>{with_html}
</div>
<div style="flex: 1 1 180px; display: flex; flex-direction: column; gap: 4px; align-items: flex-start">
<span style="font-size: 15px; line-height: 24px; color: {MUTED}">{where}</span>
{link}
</div>
</div>"""


def upcoming_rows(limit, placeholders):
    items = sorted(PERF.get('upcoming', []), key=lambda i: i.get('date', ''))[:limit]
    rows = items if items else [None] * placeholders
    return '\n'.join(perf_row(r, last=(n == len(rows) - 1)) for n, r in enumerate(rows))


def past_row(item=None):
    if item:
        d = parse_date(item.get('date'))
        when = f'{MONTHS[d.month - 1][:3]} {d.day}' if d else ''
        what = ': '.join(x for x in [esc(item.get('composer')), esc(item.get('work'))] if x)
        where = esc(item.get('venue'))
    else:
        when, what, where = '[Day month]', '[Composer: work title]', '[Venue, city]'
    return f"""<div style="display: flex; flex-wrap: wrap; gap: 4px 32px; padding: 20px 0; border-top: {RULE}">
<span style="flex: 0 0 136px; {META}; line-height: 30px">{when}</span>
<span style="flex: 2 1 260px; font-family: {SERIF}; font-size: 22px; line-height: 30px">{what}</span>
<span style="flex: 1 1 180px; font-size: 15px; line-height: 30px; color: {MUTED}">{where}</span>
</div>"""


def past_block():
    items = sorted(PERF.get('past', []), key=lambda i: i.get('date', ''), reverse=True)
    groups = []
    if items:
        for item in items:
            d = parse_date(item.get('date'))
            y = str(d.year) if d else 'Earlier'
            if not groups or groups[-1][0] != y:
                groups.append((y, []))
            groups[-1][1].append(item)
    else:
        groups = [(str(YEAR), [None, None]), (str(YEAR - 1), [None, None, None])]
    out = []
    for n, (y, rows) in enumerate(groups):
        mt = '' if n == 0 else 'margin-top: 56px; '
        out.append(f'<h3 style="{H3}; {mt}padding-bottom: 16px">{y}</h3>')
        out.extend(past_row(r) for r in rows)
        out.append(f'<div style="border-top: {RULE}"></div>')
    return '\n'.join(out)


# ------------------------------------------------------------------ posts
def read_post(path):
    raw = open(path, encoding='utf-8').read()
    meta, body = {}, raw
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', raw, re.S)
    if m:
        body = m.group(2)
        key = None
        for line in m.group(1).splitlines():
            if line.startswith('- ') and key:
                if not isinstance(meta.get(key), list):
                    meta[key] = []
                meta[key].append(line[2:].strip())
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                meta[key] = value.strip()
    name = os.path.splitext(os.path.basename(path))[0]
    order = int(re.match(r'^(\d+)', name).group(1)) if re.match(r'^\d+', name) else 0
    slug = re.sub(r'^\d+-', '', name)
    words = len(re.findall(r'\w+', body))
    return {
        'slug': slug, 'order': order, 'url': f'/writing/{slug}/',
        'title': meta.get('title', slug), 'topic': meta.get('topic', ''),
        'date': parse_date(meta.get('date', '')),
        'summary': meta.get('summary', ''), 'standfirst': meta.get('standfirst', ''),
        'sources': meta.get('sources') if isinstance(meta.get('sources'), list) else [],
        'draft': meta.get('draft', '').lower() in ('true', 'yes'),
        'html': markdown.markdown(body, extensions=['smarty', 'tables', 'footnotes']),
        'minutes': max(1, round(words / 220)),
    }


def load_posts():
    folder = os.path.join(ROOT, 'content', 'posts')
    posts = [read_post(os.path.join(folder, f)) for f in sorted(os.listdir(folder)) if f.endswith('.md')]
    posts = [p for p in posts if not p['draft']]
    # Newest first: by date when every post has one, otherwise by the number at the start of the file name.
    if posts and all(p['date'] for p in posts):
        posts.sort(key=lambda p: (p['date'], p['order']), reverse=True)
    else:
        posts.sort(key=lambda p: p['order'], reverse=True)
    return posts


POSTS = load_posts()


def post_meta(p, lead=False):
    bits = (['Newest'] if lead else []) + [x for x in [esc(p['topic']), long_date(p['date'])] if x]
    return ' · '.join(bits)


def post_list_small(posts):
    out = []
    for n, p in enumerate(posts):
        bb = f'; border-bottom: {RULE}' if n == len(posts) - 1 else ''
        out.append(f"""<a href="{p['url']}" style="display: flex; flex-direction: column; gap: 8px; padding: 24px 0; border-top: {RULE}{bb}; color: {INK}; text-decoration: none">
<span style="{META}">{post_meta(p)}</span>
<span style="font-family: {SERIF}; font-size: 22px; line-height: 30px">{esc(p['title'])}</span>
</a>""")
    return '\n'.join(out)


def post_rows(posts):
    out = []
    for n, p in enumerate(posts):
        bb = f'; border-bottom: {RULE}' if n == len(posts) - 1 else ''
        out.append(f"""<a href="{p['url']}" style="display: flex; flex-wrap: wrap; gap: 8px 32px; padding: 28px 0; border-top: {RULE}{bb}; color: {INK}; text-decoration: none">
<span style="flex: 0 0 136px; {META}; line-height: 34px">{long_date(p['date'])}</span>
<span style="flex: 1 1 300px; display: flex; flex-direction: column; gap: 6px">
<span style="{META}">{esc(p['topic'])}</span>
<span style="font-family: {SERIF}; font-size: 28px; line-height: 34px">{esc(p['title'])}</span>
<span style="max-width: 560px">{esc(p['summary'])}</span>
</span>
</a>""")
    return '\n'.join(out) if out else f'<p style="{P}">Nothing here yet.</p>'


def lead_post(p, tag='h2'):
    return f"""<article style="flex: 7 1 480px; display: flex; flex-direction: column; gap: 16px; align-items: flex-start; padding-top: 24px; border-top: {RULE}">
<span style="{META}">{post_meta(p, lead=(tag == 'h2'))}</span>
<{tag} style="margin: 0; max-width: 680px; font-family: {SERIF}; font-size: clamp(40px, 4.4cqw, 56px); line-height: 1.08; font-weight: 400; letter-spacing: -0.01em">{esc(p['title'])}</{tag}>
<p style="margin: 0; max-width: 600px; font-size: 21px; line-height: 32px">{esc(p['summary'])}</p>
<a href="{p['url']}" style="{LINK}">Read the post</a>
</article>"""


# ------------------------------------------------------------------ menu and page shell
def menu(current):
    items = [('home', 'Home'), ('bio', 'Biography and photos'), ('perf', 'Performances'), ('teach', 'Teaching'),
             ('writing', 'Writing'), ('duo', 'Understory Duo'), ('contact', 'Contact')]
    links = '\n'.join(
        f'<a href="{URL[k]}"{" aria-current=" + chr(34) + "page" + chr(34) if k == current else ""}>{label}</a>'
        for k, label in items)
    return f"""<div id="menu" class="menu" role="dialog" aria-modal="true" aria-label="Menu">
<div class="menu-photo"><img src="{IMG['hero']}" alt="" loading="lazy"></div>
<nav class="menu-nav" aria-label="Main">
<div class="menu-top">
<a class="menu-name" href="{URL['home']}">Kellum Jones</a>
<a class="menu-close" href="#top" data-menu-close aria-label="Close menu"><span>Close</span>{CLOSE_ICON}</a>
</div>
<div class="menu-links">
{links}
</div>
<div class="menu-foot">
<a href="{EMAIL_HREF}">{EMAIL_LABEL}</a>
{f'<a href="{YOUTUBE}">YouTube</a>' if YOUTUBE else ''}
<a href="{INSTAGRAM}">Instagram</a>
</div>
</nav>
</div>"""


PAGES_WRITTEN = []


def page(path, title, description, header, main, current=None, og_type='website', head_extra=''):
    """Wrap a header and its main content in the full page and write it to public/<path>/index.html."""
    canonical = f'{BASE}{path}'
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="Kellum Jones">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}/images/og-card.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/cardo-regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
<link rel="alternate" type="application/rss+xml" title="Kellum Jones: writing" href="/writing/feed.xml">{head_extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="page">

{header}

<main id="main">

{main}

</main>

{FOOTER}

</div>
{menu(current)}
<script src="/js/site.js" defer></script>
</body>
</html>
"""
    target = os.path.join(OUT, path.strip('/'), 'index.html') if path != '/404.html' else os.path.join(OUT, '404.html')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(doc)
    PAGES_WRITTEN.append((path, doc))


# ------------------------------------------------------------------ Home
def build_home():
    header = f"""<header id="top" class="d-hero on-dark" style="position: relative; display: flex; flex-direction: column; background: {BACKDROP}; color: {EGG}; overflow: hidden">
<img class="d-hero-img" src="{IMG['hero']}" alt="Kellum Jones leaning on a white plinth against a dark backdrop" fetchpriority="high">
<div class="d-hero-fade" aria-hidden="true"></div>
<svg class="d-bow" aria-hidden="true" viewBox="0 0 118 1000" fill="none" stroke="{EGG}" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
{BOW_G}
</svg>
<div style="position: absolute; top: 0; left: 0; right: 0; box-sizing: border-box; padding: 22px {PAD} 0; display: flex; justify-content: flex-end">
{MENU_BUTTON}
</div>
<div style="position: relative; margin: auto auto 0; box-sizing: border-box; width: 100%; max-width: 1280px; padding: 48px {PAD} 40px; display: flex; flex-direction: column; gap: 40px">
<h1 style="margin: 0; display: flex; flex-direction: column; font-family: {SERIF}; font-size: clamp(88px, 12.5cqw, 160px); line-height: 0.9; font-weight: 400; letter-spacing: -0.02em">
<span>Kellum</span>
<span>Jones</span>
</h1>
<p style="margin: 0; font-family: {SERIF}; font-style: italic; font-size: 26px; line-height: 34px">Double bass</p>
</div>
</header>"""

    notebook = ''
    if POSTS:
        notebook = f"""<section id="writing" style="{WRAP}; padding: 96px {PAD} 0; display: flex; flex-direction: column; gap: 48px">
<h2 style="{H2S}">From the notebook</h2>
<div style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 48px clamp(32px, 8cqw, 104px)">
{lead_post(POSTS[0], tag='h3')}
<div class="h-drop" style="flex: 4 1 300px; display: flex; flex-direction: column">
{post_list_small(POSTS[1:4])}
<a href="{URL['writing']}" style="{LINK}; align-self: flex-start; margin-top: 8px">All writing</a>
</div>
</div>
</section>"""

    main = f"""{notebook}

<section id="teaching" class="h-pull" style="{WRAP}; {SECPAD}; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 64px clamp(32px, 10cqw, 128px)">
<div style="flex: 5 1 300px; display: flex; flex-direction: column; gap: 24px; align-items: flex-start">
<img src="{IMG['think']}" alt="Kellum Jones resting his chin on his hand" loading="lazy" style="width: 100%; max-width: 520px; aspect-ratio: 4 / 5; object-fit: cover; object-position: 35% 50%">
<h2 style="{H2}">Teaching</h2>
<p style="margin: 0; max-width: 520px">Lessons start with how you hold the bow and how you listen. I teach beginners and players preparing for auditions, and I am on the double bass faculty of the LaGrange Youth Symphony Orchestra.</p>
<a href="{URL['teach']}" style="{LINK}">Ask about lessons</a>
</div>
<div id="duo" class="h-drop-lg" style="flex: 7 1 380px; display: flex; flex-direction: column; gap: 24px; align-items: flex-start">
<img src="{IMG['duo']}" alt="Kellum Jones and Hsin Yeh of Understory Duo" loading="lazy" style="width: 100%; aspect-ratio: 4 / 3; object-fit: cover; object-position: 75% 50%">
<h2 style="{H2}">Understory Duo</h2>
<p style="margin: 0; max-width: 520px">A double bass and piano duo with pianist Hsin Yeh. We commission new work from living composers, and provide education [finish this line: for whom, and how].</p>
<a href="{URL['duo']}" style="{LINK}">About the duo</a>
</div>
</section>

{split(f'<h2 style="{H2}">Performances</h2>' + chr(10) + f'<a href="{URL["perf"]}" style="{LINK}">{"All performances and recordings" if HAS_VIDEO else "All performances"}</a>', upcoming_rows(2, 2), sec_id='performances')}

{NEWSLETTER}"""
    page('/', 'Kellum Jones, double bass', 'Kellum Jones is a double bassist and teacher based in Columbus, Georgia. Performances, lessons, and writing on practice and the German bow.', header, main, current='home', head_extra='\n' + structured_data())


# ------------------------------------------------------------------ Biography
def build_bio():
    bio_paras = '\n'.join(f'<p style="{P}">{t}</p>' for t in BIO_PARAS)
    main = f"""<section style="{WRAP}; padding: 96px {PAD} 0; display: flex; flex-wrap: wrap-reverse; align-items: flex-end; gap: 48px clamp(32px, 10cqw, 128px)">
<div style="flex: 7 1 420px; display: flex; flex-direction: column; gap: 24px">
<p style="{LEAD}">{BIO_LEAD}</p>
{bio_paras}
<a href="{URL['contact']}" style="{LINK}">Get in touch</a>
</div>
<div class="p-rise" style="position: relative; flex: 4 1 300px; max-width: 480px">
{photo(IMG['lean'], 'Kellum Jones leaning forward on a white plinth', '2 / 3', f'Photo: {PHOTOGRAPHER}', '50% 40%', download=False)}
{FADE}
</div>
</section>

<section aria-label="Short biography" style="padding-top: clamp(96px, 12.5cqw, 160px)">
<div class="p-bleed-r" style="box-sizing: border-box; background: {RAISED}; {PANEL_PAD_R}; display: flex; flex-direction: column; gap: 16px; align-items: flex-start">
<span style="{META}">For concert programs</span>
<h2 style="{H2S}">Short biography</h2>
<p style="margin: 0; max-width: 680px">{BIO_SHORT}</p>
<a href="{PRESS_KIT}" download style="{LINK}">Download press kit</a>
</div>
</section>

<section id="photos" style="{WRAP}; {SECPAD}; display: flex; flex-direction: column; gap: 48px">
<div style="display: flex; flex-direction: column; gap: 12px">
<h2 style="{H2}">Photos</h2>
<p style="{P}">Free to use for press and concert programs. Please credit {PHOTOGRAPHER}.</p>
</div>
<div style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 48px 32px">
<div style="flex: 7 1 420px; min-width: 0; display: flex; flex-direction: column; gap: 48px">
{photo(IMG['hero'], 'Kellum Jones leaning on a white plinth, head resting on his hand', '3 / 2', 'Landscape, dark backdrop', '50% 30%', download=PRESS + 'kellum-jones-leaning-on-hand.jpg')}
<div class="p-indent">
{photo(IMG['think'], 'Kellum Jones resting his chin on his hand', '3 / 2', 'Landscape, dark backdrop', download=PRESS + 'kellum-jones-chin-on-hand.jpg')}
</div>
<div style="max-width: 62%">
{photo(IMG['lean'], 'Kellum Jones leaning forward on a white plinth', '2 / 3', 'Portrait, dark backdrop', '50% 40%', download=PRESS + 'kellum-jones-leaning-forward.jpg')}
</div>
</div>
<div class="h-drop" style="flex: 4 1 260px; min-width: 0; display: flex; flex-direction: column; gap: 48px">
{photo(IMG['stand'], 'Kellum Jones standing in a camel coat, looking at the camera', '2 / 3', 'Portrait, grey backdrop', download=PRESS + 'kellum-jones-standing.jpg')}
{photo(IMG['up'], 'Kellum Jones standing in a camel coat, looking up', '2 / 3', 'Portrait, grey backdrop', download=PRESS + 'kellum-jones-standing-looking-up.jpg')}
</div>
</div>
</section>"""
    page(URL['bio'], 'Biography and photos · Kellum Jones', 'Biography of double bassist Kellum Jones, a short version for concert programs, and press photos.', band('<span>Biography</span>', mark='clef'), main, current='bio')


# ------------------------------------------------------------------ Performances
def build_perf():
    vids = PERF.get('videos', [])
    v = (vids + [None, None, None])[:3]
    watch = f"""<section id="watch" style="{WRAP}; {SECPAD}; display: flex; flex-direction: column; gap: 48px">
<h2 style="{H2}">Watch and listen</h2>
<div style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 48px 32px">
<div style="flex: 7 1 420px; min-width: 0">
{video(v[0], '[Featured video from YouTube]', '[Composer: work title] · [where and when it was recorded]')}
</div>
<div class="h-drop" style="flex: 4 1 260px; min-width: 0; display: flex; flex-direction: column; gap: 32px">
{video(v[1])}
{video(v[2])}
{yt_link(f'{LINK}; align-self: flex-start', 'More on YouTube')}
</div>
</div>
</section>""" if HAS_VIDEO else ''
    main = f"""{split(f'<h2 style="{H2}">Upcoming</h2>' + chr(10) + f'<img class="feather wide-only" src="{IMG["up"]}" alt="Kellum Jones standing in a camel coat, looking up" loading="lazy" style="display: block; width: 100%; max-width: 360px; margin-top: 16px; aspect-ratio: 4 / 5; object-fit: cover; object-position: 50% 12%">', upcoming_rows(50, 3), sec_id='upcoming', first=True)}

{watch}

{split(f'<h2 style="{H2}">Past performances</h2>', past_block(), sec_id='past')}

{cta('Booking', 'For recitals, concertos, chamber music and school visits, write with the date and the kind of program you have in mind.', 'Get in touch')}"""
    page(URL['perf'], 'Performances · Kellum Jones', 'Upcoming and past performances by double bassist Kellum Jones' + (', with video.' if HAS_VIDEO else '.'), band('<span>Performances</span>', mark='fermata'), main, current='perf')


# ------------------------------------------------------------------ Teaching
def numbered(n, title, text, last=False):
    bb = f'; border-bottom: {RULE}' if last else ''
    return f"""<div style="display: flex; flex-wrap: wrap; gap: 8px 32px; padding: 32px 0; border-top: {RULE}{bb}">
<span style="flex: 0 0 104px; font-family: {SERIF}; font-size: 48px; line-height: 48px; color: {OXINK}">{n}</span>
<div style="flex: 1 1 300px; display: flex; flex-direction: column; gap: 8px">
<h3 style="{H3}">{title}</h3>
<p style="margin: 0; max-width: 560px">{text}</p>
</div>
</div>"""


def detail(term, value, last=False):
    bb = f'; border-bottom: {RULE}' if last else ''
    return f"""<div style="display: flex; flex-wrap: wrap; gap: 4px 32px; padding: 20px 0; border-top: {RULE}{bb}">
<dt style="flex: 0 0 136px; {META}; line-height: 30px">{term}</dt>
<dd style="flex: 1 1 260px; margin: 0">{value}</dd>
</div>"""


def build_teach():
    main = f"""<section style="{WRAP}; padding: 96px {PAD} 0; display: flex; flex-wrap: wrap-reverse; align-items: flex-end; gap: 48px clamp(32px, 10cqw, 128px)">
<div style="flex: 7 1 420px; display: flex; flex-direction: column; gap: 24px">
<p style="{LEAD}">Lessons start with how you hold the bow and how you listen.</p>
<p style="{P}">I teach double bass to beginners, to school and youth orchestra players, and to students preparing for auditions. I am on the double bass faculty of the LaGrange Youth Symphony Orchestra, and I lead weekly technique sessions for students at the Schwob School of Music.</p>
<p style="{P}">[Your approach in your own words: two or three sentences on what a student can expect from you and what you expect from them.]</p>
<a href="{URL['contact']}" style="{LINK}">Ask about lessons</a>
</div>
<div class="p-rise" style="position: relative; flex: 4 1 300px; max-width: 480px">
<img src="{IMG['think']}" alt="Kellum Jones resting his chin on his hand" style="display: block; width: 100%; aspect-ratio: 4 / 5; object-fit: cover; object-position: 35% 50%">
{FADE}
</div>
</section>

{split(f'<h2 style="{H2}">What lessons cover</h2>', numbered(1, 'Sound and the bow', 'The bow hold, arm weight, contact point and string crossings. German bow is my own instrument. [Say here whether you also take French bow students.]') + chr(10) + numbered(2, 'The left hand', 'Shifting, intonation and a hand frame that stays relaxed across the whole fingerboard.') + chr(10) + numbered(3, 'How to practice', 'How to plan an hour, what to do when a passage will not improve, and how to tell whether the work is paying off.', last=True), sec_id='cover')}

<section aria-label="Practical details" style="padding-top: clamp(96px, 12.5cqw, 160px)">
<div class="p-bleed-r" style="box-sizing: border-box; background: {RAISED}; {PANEL_PAD_R}; display: flex; flex-direction: column; gap: 24px">
<h2 style="{H2S}">Practical details</h2>
<dl style="margin: 0; max-width: 760px; display: flex; flex-direction: column">
{detail('Where', '[In person in Columbus, Georgia, and online]')}
{detail('Who', '[Ages and levels you take]')}
{detail('Length', '[30, 45 or 60 minutes]')}
{detail('Rates', '[Your rates, or &quot;on request&quot;]', last=True)}
</dl>
</div>
</section>

{cta('Ask about lessons', 'Tell me how long you have played and what you want to work on. I will write back with times.', 'Write to me')}"""
    page(URL['teach'], 'Teaching · Kellum Jones', 'Double bass lessons with Kellum Jones in Columbus, Georgia, and online: what lessons cover and how to start.', band('<span>Teaching</span>', mark='bowing'), main, current='teach')


# ------------------------------------------------------------------ Writing
def topic_nav(current_topic=None):
    out = [f'<h2 style="{META}; margin: 0 0 12px">Topics</h2>']
    for n, (name, text) in enumerate(TOPICS):
        bb = f'; border-bottom: {RULE}' if n == len(TOPICS) - 1 else ''
        cur = ' aria-current="page"' if name == current_topic else ''
        out.append(f"""<a href="/writing/topic/{slugify(name)}/"{cur} style="display: flex; flex-direction: column; gap: 4px; padding: 20px 0; border-top: {RULE}{bb}; color: {INK}; text-decoration: none">
<span style="font-family: {SERIF}; font-size: 22px; line-height: 30px">{name}</span>
<span style="font-size: 15px; line-height: 22px; color: {MUTED}">{text}</span>
</a>""")
    return '\n'.join(out)


def build_writing():
    lead = lead_post(POSTS[0]) if POSTS else f'<p style="flex: 7 1 480px; {P}">The first post is on its way.</p>'
    main = f"""<section style="{WRAP}; padding: 96px {PAD} 0; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 48px clamp(32px, 8cqw, 104px)">
{lead}
<nav aria-label="Topics" class="h-drop" style="flex: 4 1 300px; display: flex; flex-direction: column">
{topic_nav()}
</nav>
</section>

{split(f'<h2 style="{H2}">All posts</h2>', post_rows(POSTS), sec_id='all')}

{NEWSLETTER}"""
    page(URL['writing'], 'Writing · Kellum Jones', 'Notes from the practice room: posts by Kellum Jones on practice, the German bow and new music for double bass.', band('<span>Writing</span>', 'Notes from the practice room', mark='segno'), main, current='writing')

    for name, text in TOPICS:
        posts = [p for p in POSTS if p['topic'] == name]
        main = f"""{split(f'<h2 style="{H2}">{len(posts)} {"post" if len(posts) == 1 else "posts"}</h2>' + chr(10) + f'<a href="{URL["writing"]}" style="{LINK}">All writing</a>', post_rows(posts), sec_id='all', first=True)}

{NEWSLETTER}"""
        page(f'/writing/topic/{slugify(name)}/', f'{name} · Writing · Kellum Jones', text, band(f'<span>{name}</span>', text, mark='segno'), main, current='writing')


def build_posts():
    for n, p in enumerate(POSTS):
        newer = POSTS[n - 1] if n > 0 else None
        older = POSTS[n + 1] if n + 1 < len(POSTS) else None
        sources = ''
        if p['sources']:
            items = '\n'.join(f'<span style="font-size: 15px; line-height: 24px">{markdown.markdown(s)[3:-4]}</span>' for s in p['sources'])
            sources = f"""<div style="max-width: 640px; margin-top: 20px; padding-top: 20px; border-top: {RULE}; display: flex; flex-direction: column; gap: 4px">
<span style="{META}">Sources and further reading</span>
{items}
</div>"""
        standfirst = f'\n<p style="margin: 0 0 12px; max-width: 640px; font-family: {SERIF}; font-size: clamp(24px, 2.2cqw, 28px); line-height: 1.35">{esc(p["standfirst"])}</p>' if p['standfirst'] else ''
        more = []
        if older:
            more.append(f"""<a href="{older['url']}" style="flex: 3 1 200px; display: flex; flex-direction: column; gap: 8px; padding-top: 20px; border-top: {RULE}; color: {INK}; text-decoration: none">
<span style="{META}">Previous</span>
<span style="font-family: {SERIF}; font-size: 22px; line-height: 30px">{esc(older['title'])}</span>
</a>""")
        if newer:
            more.append(f"""<a href="{newer['url']}" style="flex: 9 1 480px; display: flex; flex-direction: column; gap: 8px; padding-top: 20px; border-top: {RULE}; color: {INK}; text-decoration: none">
<span style="{META}">Next · {esc(newer['topic'])}</span>
<span style="max-width: 680px; font-family: {SERIF}; font-size: clamp(28px, 3.2cqw, 40px); line-height: 1.15">{esc(newer['title'])}</span>
</a>""")
        more_html = f"""<nav aria-label="More writing" style="{WRAP}; {SECPAD}; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 32px clamp(32px, 6cqw, 80px)">
{chr(10).join(more)}
</nav>""" if more else ''
        main = f"""<article style="{WRAP}; padding: clamp(64px, 8cqw, 104px) {PAD} 0; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 32px clamp(32px, 6cqw, 80px)">
<div style="flex: 3 1 200px; display: flex; flex-direction: column; gap: 4px; align-items: flex-start; padding-top: 20px; border-top: {RULE}">
<span style="{META}; color: {INK}">{esc(p['topic'])}</span>
<span style="{META}">{long_date(p['date'])}</span>
<span style="{META}">{p['minutes']} minute read</span>
<a href="{URL['writing']}" style="{LINK}; margin-top: 8px">All writing</a>
</div>
<div style="flex: 9 1 480px; min-width: 0; display: flex; flex-direction: column; gap: 28px">
<h1 style="margin: 0; max-width: 820px; font-family: {SERIF}; font-size: clamp(44px, 5.6cqw, 72px); line-height: 1.04; font-weight: 400; letter-spacing: -0.015em">{esc(p['title'])}</h1>{standfirst}
<div class="prose">
{p['html']}
</div>
{END_MARK}
{sources}
</div>
</article>

{more_html}

{NEWSLETTER}"""
        page(p['url'], f'{p["title"]} · Kellum Jones', p['summary'] or p['standfirst'] or p['title'], BAR, main, current='writing', og_type='article')


# ------------------------------------------------------------------ Understory Duo
def commission(last=False):
    bb = f'; border-bottom: {RULE}' if last else ''
    return f"""<div style="display: flex; flex-wrap: wrap; gap: 8px 32px; padding: 28px 0; border-top: {RULE}{bb}">
<span style="flex: 0 0 136px; {META}; line-height: 30px">[Year]</span>
<div style="flex: 2 1 260px; display: flex; flex-direction: column; gap: 6px">
<span style="font-size: 15px; line-height: 22px; font-weight: 500; letter-spacing: 0.01em">[Composer]</span>
<span style="font-family: {SERIF}; font-size: 22px; line-height: 30px">[Work title]</span>
</div>
<span style="flex: 1 1 180px; font-size: 15px; line-height: 30px; color: {MUTED}">[Premiere: venue, city]</span>
</div>"""


def build_duo():
    main = f"""<section style="{WRAP}; padding: 96px {PAD} 0; display: flex; flex-wrap: wrap-reverse; align-items: flex-end; gap: 48px clamp(32px, 7.5cqw, 96px)">
<div style="flex: 5 1 340px; display: flex; flex-direction: column; gap: 24px">
<p style="{LEAD}">Understory Duo is the double bassist Kellum Jones and the pianist Hsin Yeh.</p>
<p style="{P}">We commission new work from living composers, and provide education [finish this line: for whom, and how].</p>
<p style="{P}">[Why the name: one or two sentences on what &quot;understory&quot; means to you both.]</p>
<a href="{URL['contact']}" style="{LINK}">Write to the duo</a>
</div>
<div class="p-rise" style="position: relative; flex: 6 1 380px">
<img src="{IMG['duo']}" alt="Kellum Jones and Hsin Yeh of Understory Duo" style="display: block; width: 100%; aspect-ratio: 4 / 3; object-fit: cover; object-position: 75% 50%">
{FADE}
</div>
</section>

<section id="players" style="{WRAP}; {SECPAD}; display: flex; flex-direction: column; gap: 48px">
<h2 style="{H2}">The players</h2>
<div style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 48px clamp(32px, 10cqw, 128px)">
<div style="flex: 5 1 300px; display: flex; flex-direction: column; gap: 12px; align-items: flex-start; padding-top: 24px; border-top: {RULE}">
<span style="{META}">Double bass</span>
<h3 style="{H3}">Kellum Jones</h3>
<p style="margin: 0; max-width: 520px">Kellum studies at the Schwob School of Music with Dr. Luca Lombardi and plays the German bow in the Viennese tradition. He teaches on the double bass faculty of the LaGrange Youth Symphony Orchestra.</p>
<a href="{URL['bio']}" style="{LINK}">Full biography</a>
</div>
<div class="h-drop" style="flex: 6 1 340px; display: flex; flex-direction: column; gap: 12px; align-items: flex-start; padding-top: 24px; border-top: {RULE}">
<span style="{META}">Piano</span>
<h3 style="{H3}">Hsin Yeh</h3>
<p style="margin: 0; max-width: 520px">[Hsin&#39;s biography: two or three sentences, in the third person.]</p>
</div>
</div>
</section>

{split(f'<h2 style="{H2}">Commissions</h2>' + chr(10) + '<p style="margin: 0; max-width: 320px">New pieces written for the duo.</p>', commission() + chr(10) + commission(last=True), sec_id='commissions')}

{cta('Composers and presenters', 'We are looking for new pieces and for places to play them. Tell us what you are working on.', 'Write to us')}"""
    page(URL['duo'], 'Understory Duo · double bass and piano', 'Understory Duo is double bassist Kellum Jones and pianist Hsin Yeh, commissioning new work for double bass and piano from living composers.', band('<span>Understory</span><span>Duo</span>', 'Double bass and piano', mark='tie'), main, current='duo')


# ------------------------------------------------------------------ Contact
def reach(label, heading, text):
    return f"""<div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-start; padding-top: 24px; border-top: {RULE}">
<span style="{META}">{label}</span>
<h2 style="{H3}">{heading}</h2>
<p style="margin: 4px 0 0; max-width: 420px">{text}</p>
<a href="{EMAIL_HREF}" style="{LINK}">{EMAIL_LABEL}</a>
</div>"""


def build_contact():
    if FORM_ACTION:
        form_open = f'<form action="{FORM_ACTION}" method="post"'
    elif EMAIL:
        form_open = f'<form action="mailto:{esc(EMAIL)}" method="post" enctype="text/plain" data-mailto="{esc(EMAIL)}"'
    else:
        form_open = '<form action="#main" method="get"'
    main = f"""<section style="{WRAP}; padding: 96px {PAD} 0; display: flex; flex-wrap: wrap; align-items: flex-start; gap: 64px clamp(32px, 5cqw, 64px)">
<div class="c-photo" style="flex: 3 1 240px; min-width: 0">
<img class="feather" src="{IMG['stand']}" alt="Kellum Jones standing in a camel coat, looking at the camera" loading="lazy" style="display: block; width: 100%; max-width: 420px; aspect-ratio: 3 / 4; object-fit: cover; object-position: 50% 10%">
</div>
<div style="flex: 4 1 260px; display: flex; flex-direction: column; gap: 40px">
{reach('Concerts', 'Booking and programs', 'Recitals, concertos, chamber music and school visits.')}
{reach('Lessons', 'Study with me', 'In person in Columbus, Georgia, and online.')}
<div style="display: flex; flex-direction: column; gap: 4px; align-items: flex-start; padding-top: 24px; border-top: {RULE}">
<span style="{META}">Elsewhere</span>
<div style="display: flex; flex-wrap: wrap; gap: 0 32px">
{yt_link(LINK)}
<a href="{INSTAGRAM}" style="{LINK}">Instagram</a>
<a href="{URL['duo']}" style="{LINK}">Understory Duo</a>
</div>
</div>
</div>
{form_open} class="h-drop" style="flex: 5 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 24px">
<h2 style="{H2S}">Send a message</h2>
<div style="display: flex; flex-wrap: wrap; gap: 24px 16px">
<div style="flex: 1 1 200px; display: flex; flex-direction: column; gap: 8px">
<label for="c-name" style="{LABEL}">Name</label>
<input id="c-name" name="name" type="text" autocomplete="name" required style="{FIELD}">
</div>
<div style="flex: 1 1 200px; display: flex; flex-direction: column; gap: 8px">
<label for="c-email" style="{LABEL}">Email address</label>
<input id="c-email" name="email" type="email" autocomplete="email" required style="{FIELD}">
</div>
</div>
<div style="display: flex; flex-direction: column; gap: 8px">
<label for="c-about" style="{LABEL}">What is this about?</label>
<select id="c-about" name="about" style="{FIELD}">
<option>Booking a performance</option>
<option>Lessons</option>
<option>Understory Duo</option>
<option>Something else</option>
</select>
</div>
<div style="display: flex; flex-direction: column; gap: 8px">
<label for="c-message" style="{LABEL}">Message</label>
<textarea id="c-message" name="message" rows="7" required style="{FIELD}; resize: vertical"></textarea>
</div>
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px 24px">
<button type="submit" class="btn" style="{BTN}">Send message</button>
<span style="font-size: 15px; line-height: 22px; color: {MUTED}">I reply within {REPLY_TIME}.</span>
</div>
</form>
</section>"""
    page(URL['contact'], 'Contact · Kellum Jones', 'Write to Kellum Jones about booking a performance, double bass lessons, or Understory Duo.', band('<span>Contact</span>', mark='trill'), main, current='contact')


def build_404():
    main = f"""<section style="{WRAP}; padding: 96px {PAD} 0; display: flex; flex-direction: column; gap: 24px; align-items: flex-start">
<p style="{LEAD}">That page is not here. It may have moved, or the link may be wrong.</p>
<a href="{URL['home']}" class="btn" style="{BTN}">Go to the home page</a>
</section>"""
    page('/404.html', 'Page not found · Kellum Jones', 'Page not found.', band('<span>Page not found</span>', mark='fermata'), main)


# ------------------------------------------------------------------ files beside the pages
FAVICON = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="{OX}"/>
<g transform="translate(11 9)" fill="none" stroke="{EGG}" stroke-width="3" stroke-linecap="round">
<circle cx="9" cy="17" r="4" fill="{EGG}" stroke="none"/>
<path d="M9 17 C9 6 30 2 31 17 C32 29 20 39 6 43"/>
<circle cx="40" cy="11" r="2.8" fill="{EGG}" stroke="none"/>
<circle cx="40" cy="22" r="2.8" fill="{EGG}" stroke="none"/>
</g>
</svg>
"""


def write(path, text):
    target = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(text)


def build_extras():
    write('favicon.svg', FAVICON)
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    urls = '\n'.join(f'<url><loc>{BASE}{path}</loc></url>' for path, _ in PAGES_WRITTEN if path != '/404.html')
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    items = '\n'.join(
        f'<item><title>{esc(p["title"])}</title><link>{BASE}{p["url"]}</link><guid>{BASE}{p["url"]}</guid>'
        + (f'<pubDate>{p["date"].strftime("%a, %d %b %Y")} 12:00:00 GMT</pubDate>' if p['date'] else '')
        + f'<description>{esc(p["summary"])}</description></item>'
        for p in POSTS)
    write('writing/feed.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Kellum Jones: writing</title><link>{BASE}/writing/</link><description>Notes from the practice room.</description>\n{items}\n</channel></rss>\n')
    write('_headers', '/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n/images/*\n  Cache-Control: public, max-age=604800\n/css/*\n  Cache-Control: public, max-age=3600\n/js/*\n  Cache-Control: public, max-age=3600\n')


def build_press_kit():
    """Write press/kellum-jones-press-kit.zip: both biographies as text, plus the press photos."""
    import zipfile
    finished = [t for t in BIO_PARAS if not t.startswith('[')]     # leave unfinished paragraphs out
    credit = SITE.get('photographer', '').strip()
    text = '\n'.join([
        'KELLUM JONES, double bass', BASE, '',
        'SHORT BIOGRAPHY (for concert programs)', '', BIO_SHORT, '', '',
        'BIOGRAPHY', '', BIO_LEAD, '', '\n\n'.join(finished), '', '',
        'PHOTOS', '', 'Free to use for press and concert programs.' + (f' Please credit {credit}.' if credit else ''), '',
        'CONTACT', '', SITE.get('email', '').strip() or f'{BASE}/contact/', '',
    ])
    folder = os.path.join(ROOT, 'assets', 'images', 'press')
    target = os.path.join(OUT, KIT_URL.strip('/'))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    fixed = (2026, 1, 1, 0, 0, 0)       # a fixed date, so the file only changes when its contents do
    with zipfile.ZipFile(target, 'w') as z:
        z.writestr(zipfile.ZipInfo('kellum-jones-press-kit/biography.txt', fixed), text, zipfile.ZIP_DEFLATED)
        for name in sorted(os.listdir(folder)):
            with open(os.path.join(folder, name), 'rb') as f:
                z.writestr(zipfile.ZipInfo(f'kellum-jones-press-kit/photos/{name}', fixed), f.read(), zipfile.ZIP_STORED)


def structured_data():
    """A short description of Kellum for search engines, placed on the home page."""
    same = [u for u in (SITE.get('youtube', '').strip(), SITE.get('instagram', '').strip()) if u]
    data = {'@context': 'https://schema.org', '@type': 'Person', 'name': 'Kellum Jones', 'jobTitle': 'Double bassist',
            'url': BASE + '/', 'image': BASE + IMG['hero'], 'description': BIO_SHORT,
            'address': {'@type': 'PostalAddress', 'addressLocality': 'Columbus', 'addressRegion': 'GA', 'addressCountry': 'US'},
            'memberOf': {'@type': 'MusicGroup', 'name': 'Understory Duo', 'url': BASE + URL['duo']}}
    if same:
        data['sameAs'] = same
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def copy_assets():
    for name in ('css', 'js', 'fonts', 'images'):
        shutil.copytree(os.path.join(ROOT, 'assets', name), os.path.join(OUT, name), dirs_exist_ok=True)


def report_placeholders():
    """List the bracketed placeholders still visible on the built pages."""
    total = 0
    for path, doc in PAGES_WRITTEN:
        text = re.sub(r'<(script|style)\b.*?</\1>', '', doc, flags=re.S)
        text = re.sub(r'<[^>]+>', '\n', text)
        found = sorted(set(m.strip() for m in re.findall(r'\[[^\[\]\n]{3,}\]', html.unescape(text))))
        if found:
            total += len(found)
            print(f'\n{path}')
            for f in found:
                print(f'  {f}')
    for key in ('email', 'instagram', 'photographer', 'newsletter_action'):
        if not SITE.get(key, '').strip():
            print(f'\ncontent/site.json: "{key}" is empty')
    if not HAS_VIDEO:
        print('\ncontent/site.json: "youtube" is empty, so the YouTube links and the video section are left off the site')
    print(f'\n{total} placeholders left across {len(PAGES_WRITTEN)} pages.')


if __name__ == '__main__':
    # empty public/ without removing the folder itself, so a local preview server keeps working
    os.makedirs(OUT, exist_ok=True)
    for entry in os.listdir(OUT):
        path = os.path.join(OUT, entry)
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    copy_assets()
    build_home()
    build_bio()
    build_perf()
    build_teach()
    build_writing()
    build_posts()
    build_duo()
    build_contact()
    build_404()
    build_extras()
    build_press_kit()
    print(f'Built {len(PAGES_WRITTEN)} pages into public/')
    if '--check' in sys.argv:
        report_placeholders()
