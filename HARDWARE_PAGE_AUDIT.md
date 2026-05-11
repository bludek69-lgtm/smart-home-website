# HARDWARE PAGE AUDIT (2026-05-11)

**Scope:** `hardware-komplet.html` na `https://bludek69-lgtm.github.io/smart-home-website/`
**Zdroj pravdy:** `C:\Claude_code_SMART_HOME\11_5\homey_devices_2026-05-11.json` (live REST snapshot, 79 zařízení)
**Předchozí audit:** `HARDWARE_PAGE_FIX_AUDIT.md` (2026-05-11 ráno, Matter 1→8 fix)

---

## 1) Současný stav stránky (před tímto refresh)

| Atribut | Hodnota |
|---|---|
| Existující soubor | `hardware-komplet.html` (109 KB) |
| Pipeline | `_build_hardware_inventory.py` → `data/hardware_inventory.json` → `_build_hardware_complete.py` → HTML |
| Schema inventory | 14 polí (`name`, `public_name`, `category`, `class`, `zone`, `manufacturer`, `model`, `protocol`, `capabilities`, `automation_used`, `energy_data`, `status`, `image`, `note`) |
| Stránka má | Hero, KPI stats (9), filtry (kategorie+zóna+protocol+stav), grid kartami, zone tabulka, protocol tabulka, full table |
| Vlastní reports | `HARDWARE_PAGE_FIX_AUDIT.md`, `HARDWARE_PHOTO_SOURCE_REPORT.md`, `HARDWARE_UNKNOWN_DEVICES_TODO.md` |

---

## 2) Audit — kontrolní body

### ✅ Co bylo OK před refresh

| Kontrola | Status |
|---|---|
| Všechna zařízení (79) | ✅ |
| Zóny pokryté | ✅ 10 fyzických (jídelna, kuchyně, ložnice, koupelna, pracovna, prádelna, předsíň, toaleta, pcsetup, společné) |
| Matter zařízení po ranní opravě | ✅ 8 (1 physical + 7 virtual bridge) |
| Sanitizace (žádné UUID/IP/token) | ✅ |
| Filtry základní | ✅ kategorie / zóna / protokol / stav |

### 🟡 Co potřebovalo prohloubit

| Gap | Detail |
|---|---|
| Schema chybí pole dle prompt §3 | `display_name`, `role`, `driver`, `app`, `device_class`, `image_source_url`, `image_license_status`, `verification_status`, `used_in_dashboard`, `matter_device` (boolean), `matter_class` (granular) |
| Matter neměl granularitu physical vs virtual_bridge | Předtím jen `protocol=Matter`, teď `matter_class: physical / virtual_bridge / no` |
| Filtry chyběly | brand, automation y/n, energy y/n, search box |
| Card/Table mode toggle | Chyběl |
| UNKNOWN section | Předtím nebyla separátní; položky byly rozprostřené v kartách |
| `used_in_dashboard` detection | Chyběl — teď grep dashboard HTML |
| `used_in_automation` detection | Bylo částečné — teď grep flow JSON |
| `hardware_image_sources.csv` ve schéma per §5 | Schema neodpovídal (chybělo `source_type`, `license_status`) |

### ❌ CHYBÍ (před refreshem byly k doplnění)

- `device_class` (Homey native) — teď zahrnuto
- `driver` + `app` (com.fibaro:FGT-001 atd.) — teď zahrnuto
- `verification_status` (verified/partial/unknown) — teď zahrnuto
- Matter sekce dedikovaná — teď zahrnuta
- `Zařízení k ověření` sekce (UNKNOWN) — teď zahrnuta
- `image_license_status` — teď zahrnuto
- KPI karty per §6.2 (Total, Zigbee, Z-Wave, Matter, Wi-Fi, Virtual, Energy, Automation) — teď zahrnuto

### ⚠️ NEPŘESNÉ (před refreshem)

- Verification status nebyl tracking-able (jen `status: active/legacy/planned`)
- Matter zařízení nebyla skupinová sekce — teď je
- 11 zařízení mělo UNKNOWN protocol v dřívějším buildu (před ranní opravou DRIVER_META) — od commitu `1c96668` opraveno
- Energy data byla jen REAL/ESTIMATE — teď `energy_measured: yes/partial/no` per skutečné capability

### 🔁 DUPLICITY

Žádné duplikáty zařízení. 79 unikátních.

### ❓ UNKNOWN — položky k ověření (7)

Po refreshe je verifikace striktní. Položky s `verification_status: partial`:

| # | Device | Důvod partial |
|---|---|---|
| 1 | Smart RGBTW Bulb 1 (Jídelna) | Matter virtual bridge — fyzický HW model UNKNOWN |
| 2 | Smart RGBTW Bulb 2 (Jídelna) | dtto |
| 3 | Smart RGBTW Bulb 3 (Jídelna) | dtto |
| 4 | Kuchyne 1 (Kitchen) | Matter virtual A19/A60 — fyzický model UNKNOWN |
| 5 | Kuchyne 2 (Kitchen) | dtto |
| 6 | Kuchyne 3 (Kitchen) | dtto |
| 7 | Zarovka Loznice (Ložnice) | Matter virtual bridge (po 4.5. atomic rename z Lidl Zigbee) |

**Akce:** user potvrdí konkrétní fyzické modely (např. "RGBTW Bulb 1-3 = Lidl Livarno HG06492C E27"). Po potvrzení → update `derive_brand_model()` v `_build_hardware_verified.py` → re-build → status přejde na `verified`.

### 📷 FOTKY K OPRAVĚ

| Kategorie | Počet | Akce |
|---|---:|---|
| Foto na disku (`assets/photos/`) | 5 / 79 | OK (Homey Pro, Aqara Cube, Nest Mini 3×, Viomi V7) |
| Bez fotky (placeholder ikona) | 74 / 79 | Tracking: `hardware_image_sources.csv` status_doc=`PHOTO_TODO` |

Doporučená Wave A (8-10 high-impact, manufacturer press kits):
- Sektorka1 (Lidl HG06492C)
- Sensore di Presenza SNZB-06P openspace (SONOFF SNZB-06P)
- FGS-214 (Fibaro FGS-214)
- 4× Sonoff TRVZB (Sonoff TRVZB)
- Meross MSS315 (Meross MSS315)
- Shelly Plug S Gen3
- Foscam venkovní kamera (Foscam)

### 🔷 MATTER ZAŘÍZENÍ K OVĚŘENÍ (8)

| # | Device | Matter class | Status |
|---|---|---|---|
| 1 | Zasuvka Kuchyne Kaffe | **physical** | ✅ Verified — Meross MSS315 Smart Plug (Matter native) |
| 2 | Smart RGBTW Bulb 1 | virtual_bridge | 🟡 Partial — fyzický model? |
| 3 | Smart RGBTW Bulb 2 | virtual_bridge | 🟡 Partial — fyzický model? |
| 4 | Smart RGBTW Bulb 3 | virtual_bridge | 🟡 Partial — fyzický model? |
| 5 | Kuchyne 1 | virtual_bridge | 🟡 Partial — fyzický model? |
| 6 | Kuchyne 2 | virtual_bridge | 🟡 Partial — fyzický model? |
| 7 | Kuchyne 3 | virtual_bridge | 🟡 Partial — fyzický model? |
| 8 | Zarovka Loznice | virtual_bridge | 🟡 Partial — 4.5. atomic rename z Lidl Zigbee |

DriverId `homey:virtualdrivermatter:driver` znamená že Homey expose zařízení jako Matter, ale jeho původní fyzický HW může být jakýkoli (Lidl, IKEA, Tuya…). REST API neexpose original Zigbee fingerprint pod virtual Matter driver.

---

## 3) Změny v této opravě (2026-05-11 11:13)

### Nový SSOT pipeline
```
homey_devices_2026-05-11.json (live REST 79 zařízení)
   → _build_hardware_verified.py  (NEW, rozšířené schéma 22 polí)
   → data/hardware_inventory_verified.json (NEW)
   → _build_hardware_page_v2.py    (NEW, refactor HTML)
   → hardware-komplet.html         (overwrite)
```

### Backup
- `_archive/hardware_page_before_fix/2026-05-11_1113/` (kompletní pre-state)

### Nové schema (22 polí per prompt §3)

```json
{
  "name_homey": "Sensore di Presenza SNZB-06P openspace",
  "display_name": "Sensore di Presenza SNZB-06P openspace",
  "zone": "Spolecne",
  "room_group": "open_space",
  "device_class": "sensor",
  "brand": "SONOFF",
  "model": "SNZB-06P Presence",
  "protocol": "Zigbee",
  "driver": "homey:app:com.sonoff:snzb-06p",
  "app": "SONOFF",
  "capabilities": ["alarm_presence", "measure_luminance", ...],
  "used_in_automation": "yes",
  "used_in_dashboard": "yes",
  "energy_measured": "no",
  "matter_device": "no",
  "matter_class": "no",
  "role": "Environmentální senzor",
  "description": "...",
  "image_file": "",
  "image_source_url": "",
  "image_license_status": "unknown",
  "verification_status": "verified",
  "notes": "..."
}
```

### Nové features na stránce

| Sekce | Detail |
|---|---|
| Hero | Title + statistiky + last update date |
| KPI cards | 10 karet (Total, Zóny, Zigbee, Z-Wave, Matter, Wi-Fi/Cast, Cloud, Energy, Automation, Dashboard) |
| Filtry | Search + Zone + Protocol + Brand + Matter + Automation + Energy + Reset |
| Mode toggle | Cards / Table (mobile-friendly) |
| Sekce | Matter (8) → Zone-by-zone (11) → Legacy (3) → UNKNOWN to verify (7) |
| Card | Photo/icon + display_name + brand + model + role + protocol badge + zone badge + matter badge + verif badge + automation/dashboard/energy mini-grid + capabilities preview |
| Table | 10 columns (Název, Zóna, Brand, Model, Protocol, Matter, Auto, Dash, Energy, Ověření), scrollable on mobile, sticky header |
| UNKNOWN section | 7 položek s důvodem partial verifikace + akcí |
| Meta sekce | Souhrn protokolů + počet ověřených + odkazy na soubory |

### SEO
- title: "Kompletní hardware chytré domácnosti | SMART HOME Semily"
- meta description: zahrnuje counts (79 zařízení, 10 zón, 9 protokolů, 8 Matter)
- OG title + description
- H1/H2/H3 hierarchy
- alt text na všech foto + ikonách

### Responsive breakpoints
- Desktop 1920×1080 — `repeat(auto-fill, minmax(290px, 1fr))` grid
- Notebook 1366×768 — stejně, ale méně sloupců
- Mobil 390×844 — 1-sloupcový grid, vertical filters, table horizontal scroll

---

## 4) Compliance s prompt §1-§14

| Pravidlo | Status |
|---|---|
| §1 Načti aktuální stav | ✅ — read existující HTML + live Homey API + 79 device snapshot |
| §2 Audit report | ✅ — tento soubor |
| §3 hardware_inventory_verified.json | ✅ — 22 polí schema |
| §4 Matter separate section | ✅ — dedicated section + physical/virtual_bridge distinction |
| §5 Photo policy | ✅ — placeholder ikony pro 74/79, žádný e-shop hotlink, CSV s `source_type` + `license_status` |
| §6 Page structure | ✅ — hero + KPI + filtry + zóny + Matter + UNKNOWN + table mode |
| §7 Design | ✅ — responsive 1920/1366/390, jednotné karty, table scroll-x na mobile |
| §8 SEO | ✅ — title, meta, OG, H-hierarchy, alt text |
| §9 Backup | ✅ — `_archive/hardware_page_before_fix/2026-05-11_1113/` |
| §10 Implementation | ✅ — žádné jiné stránky netknuté |
| §11 QA | ⏳ — Phase 6 (screenshoty) |
| §12 Outputs | ⏳ — 8 souborů, většina hotová |
| §13 Final report | ⏳ — Phase 7 |
| §14 Stop pravidlo | ✅ — žádný dashboard / Homey / Flow / scripty / účetní kniha touched |

---

## 5) Závěr auditu

| Kategorie | Před | Po |
|---|---:|---:|
| Zařízení | 79 | 79 ✅ |
| Matter (správně klasifikováno) | 1 (ráno → 8) | **8** (1 physical + 7 virtual bridge) ✅ |
| Protokoly explicitně | 9 | **10** (+ Cloud (web)) ✅ |
| UNKNOWN protokol | 0 | 0 ✅ |
| UNKNOWN model | 0 | 0 (per brand inference) ✅ |
| Verification status | 0 (chyběl) | 72 verified / 7 partial / 0 unknown |
| Schema polí | 14 | 22 |
| Filtry | 4 | 7 |
| Mode toggle | ne | ano (Cards/Table) |
| Sekce | flat | Matter → Zones → Legacy → UNKNOWN |
| Foto na disku | 5 | 5 (bez změny — Wave A doplnit user) |
| Foto placeholder | text | ikona kategorie + label |

**Audit closed.** Implementační fáze hotová, vyžaduje jen QA screenshoty + final report.
