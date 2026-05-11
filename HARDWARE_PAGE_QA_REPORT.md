# HARDWARE PAGE QA REPORT (2026-05-11)

**Scope:** `hardware-komplet.html` v2 (post-refresh)
**Audit input:** `HARDWARE_PAGE_AUDIT.md` (Phase 2)
**Build pipeline:** `_build_hardware_verified.py` → `data/hardware_inventory_verified.json` → `_build_hardware_page_v2.py` → `hardware-komplet.html`

---

## 11.1 Datová kontrola

| Kontrola | Výsledek |
|---|---|
| Počet zařízení vs Homey export | ✅ **79 = 79** (live `homey_devices_2026-05-11.json`) |
| Matter zařízení správně klasifikovaná | ✅ **8** (1 physical Meross MSS315 + 7 virtual bridge) |
| Žádné duplicity v primárních kartách | ✅ — Matter + UNKNOWN sekce mají `hw-card-dup` flag (nezapočítávají se do counts) |
| Každé zařízení má zónu | ✅ 79 / 79 (11 zón vč. "nefunkcni" legacy) |
| Každé zařízení má protocol nebo unknown | ✅ 79 / 79 mají non-null protocol, 0× UNKNOWN |
| Každý obrázek má zdroj | ✅ 5 verified local + 74 placeholder s kategorií ikonou; `hardware_image_sources.csv` má `source_type` per řádek |
| UNKNOWN položky jasně označené | ✅ 7 položek v sekci "❓ Zařízení k ověření" |

### Stats po refreshe

```
Protokoly: Zigbee 39, Z-Wave 10, Wi-Fi (Cloud) 10, Matter 7, Zigbee (Hue Bridge) 5,
           Google Cast (Wi-Fi) 3, Wi-Fi (HA) 2, Cloud (web) 1, Wi-Fi 1, Wi-Fi (LAN) 1
Matter:    yes 8 (class: physical 1, virtual_bridge 7)
Verification: verified 72, partial 7, unknown 0
Automation:   yes 37, no 42
Dashboard:    yes 38, no 41
Energy:       yes 11, partial 10, no 58
```

---

## 11.2 Vizuální kontrola

### Screenshoty captured

| Viewport | Soubor | Velikost |
|---|---|---:|
| **Desktop 1920×1080** | `_qa/screenshots/hardware/desktop_1920x1080_01_top.png` | 140 KB |
| | `desktop_1920x1080_02_filters.png` | 112 KB |
| | `desktop_1920x1080_03_matter.png` | 109 KB |
| | `desktop_1920x1080_04_table.png` | 185 KB |
| | `desktop_1920x1080_05_unknown.png` | 61 KB |
| **Notebook 1366×768** | `notebook_1366x768_01_top.png` | 114 KB |
| | `notebook_1366x768_02_filters.png` | 102 KB |
| | `notebook_1366x768_03_matter.png` | 93 KB |
| | `notebook_1366x768_04_table.png` | 136 KB |
| | `notebook_1366x768_05_unknown.png` | 66 KB |
| **Mobile 390×844** | `mobile_390x844_01_top.png` | 58 KB |
| | `mobile_390x844_02_filters.png` | 30 KB |
| | `mobile_390x844_03_matter.png` | 39 KB |
| | `mobile_390x844_04_table.png` | 50 KB |
| | `mobile_390x844_05_unknown.png` | 2 KB |

**Total: 15 screenshots × 3 viewports.**

### Vizuální kontroly

| Kontrola | Výsledek |
|---|---|
| Žádný horizontální overflow | ✅ 1920 / 1366 / 390 — všechny `overflow_x: False` |
| Karty mají správnou velikost | ✅ aspect-ratio 16:10 photos, jednotná výška via flexbox |
| Tabulka čitelná | ✅ desktop full-width, mobile horizontal scroll via `overflow-x:auto`, sticky header |
| Filtry fungují | ✅ ověřeno v JS test (search input + 6 dropdownů + reset) |
| Obrázky nedeformované | ✅ `object-fit: contain` + placeholder ikony jednotné |
| Mobilní verze použitelná | ✅ 1-column grid, vertical filter stack, table horizontal scroll |
| Filtry nerozbijí layout | ✅ flex-wrap na controls baru |
| KPI cards na malých displejích | ✅ 390px → 2-col grid; 1024px → 3-4 col; 1920px → 10-col single row |

---

## 11.3 Funkční kontrola

| Test | Postup | Výsledek |
|---|---|---|
| Vyhledávání | typing "snzb" → filtruje na SNZB-* zařízení | ✅ (substring match na name+model+brand+caps) |
| Filtr zóna | dropdown → "Kitchen" → ukáže 7 kuchyňských | ✅ |
| Filtr protocol | "Z-Wave" → 10 zařízení | ✅ |
| Filtr brand | "Fibaro" → 5 (FGT-001, FGS-214, FGMS-001, FGS-223, FGWOF-011) | ✅ |
| Filtr Matter | "yes" → 8 Matter | ✅ |
| Filtr automation | "yes" → 37 zařízení v Flow JSON | ✅ |
| Filtr energy | "yes" → 11 měřících | ✅ |
| Reset tlačítko | klik → všechny dropdowny + search = "" | ✅ |
| Card → Table toggle | klik "📋 Tabulka" → cards hide, table show | ✅ |
| Table → Card toggle | klik "📇 Karty" → naopak | ✅ |
| Empty section hide | filter "Matter=yes" → ostatní zone sekce zmizí | ✅ |
| Count update | filter aktivní → display "X / 79" reflektuje filtrovaný počet | ✅ |
| Photo fallback | 74/79 chybí soubor → placeholder s kategorií ikonou | ✅ |
| Mobile responsive | 390px → vertikální stack, žádný overflow | ✅ |
| Print stylesheet | media print → controls hide, cards print-friendly | ✅ |
| JS errors | 0 / 3 viewports | ✅ |

---

## 11.4 SEO & accessibility

| Atribut | Status |
|---|---|
| `<title>` | ✅ "Kompletní hardware chytré domácnosti \| SMART HOME Semily" |
| `<meta name="description">` | ✅ "Přesný přehled 79 zařízení... 8× Matter..." |
| `<meta property="og:title">` | ✅ |
| `<meta property="og:description">` | ✅ |
| H1 / H2 / H3 hierarchy | ✅ H1 hero, H2 sekce, H3 cards |
| `alt` text na obrázcích | ✅ display_name jako alt |
| ARIA labels na filtry | ✅ `aria-label` na search + dropdowns |
| ARIA `role="tablist"` na mode toggle | ✅ `aria-pressed` synchronizováno |
| Keyboard navigable | ✅ všechny controls jsou native `<select>` / `<input>` / `<button>` |
| Print-friendly | ✅ `@media print` — controls hidden, cards break-inside avoid |

---

## 11.5 Compliance s prompt zákazy

| Zákaz | Status |
|---|---|
| Žádné vymyšlené zařízení | ✅ — všech 79 z live API |
| Žádný odhad protocol | ✅ — protocol vždy z driverId pattern (ne dojem) |
| Matter neover jen jedno zařízení | ✅ — 8 zařízení, kategorizováno physical/virtual |
| Žádné generické fake obrázky | ✅ — 74/79 placeholder s ikonou (jasně označeno) |
| Žádné hotlinky z cizích webů | ✅ — všechny image_file lokální nebo placeholder |
| Žádný redesign celého webu | ✅ — jen hardware-komplet.html + build skripty |
| Žádné změny dashboardu | ✅ |
| Žádné změny Homey systému | ✅ — read-only refetch |
| Žádné změny Flow / scriptů | ✅ |
| Žádné změny účetní knihy | ✅ |
| Žádný reklamní katalog | ✅ — neutrální popis, žádné "nejlepší smart home" |

---

## 11.6 Compliance s normalizovanými hodnotami

| Hodnota | Použito v inventory | Status |
|---|---|---|
| yes / no | `used_in_automation`, `used_in_dashboard` (+ `unknown` fallback) | ✅ |
| yes / no / partial | `energy_measured` | ✅ (partial pro `energyObj.W` bez `measure_power` cap) |
| yes / no | `matter_device` | ✅ |
| verified / partial / unknown | `verification_status` | ✅ |
| physical / virtual_bridge / no | `matter_class` (extra granularita) | ✅ |

Žádné `ano/ne`, `true/false`, `zapnuto/vypnuto` v inventory.

---

## 12 Výstupní soubory (per prompt §12)

| # | Soubor | Status |
|---|---|---|
| 1 | `HARDWARE_PAGE_AUDIT.md` | ✅ |
| 2 | `data/hardware_inventory_verified.json` | ✅ (86 KB, 79 položek, 22 polí schema) |
| 3 | `hardware_image_sources.csv` | ✅ (79 řádků s `source_type` + `license_status`) |
| 4 | `hardware-komplet.html` (refactored) | ✅ (191 KB) |
| 5 | `assets/photos/` (existing 5 + 74 placeholder) | ✅ (Wave A pending user) |
| 6 | `_qa/screenshots/hardware/` (15 PNG) | ✅ |
| 7 | `HARDWARE_PAGE_QA_REPORT.md` | ✅ (tento soubor) |
| 8 | `HARDWARE_PAGE_CHANGELOG.md` | ✅ |

---

## Verdikt

| Kategorie | Status |
|---|---|
| **Datová správnost** | ✅ READY |
| **Vizuální kvalita** | ✅ READY (3 viewports verified, 0 overflow, 0 JS errors) |
| **Funkční kompletnost** | ✅ READY (7 filtrů + 2 mode + reset všechny fungují) |
| **SEO** | ✅ READY |
| **Bezpečnost** | ✅ READY (žádné UUID/IP/token v public) |
| **Compliance** | ✅ READY (žádné fake / hotlink / Homey změny) |

**Stránka je připravena k publikování.** Po commit + push → GitHub Pages auto-deploy.
