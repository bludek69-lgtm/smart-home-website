"""Idempotent page builder — Phase A: 4-pillar mega-menu architecture.

Reads each existing per-page HTML, extracts its <main> content, and re-wraps
with the current shared template (header with mega-menu + footer).

Also generates 2 new hub pages (prozivani.html, pribeh.html) and rebuilds
index.html with hero + 4 pillar cards.

Run from website root:
  py -3.14 _build_pages.py

Idempotency: re-running keeps existing content intact. Source of truth for
each subpage is its own HTML file's <main> block.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

# ─── PILLAR / NAV ARCHITECTURE ─────────────────────────────────
# Top-level nav items.  Each pillar can have subpages used to BUILD the
# corresponding hub page and the technicka-mapa.html page; nav strip itself
# is LEAN (7 flat items, no mega-menu) — see MAIN_NAV below.
PILLARS = [
    {
        'id': 'prozivani',
        'icon': '🏠',
        'label': 'Prožívání',
        'title': 'Prožívání — co systém umožňuje',
        'lead': 'Use-case pohled na celý systém — co dům dělá pro ty, kdo v něm žijí. Funkce, dashboardy a AI vrstva v jednom.',
        'sub': ['topeni-klima', 'svetla', 'audio', 'bezpecnost-kamery', 'atmosfera', 'energie', 'funkce', 'digital-twin', 'ai-brain'],
    },
    {
        'id': 'zarizeni',
        'icon': '📦',
        'label': 'Zařízení',
        'title': 'Zařízení',
        'lead': 'Hardware co řídí dům — Homey Pro 2026, 79 zařízení, infrastruktura okolo.',
        'sub': ['senzory', 'ovladace', 'svitidla', 'repro', 'rolety', 'zasuvky', 'hardware', 'infra'],
        'is_existing': True,  # zarizeni.html already exists, don't overwrite content
    },
    {
        'id': 'pribeh',
        'icon': '📖',
        'label': 'Příběh',
        'title': 'Příběh projektu',
        'lead': 'Cesta k současnému stavu — historie, architektonické přechody a problémy které vznikaly a řešily se cestou.',
        'sub': ['team', 'journey', 'proc-smart-home', 'historie', 'architektura', 'vyzvy', 'rano-rutina', 'navrat-domu', 'nocni-koupelna'],
    },
    {
        'id': 'blog',
        'icon': '📝',
        'label': 'Blog',
        'title': 'Blog a novinky',
        'lead': 'Pravidelné poznámky o tom, co se v systému změnilo, co se rozbilo a jak se to fixovalo.',
        'sub': [],
        'is_existing': True,
    },
    {
        'id': 'kontakt',
        'icon': '✉',
        'label': 'Kontakt',
        'title': 'O projektu',
        'lead': 'Kdo, proč, stack.',
        'sub': [],
        'is_existing': True,
    },
    {
        'id': 'aplikace',
        'icon': '🗃',
        'label': 'Sbírka App',
        'title': 'Sbírka — numismatika a filatelie',
        'lead': 'Webová aplikace pro správu numismatické a filatelistické sbírky. DEMO verze veřejně, PRIVATE instance chráněná přihlášením.',
        'sub': [],
        'is_existing': True,
    },
]

# Lean top-level navigation — 8 flat items, no mega-menu.
# Order: Domů, Jak to funguje, Zařízení, Hardware (kompletní katalog), Dashboard, Příběh, Blog, Kontakt.
# 2026-05-20: Hardware-komplet vrácen do hlavního menu (uživatel hledal katalog s obrázky zařízení).
MAIN_NAV = [
    {'id': 'home',              'href': 'index.html',             'label': 'Domů'},
    {'id': 'prozivani',         'href': 'prozivani.html',         'label': 'Jak to funguje'},
    {'id': 'zarizeni',          'href': 'zarizeni.html',          'label': 'Zařízení'},
    {'id': 'hardware-komplet',  'href': 'hardware-komplet.html',  'label': 'Hardware'},
    {'id': 'dashboard',         'href': 'dashboard.html',         'label': 'Dashboard'},
    {'id': 'pribeh',            'href': 'pribeh.html',            'label': 'Příběh'},
    {'id': 'blog',              'href': 'blog.html',              'label': 'Blog'},
    {'id': 'kontakt',           'href': 'kontakt.html',           'label': 'Kontakt'},
    {'id': 'aplikace',          'href': 'aplikace.html',          'label': 'Sbírka App'},
]

# Sub-page metadata (existing pages that became sub-pages under pillars).
SUBPAGES = {
    'topeni-klima': ('Topení a klima', 'Topení a klima',        'Elektrický kotel 9 kW, 4 zóny s vlastním rozvrhem, 3 režimy a tři AI vrstvy. Topení které předvídá a šetří.'),
    'svetla':       ('Světla',         'Světla a osvětlení',    'Dual-sensor open space, lux-driven automatika, privacy guard kdy svítit nesmí, 4-vrstvá pipeline od request po fyzickou žárovku.'),
    'audio':        ('Audio a TTS',    'Audio a TTS',           'TTS přes Google Cast s 200-char limitem, briefing split do fází, multi-speaker routing, sleep guard, prev_playing protection po bathroom misroute.'),
    'bezpecnost-kamery': ('Bezpečnost a kamery', 'Bezpečnost a kamery', 'Multi-zone motion + presence detection, door/window guard, away/home stavová logika, anomaly detection přes Brain Guardian.'),
    'atmosfera':    ('Atmosféra',      'Atmosféra a scény',     'Sleep state co všechno gateuje, morning/sleep brain, comfort suggest, time-of-day scénografie. Dům co cítí část dne.'),
    'energie':      ('Energie',        'Energie a spotřeba',    'Runtime-based kWh estimate kotle, plug devices s power metering, daily/yearly tracking, Shelly Pro 3EM v rozvaděči pro reálné měření (live od 12. 5. 2026).'),
    'senzory':      ('Senzory',        'Senzory',               'mmWave presence FP2, PIR Fibaro, door/window kontakty, lux senzory. Co dům vidí a slyší.'),
    'ovladace':     ('Tlačítka a ovladače', 'Tlačítka a ovladače', 'Aqara Cube T1 Pro jako primární gestural input, fyzická tlačítka jako fallback. User input bez aplikací.'),
    'svitidla':     ('Svítidla',       'Svítidla',              'Stropní, stolní, LED pásek, koupelnová svítidla. Wi-Fi, Zigbee, Z-wave — všechno zpod jedné pipeline.'),
    'repro':        ('Reproduktory',   'Reproduktory',          'Tři Google Cast koncové body + Nest Hub Max. Speakers v kuchyni, koupelně, ložnici, vizuál v ložnici.'),
    'rolety':       ('Rolety',         'Rolety',                'IKEA Fyrtur, dvojí role — fyzické zastínění a privacy signal pro light router.'),
    'zasuvky':      ('Zásuvky a měření', 'Zásuvky a měření',    '11 plug devices s power metering, FGS-223 rezerva, Shelly Pro 3EM v rozvaděči pro 3-fázové měření (live od 12. 5. 2026).'),
    'rano-rutina':  ('Ráno v 3:15',    'Ráno v 3:15',           'Případová studie — minute-by-minute timeline pondělního rána. Pre-wake boost, briefing split, bathroom radio, departure. Vše autonomní.'),
    'navrat-domu':  ('Návrat domů',    'Když přijdu domů',      'Případová studie — multi-signal arrival pipeline. Geofence, motion confirm, preset přepnutí, heating boost, light routing. 30 sekund od vstupu po sync.'),
    'nocni-koupelna': ('Noční koupelna', 'Noční koupelna ve 3 ráno', 'Případová studie — motion v koupelně uprostřed noci. Sleep guard, jemná dim cesta, žádný TTS, žádný plný restart subsystémů. Subtilní rozdíl, který drží spánek.'),
    'team':         ('Kdo za tím stojí', 'Kdo stojí za SMART HOME OS', 'Lidský architekt + AI co-pilots. 5 rolí, jedno zařízení. Human + AI Co-Built System.'),
    'journey':      ('Jak vznikal',    'Jak vznikal SMART HOME OS', 'Engineering journey od první žárovky po Brain Guardian. 7 fází + lessons learned + co dělá systém unikátním.'),
    'proc-smart-home': ('Proč smart home', 'Proč vůbec smart home', 'Realisticky, ne marketingově. Energie, komfort, stabilita — co dům reálně řeší a kde se nejvíc plýtvá energií. Plus role AI v rozhodování.'),
    'historie':     ('Historie',       'Historie projektu',     'Jak systém vznikal — od první žárovky k AI Brain Guardian.'),
    'hardware':     ('Hardware',       'Hardware',              'Homey Pro 2026, bezdrátové protokoly, klíčová zařízení.'),
    'funkce':       ('Funkce',         'Funkce',                'Topení, ranní rutina, příchod/odchod, fyzická tlačítka, koupelna, světelný cyklus, robot vysavač.'),
    'infra':        ('Infrastruktura', 'Infrastruktura',        'Raspberry Pi, Home Assistant, GitHub repos, GitHub Actions.'),
    'dashboard':    ('Dashboard',      'Dashboard',             'Tři obrazovky, jeden systém. 1024×600 RPi kiosek, 1920×1080 notebook, 2880×1800 monitor.'),
    'digital-twin': ('Digital Twin',   'Digital Twin domu',     'Klikací půdorys s 7 zónami a 74 zařízeními. Read-only showcase — žádné API tokeny, žádné ovládání, jen mapa toho, co dům má.'),
    'architektura': ('Architektura',   'Architektura',          'Script-first princip a 12 pravidel co drží systém pohromadě.'),
    'vyzvy':        ('Výzvy',          'Výzvy',                 'Reálné problémy které jsem řešil — Zigbee battery, SIGABRT, ghost values, audio race conditions.'),
    'ai-brain':     ('AI Brain',       'AI Brain Guardian',     'Meta-vrstva nad systémem — state validator, expected state engine, self-healing, Gemini.'),
}

# Extra technical pages that exist but aren't built from <main> extraction.
# They appear on technicka-mapa.html as link cards only.
EXTRA_TECH = {
    'hardware-komplet': ('Kompletní hardware', 'Katalog všech 82 zařízení z živého Homey exportu — filtry, fotky, role, protokol, zóna.'),
    'dashboard':        ('Dashboard',          'Tři obrazovky, jeden systém. 1024×600 RPi kiosek, 1920×1080 notebook, 2880×1800 monitor.'),
}

# Reverse map: subpage id → parent pillar id (for is-active highlighting).
SUB_TO_PILLAR = {sub: p['id'] for p in PILLARS for sub in p['sub']}


# ─── HELPERS ──────────────────────────────────────────────────
def extract_main(html: str) -> str:
    """Extract everything between <main id="main"> and </main>."""
    m = re.search(r'<main id="main">\s*(.*?)\s*</main>', html, re.DOTALL)
    if not m:
        raise ValueError('no <main id="main">…</main> block found')
    return m.group(1)


def build_nav(active_id: str | None) -> str:
    """Build LEAN top-level navigation — 7 flat items, no mega-menu.

    active_id is either one of MAIN_NAV ids, a sub-page id, or 'home'.
    Sub-pages highlight their parent pillar in the strip.
    Technical sub-pages live on technicka-mapa.html, linked from footer.
    """
    # Resolve sub-page → its pillar for highlight purposes
    active_pillar = SUB_TO_PILLAR.get(active_id, active_id)

    items = []
    for item in MAIN_NAV:
        is_active = (item['id'] == active_id) or (item['id'] == active_pillar)
        attrs = []
        if is_active:
            attrs.append('class="is-active"')
            attrs.append('aria-current="page"')
        attr_str = (' ' + ' '.join(attrs)) if attrs else ''
        items.append(f'<li><a href="{item["href"]}"{attr_str}>{item["label"]}</a></li>')

    return '\n          '.join(items)


def page_template(active_id: str | None, page_title: str, lead: str, content: str) -> str:
    nav = build_nav(active_id)
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{lead}" />
  <meta name="theme-color" content="#0a0e14" />
  <title>{page_title} | SMART HOME</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <a href="#main" class="skip-link">Přeskočit na obsah</a>

  <header class="site-header" id="site-header">
    <div class="container header-inner">
      <a href="index.html" class="brand" aria-label="SMART HOME – home">
        <span class="brand-mark" aria-hidden="true"></span>
        <span class="brand-name">SMART<span class="brand-name-accent">HOME</span></span>
      </a>
      <nav class="primary-nav" aria-label="Hlavní navigace">
        <button class="nav-toggle" aria-expanded="false" aria-controls="nav-list">
          <span class="sr-only">Otevřít menu</span>
          <span class="nav-toggle-bars" aria-hidden="true"></span>
        </button>
        <ul id="nav-list" class="nav-list">
          {nav}
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
{content}
  </main>

  <!-- LIGHTBOX -->
  <div id="lightbox" class="lightbox" aria-hidden="true" role="dialog" aria-label="Zvětšený obrázek">
    <button class="lightbox-close" aria-label="Zavřít zvětšení">&times;</button>
    <img class="lightbox-img" src="" alt="" />
    <p class="lightbox-cap"></p>
  </div>

  <footer class="site-footer">
    <div class="container footer-inner">
      <p>© <span id="year"></span> SMART HOME projekt · Semily · Vyrobeno s ❤️ a script-first myšlením.</p>
      <p class="footer-meta">Veřejná prezentace · žádné API klíče · žádné lokální IP · žádné ovládání odtud.</p>
      <p class="footer-meta"><a href="technicka-mapa.html">Technická mapa →</a> · <a href="index.html">Domů</a></p>
    </div>
  </footer>

  <script src="script.js" defer></script>
</body>
</html>
'''


def hub_content(pillar: dict) -> str:
    """Build content for a NEW hub page (prozivani, pribeh)."""
    sub_cards = []
    for sub_id in pillar['sub']:
        label, _t, lead = SUBPAGES[sub_id]
        sub_cards.append(
            f'''      <a href="{sub_id}.html" class="home-card">
        <h3>{label}</h3>
        <p>{lead}</p>
        <span class="home-card-cta">Otevřít stránku →</span>
      </a>''')
    cards_html = '\n'.join(sub_cards)

    return f'''    <section id="{pillar['id']}" class="section section-hero hub-hero">
      <div class="container">
        <p class="eyebrow"><span class="status-dot" aria-hidden="true"></span>{pillar['icon']} Pilíř · {pillar['label']}</p>
        <h1 class="hero-title">{pillar['title']}</h1>
        <p class="hero-lead">{pillar['lead']}</p>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <header class="section-header">
          <p class="section-eyebrow">Obsah pilíře</p>
          <h2 class="section-title">Co tady najdeš</h2>
          <p class="section-lead">Pilíř {pillar['label']} sdružuje tematické stránky níže.</p>
        </header>
        <div class="home-grid">
{cards_html}
        </div>
      </div>
    </section>'''


# ─── TECHNICKA MAPA (full site index, replaces mega-menu surface) ─────
def technicka_mapa_content() -> str:
    """Build content for technicka-mapa.html — full index of every page,
    grouped by pillar.  Replaces the surface area lost from the mega-menu.
    """
    sections = []
    sections.append('''    <section class="section section-hero hub-hero">
      <div class="container">
        <p class="eyebrow"><span class="status-dot" aria-hidden="true"></span>🗺 Technická mapa</p>
        <h1 class="hero-title">Všechny stránky webu</h1>
        <p class="hero-lead">Kompletní rozcestník — každá podstránka, seskupená podle pilíře. Hlavní menu je úmyslně krátké; tady je všechno.</p>
      </div>
    </section>''')

    for p in PILLARS:
        if p['id'] == 'kontakt':
            continue
        sub_ids = list(p['sub'])
        # zarizeni pillar also surfaces hardware-komplet (extra tech page)
        extras_for_pillar = []
        if p['id'] == 'zarizeni':
            extras_for_pillar.append('hardware-komplet')
        if not sub_ids and not extras_for_pillar:
            continue
        cards = []
        for sub_id in sub_ids:
            if sub_id not in SUBPAGES:
                continue
            label, _t, lead = SUBPAGES[sub_id]
            cards.append(
                f'''      <a href="{sub_id}.html" class="home-card">
        <h3>{label}</h3>
        <p>{lead}</p>
        <span class="home-card-cta">Otevřít stránku →</span>
      </a>''')
        for ex_id in extras_for_pillar:
            if ex_id in EXTRA_TECH:
                label, lead = EXTRA_TECH[ex_id]
                cards.append(
                    f'''      <a href="{ex_id}.html" class="home-card">
        <h3>{label}</h3>
        <p>{lead}</p>
        <span class="home-card-cta">Otevřít stránku →</span>
      </a>''')
        cards_html = '\n'.join(cards)
        sections.append(f'''    <section class="section section-alt">
      <div class="container">
        <header class="section-header">
          <p class="section-eyebrow">{p['icon']} Pilíř</p>
          <h2 class="section-title">{p['label']}</h2>
          <p class="section-lead"><a href="{p['id']}.html">Otevřít hub →</a></p>
        </header>
        <div class="home-grid">
{cards_html}
        </div>
      </div>
    </section>''')

    # Standalones (Dashboard at top-level + Blog + Kontakt)
    standalones = [
        ('dashboard', '📊 Dashboard'),
        ('blog',      '📝 Blog'),
        ('kontakt',   '✉ Kontakt'),
    ]
    standalone_cards = []
    for sid, sicon in standalones:
        if sid in SUBPAGES:
            label, _t, lead = SUBPAGES[sid]
        elif sid == 'blog':
            label, lead = 'Blog', 'Pravidelné poznámky o tom, co se v systému změnilo.'
        elif sid == 'kontakt':
            label, lead = 'Kontakt / O projektu', 'Kdo, proč, stack.'
        else:
            continue
        standalone_cards.append(
            f'''      <a href="{sid}.html" class="home-card">
        <h3>{sicon} {label}</h3>
        <p>{lead}</p>
        <span class="home-card-cta">Otevřít stránku →</span>
      </a>''')
    sections.append(f'''    <section class="section section-alt">
      <div class="container">
        <header class="section-header">
          <p class="section-eyebrow">Samostatné</p>
          <h2 class="section-title">Top-level stránky</h2>
        </header>
        <div class="home-grid">
{chr(10).join(standalone_cards)}
        </div>
      </div>
    </section>''')

    return '\n\n'.join(sections)


# ─── BUILD ────────────────────────────────────────────────────
def build():
    written = []

    # 1) Re-template each existing sub-page (preserve <main> content).
    for sub_id, (_label, page_title, lead) in SUBPAGES.items():
        path = ROOT / f'{sub_id}.html'
        if not path.exists():
            print(f'⚠ skipping {sub_id}.html — file missing')
            continue
        try:
            existing = path.read_text(encoding='utf-8')
            content = extract_main(existing)
        except ValueError as e:
            print(f'⚠ {sub_id}: {e}')
            continue
        out = page_template(sub_id, page_title, lead, content)
        path.write_text(out, encoding='utf-8')
        written.append(path.name)

    # 2) Re-template existing pillar/standalone pages (zarizeni, blog, kontakt).
    for p in PILLARS:
        if not p.get('is_existing'):
            continue
        path = ROOT / f'{p["id"]}.html'
        if not path.exists():
            print(f'⚠ skipping {p["id"]}.html — file missing')
            continue
        existing = path.read_text(encoding='utf-8')
        content = extract_main(existing)
        out = page_template(p['id'], p['title'], p['lead'], content)
        path.write_text(out, encoding='utf-8')
        written.append(path.name)

    # 3) Build NEW hub pages (prozivani, pribeh).
    for p in PILLARS:
        if p.get('is_existing'):
            continue
        if p['id'] in ('blog', 'kontakt'):
            continue  # standalones, already handled above
        path = ROOT / f'{p["id"]}.html'
        content = hub_content(p)
        out = page_template(p['id'], p['title'], p['lead'], content)
        path.write_text(out, encoding='utf-8')
        written.append(path.name + ' (NEW hub)')

    # 4) Rebuild index.html — preserve hero from existing index, replace cards.
    index_path = ROOT / 'index.html'
    existing_index = index_path.read_text(encoding='utf-8')
    main_block = extract_main(existing_index)

    # Extract hero section (everything from `<section id="home"` to its </section>)
    hero_match = re.search(
        r'<section id="home"[^>]*>.*?</section>\s*(?=<section|\Z)',
        main_block, re.DOTALL,
    )
    if hero_match:
        hero = hero_match.group(0).rstrip()
    else:
        # fallback minimal hero
        hero = '''<section id="home" class="section section-hero">
      <div class="container hero-inner">
        <div class="hero-text">
          <h1 class="hero-title">Smart home jako <span class="grad-text">živý organismus</span></h1>
        </div>
      </div>
    </section>'''

    # Build pillar cards (4 pillars, no Kontakt — that stays nav-only).
    home_cards_html_parts = []
    for p in PILLARS:
        if p['id'] == 'kontakt':
            continue
        home_cards_html_parts.append(
            f'''      <a href="{p['id']}.html" class="home-card home-card-pillar">
        <span class="home-card-icon" aria-hidden="true">{p['icon']}</span>
        <h3>{p['label']}</h3>
        <p>{p['lead']}</p>
        <span class="home-card-cta">Otevřít pilíř →</span>
      </a>''')
    home_cards_html = '\n'.join(home_cards_html_parts)

    new_index_content = f'''    {hero}

    <section class="section section-alt" id="navigace">
      <div class="container">
        <header class="section-header">
          <p class="section-eyebrow">Navigace</p>
          <h2 class="section-title">Co tě zajímá?</h2>
          <p class="section-lead">Web je rozdělený do čtyř pilířů. Vyber, kam chceš.</p>
        </header>
        <div class="home-grid home-grid-pillars">
{home_cards_html}
        </div>
        <p class="home-foot">Hledáš kontakt? <a href="kontakt.html">O projektu →</a></p>
      </div>
    </section>'''

    out = page_template(
        'home',
        'SMART HOME — projekt Luďka Budínského',
        'Domácnost řízená script-first architekturou nad Homey Pro 2026. Garsonka v přízemí, 79 zařízení, 100+ skriptů, vlastní AI Brain Guardian.',
        new_index_content,
    )
    index_path.write_text(out, encoding='utf-8')
    written.append('index.html')

    # 5) Build / rebuild technicka-mapa.html — full site index page.
    tm_path = ROOT / 'technicka-mapa.html'
    tm_content = technicka_mapa_content()
    tm_out = page_template(
        'technicka-mapa',
        'Technická mapa — všechny stránky webu',
        'Kompletní rozcestník — každá podstránka, seskupená podle pilíře. Hlavní menu je úmyslně krátké; tady je všechno.',
        tm_content,
    )
    tm_path.write_text(tm_out, encoding='utf-8')
    written.append('technicka-mapa.html')

    # Report (ASCII-safe for Windows cp1250 console)
    for n in written:
        print(f'[OK] {n}')
    print(f'\nBuild complete: {len(written)} files written.')


if __name__ == '__main__':
    build()
