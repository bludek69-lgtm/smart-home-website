"""Split index.html sections into individual subpages.

Reads current index.html, extracts each <section id="X"> block, and writes
a standalone page <X>.html with shared header/footer.

After running, index.html is replaced with a homepage that has hero +
summary cards linking to the subpages.

Run from website root:
  py -3.14 _build_pages.py
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / 'index.html'

# Page metadata: id → (filename, nav label, page title, hero subtitle)
PAGES = [
    ('historie',     'Historie',      'Historie projektu',          'Jak systém vznikal — od první žárovky k AI Brain Guardian.'),
    ('hardware',     'Hardware',      'Hardware',                    'Homey Pro 2026, bezdrátové protokoly, klíčová zařízení.'),
    ('funkce',       'Funkce',        'Funkce',                      'Topení, ranní rutina, příchod/odchod, fyzická tlačítka, koupelna, světelný cyklus, robot vysavač.'),
    ('infra',        'Infrastruktura','Infrastruktura',              'Raspberry Pi, Home Assistant, GitHub repos, GitHub Actions.'),
    ('dashboard',    'Dashboard',     'Dashboard',                   'Tři obrazovky, jeden systém. 1024×600 RPi kiosek, 1920×1080 notebook, 2880×1800 monitor.'),
    ('zarizeni',     'Zařízení',      'Zařízení',                    'Co všechno systém řídí — světla, topení, audio, senzory, kamery, rolety, AI.'),
    ('architektura', 'Architektura',  'Architektura',                'Script-first princip a 12 pravidel co drží systém pohromadě.'),
    ('vyzvy',        'Výzvy',         'Výzvy',                       'Reálné problémy které jsem řešil — Zigbee battery, SIGABRT, ghost values, audio race conditions.'),
    ('ai-brain',     'AI Brain',      'AI Brain Guardian',           'Meta-vrstva nad systémem — state validator, expected state engine, self-healing, Gemini.'),
    ('blog',         'Blog',          'Blog a novinky',              'Pravidelné poznámky o tom, co se v systému změnilo, co se rozbilo a jak se to fixovalo.'),
    ('kontakt',      'Kontakt',       'O projektu',                  'Kdo, proč, stack.'),
]

# Read source
src = INDEX.read_text(encoding='utf-8')

def extract_section(html: str, sec_id: str) -> str:
    """Extract <section id="sec_id" ...>...</section> from html."""
    # Find opening tag
    m = re.search(rf'<section id="{re.escape(sec_id)}"[^>]*>', html)
    if not m:
        raise ValueError(f'section id="{sec_id}" not found')
    start = m.start()
    # Walk forward to find matching closing </section>
    depth = 0
    i = start
    while i < len(html):
        if html[i:i+9] == '<section ' or html[i:i+9] == '<section>':
            depth += 1
            i += 9
        elif html[i:i+10] == '</section>':
            depth -= 1
            i += 10
            if depth == 0:
                return html[start:i]
        else:
            i += 1
    raise ValueError(f'unbalanced section for id="{sec_id}"')

def build_nav(active_id: str | None) -> str:
    """Build <ul> navigation pointing to subpages."""
    items = ['<li><a href="index.html"' + (' class="is-active"' if active_id is None else '') + '>Home</a></li>']
    for sid, label, _t, _l in PAGES:
        cls = ' class="is-active"' if sid == active_id else ''
        items.append(f'<li><a href="{sid}.html"{cls}>{label}</a></li>')
    return '\n          '.join(items)

def page_template(sec_id: str, title: str, lead: str, content: str) -> str:
    nav = build_nav(sec_id)
    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{lead}" />
  <meta name="theme-color" content="#0a0e14" />
  <title>{title} | SMART HOME</title>
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
    </div>
  </footer>

  <script src="script.js" defer></script>
</body>
</html>
'''

# Generate each subpage
for sec_id, label, page_title, lead in PAGES:
    try:
        content = extract_section(src, sec_id)
    except ValueError as e:
        print(f'⚠ {sec_id}: {e}')
        continue
    out = page_template(sec_id, page_title, lead, '    ' + content)
    target = ROOT / f'{sec_id}.html'
    target.write_text(out, encoding='utf-8')
    print(f'✓ {target.name} ({len(out)} bytes)')

# Build new homepage (index.html)
hero = extract_section(src, 'home')

# Page summary cards
cards_html = '\n'.join([
    f'''      <a href="{sid}.html" class="home-card">
        <h3>{label}</h3>
        <p>{lead}</p>
        <span class="home-card-cta">Otevřít stránku →</span>
      </a>'''
    for sid, label, _t, lead in PAGES
])

new_index = page_template(
    None,
    'SMART HOME — projekt Luďka Budínského',
    'Domácnost řízená script-first architekturou nad Homey Pro 2026. Garsonka v přízemí, 77 zařízení, 110 skriptů, vlastní AI Brain Guardian.',
    f'''    {hero}

    <section class="section section-alt" id="navigace">
      <div class="container">
        <header class="section-header">
          <p class="section-eyebrow">Navigace</p>
          <h2 class="section-title">Co tě zajímá?</h2>
          <p class="section-lead">Web je rozdělený do tematických stránek. Vyber, kam chceš.</p>
        </header>
        <div class="home-grid">
{cards_html}
        </div>
      </div>
    </section>'''
).replace('class="is-active"', '')  # home doesn't highlight any nav item

# Special: index nav should highlight Home
new_index = new_index.replace(
    '<li><a href="index.html">Home</a></li>',
    '<li><a href="index.html" class="is-active">Home</a></li>'
)

(ROOT / 'index.html').write_text(new_index, encoding='utf-8')
print(f'✓ index.html rewritten ({len(new_index)} bytes)')
print()
print('Build complete. Next: append home-card CSS to style.css')
