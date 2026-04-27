# SMART HOME — public website

Statické webové stránky o projektu **SMART HOME** (Homey Pro 2026, Semily).
Hostováno na **GitHub Pages**, čistá HTML/CSS/JS, žádný backend.

**Live URL** (po enable Pages): `https://<username>.github.io/smart-home-website/`

---

## 📁 Struktura

```
smart-home-website/
├── index.html                  ← single-page se všemi sekcemi
├── style.css                   ← premium dark theme
├── script.js                   ← mobile menu, scroll, anim. countery
├── posts/
│   └── dashboard-v7.html       ← ukázkový blog post
├── assets/
│   └── screenshots/            ← sem nahrávat screenshoty dashboardů
│       └── .gitkeep
└── README.md                   ← tento soubor
```

---

## 🚀 Postup nasazení na GitHub Pages

### 1. Vytvoř GitHub repo

**Přes web** (https://github.com/new):
- Name: `smart-home-website`
- Public ✅
- **Bez** README/gitignore/license (máš je tu lokálně)

**Přes `gh` CLI** (rychlejší):
```bash
gh repo create smart-home-website --public --source=. --remote=origin --push
```

### 2. Push (pokud jsi nepoužil `gh repo create --push`)

```bash
cd <složka-s-projektem>
git init -b main
git add .
git commit -m "Initial public website"
git remote add origin git@github.com:<username>/smart-home-website.git
git push -u origin main
```

### 3. Zapni GitHub Pages

**Web UI**:
1. Otevři repo → **Settings** → **Pages** (levý sidebar)
2. **Source**: `Deploy from a branch`
3. **Branch**: `main`, **Folder**: `/ (root)`
4. **Save**
5. Po ~1 minutě Pages vypíše: `Your site is live at https://<username>.github.io/smart-home-website/`

**`gh` CLI** (alternativa):
```bash
gh api -X POST "repos/<username>/smart-home-website/pages" \
  -f "source[branch]=main" \
  -f "source[path]=/"
```

### 4. Custom doména (volitelné)

Settings → Pages → **Custom domain** → zadej `smart-home.example.cz` →
v DNS přidej `CNAME` na `<username>.github.io`.

---

## ✏️ Jak přidávat nové příspěvky

### A) Vytvoř HTML soubor

V `posts/` vytvoř `posts/<slug>.html` (zkopíruj jako šablonu existující
`dashboard-v7.html` a uprav obsah).

Doporučený slug: `kebab-case-bez-diakritiky.html`

### B) Přidej kartu do `index.html`

Otevři `index.html`, najdi sekci `<!-- BLOG -->` (cca řádek 130) a do
`<div class="post-grid">` přidej **na začátek** novou kartu (nejnovější
nahoře):

```html
<article class="post-card">
  <a href="posts/<slug>.html" class="post-card-link" aria-label="Název příspěvku">
    <div class="post-card-thumb">
      <span class="post-card-badge">KATEGORIE</span>
    </div>
    <div class="post-card-body">
      <p class="post-card-meta">DD. měsíce YYYY · X min čtení</p>
      <h3 class="post-card-title">Název příspěvku</h3>
      <p class="post-card-excerpt">Krátký excerpt 1–2 věty.</p>
      <span class="post-card-cta">Číst příspěvek →</span>
    </div>
  </a>
</article>
```

### C) Commit + push

```bash
git add posts/<slug>.html index.html
git commit -m "blog: <název příspěvku>"
git push
```

GitHub Pages automaticky deployne během ~1 minuty.

---

## 📸 Kam dávat screenshoty

Všechny obrázky jdou do `assets/screenshots/`.

**Doporučení**:
- Formát: `PNG` (lossless) nebo `JPG` (fotografické)
- Šířka: max **1600px** (pro retina dashboardy stačí, větší zbytečně tloustnou repo)
- Naming: `dashboard-v7-2880x1800.png`, `kuchyne-detail.jpg`, …
- **NIKDY neupload** screenshoty obsahující IP adresy, tokeny, hesla, IBANy,
  jména rodinných příslušníků, zařízení, která lze identifikovat polohou.

**Jak vložit do stránky**:

V Dashboard sekci `index.html` (sekce `<!-- DASHBOARD -->`) najdi
`<div class="gallery-empty">…</div>` a nahraď za:

```html
<div class="gallery-grid">
  <figure class="gallery-item">
    <img src="assets/screenshots/dashboard-v7-2880x1800.png"
         alt="Dashboard V7 master 2880×1800" loading="lazy" />
    <figcaption>Master 32" — 2880 × 1800</figcaption>
  </figure>
  <figure class="gallery-item">
    <img src="assets/screenshots/dashboard-v7-1920x1080.png"
         alt="Dashboard V7 notebook 1920×1080" loading="lazy" />
    <figcaption>Notebook 14" — 1920 × 1080</figcaption>
  </figure>
  <figure class="gallery-item">
    <img src="assets/screenshots/dashboard-v7-1024x600.png"
         alt="Dashboard V7 RPi kiosek 1024×600" loading="lazy" />
    <figcaption>RPi kiosek — 1024 × 600</figcaption>
  </figure>
</div>
```

A do `style.css` přidej (na konec):

```css
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}
.gallery-item {
  margin: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
.gallery-item img { width: 100%; height: auto; }
.gallery-item figcaption {
  padding: 12px 16px;
  font-size: 13px;
  color: var(--text-soft);
  border-top: 1px solid var(--border);
}
```

---

## 🧭 Jak aktualizovat menu

Menu je v `index.html` — sekce `<ul id="nav-list" class="nav-list">`.

Přidat položku:
```html
<li><a href="#nove-id">Nová sekce</a></li>
```

Pak přidat odpovídající `<section id="nove-id">…</section>` do `<main>`.

Nezapomeň upravit pořadí v `<header>` ve stejném pořadí, v jakém jsou sekce
pod sebou — JS observer pak správně highlightne aktivní položku při scrollu.

---

## 🎨 Customizace barev

Všechny barvy jsou v `style.css` v `:root` (řádek 5–25). Změna jednoho
custom property se propaguje napříč celým webem:

```css
--accent: #00e5ff;        /* primární akcentová barva */
--accent-2: #7c3aed;      /* gradient partner (fialová) */
--bg: #0a0e14;            /* hlavní pozadí */
--text: #e8eef5;          /* hlavní text */
```

---

## 🔐 Security checklist před každým commitem

- [ ] **Žádné API klíče** v HTML/JS (Homey API, Sheets, OWM, Anthropic, …)
- [ ] **Žádné lokální IP** (192.168.x.x, 100.x.x.x Tailscale)
- [ ] **Žádné domény / endpointy** vašich služeb (Apps Script, Homey REST)
- [ ] **Žádné screenshoty** s viditelnými výpisy účtů, IBANy, jmény
- [ ] **Žádné automatizační logy** s timestampy a polohou pohybu

Tento web je **veřejná prezentace projektu**, ne ovládací panel.
Nikdy odsud nelze ovládat zařízení v domě, nikdy zde nejsou citlivá data.

---

## 🛠 Lokální preview

Nejjednodušší (Python ≥ 3):
```bash
cd smart-home-website
python -m http.server 8000
# otevři http://localhost:8000 v browseru
```

Nebo jen otevři `index.html` dvojklikem — relativní cesty fungují i bez serveru
(jen blog post linky musí být klikatelné z file:// — moderní browsery to umí).

---

## 📝 Tech stack

- **HTML5** — semantický
- **CSS3** — custom properties, grid, flexbox, backdrop-filter
- **Vanilla JS** — bez frameworků, bez build kroku
- **Google Fonts** — Inter + JetBrains Mono (přes CDN)
- **GitHub Pages** — bez build pipeline, deploy = git push

Žádný npm, žádný webpack, žádná závislost. `git push` → ~60s → live.

---

## 📄 Licence

Web je osobní prezentace. Pokud chceš použít CSS / strukturu jako šablonu pro
vlastní projekt, klidně forkni. Texty a obrazový obsah ©  Luděk Budínský.
