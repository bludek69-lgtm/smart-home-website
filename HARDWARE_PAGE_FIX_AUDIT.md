# Hardware page fix — audit (2026-05-11)

**Scope:** `hardware-komplet.html` na `https://bludek69-lgtm.github.io/smart-home-website/`
**SSOT zdroj:** `C:\Claude_code_SMART_HOME\11_5\homey_devices_2026-05-11.json` (live snapshot, 79 zařízení)
**Build pipeline:** `_build_hardware_inventory.py` → `data/hardware_inventory.json` → `_build_hardware_complete.py` → `hardware-komplet.html`

---

## 1) Najité chyby (před opravou)

| # | Problém | Skutečnost (live) | Impact |
|---|---------|-------------------|--------|
| **A** | Matter zobrazován jako **1 zařízení** | **8 Matter** (7 virtuálních RGBTW + 1 Meross plug) | grossly understated |
| **B** | 11 zařízení v UNKNOWN protokolu | 0 z nich bylo skutečně neznámé — všechny mají známý driverId | falešně negativní |
| **C** | Photo placeholder = jen text "Foto doplnit" | žádná vizuální kategorie | UI flat |

### Root cause (A + B)

`DRIVER_META` v `_build_hardware_inventory.py` mělo klíče **s prefixem** `homey:` (např. `homey:virtualdrivermatter:driver`), ale lookup byl prováděn na **stripnutém** klíči po `.replace('homey:app:','').replace('homey:','')` (tj. `virtualdrivermatter:driver`).

Důsledek: 11 zařízení (7× Matter virtual + 4× Zigbee virtual) padalo do `UNKNOWN` fallbacku.

**Postižená zařízení (před opravou: UNKNOWN, po opravě: Matter):**
1. `Smart RGBTW Bulb 1` — jídelní lampa 1/3
2. `Smart RGBTW Bulb 2` — jídelní lampa 2/3
3. `Smart RGBTW Bulb 3` — jídelní lampa 3/3
4. `Kuchyne 1` — A19/A60 kuchyně, scéna-only
5. `Kuchyne 2` — A19/A60 kuchyně, scéna-only
6. `Kuchyne 3` — A19/A60 kuchyně, scéna-only
7. `Zarovka Loznice` — Matter virtual (přejmenováno 4.5.2026 z Lidl Zigbee, atomic UUID swap)

**Postižená zařízení (před opravou: UNKNOWN, po opravě: Zigbee virtual):**
8. `1 žárovka lidl E14` — Generic Zigbee virtual
9. `2 žárovka lidl E14` — Generic Zigbee virtual
10. `lampicka` — Generic Zigbee virtual (pracovna stolní lampa)
11. `Zvlhčovač1` — Generic Zigbee virtual

> 8. Meross plug `Zasuvka Kuchyne Kaffe` (driver `com.meross.official:mss315-eu-matter`) byl už předtím správně klasifikován jako Matter (jediný "real" Matter prior to fix).

---

## 2) Změny v build skriptech

### `_build_hardware_inventory.py`
- ✏️ Sjednoceny klíče `DRIVER_META` na post-strip formát (bez `homey:` prefixu)
- ✏️ Doplněny 7 human-readable notes pro Matter virtual zařízení (kontext jídelna/kuchyně/ložnice)

### `_build_hardware_complete.py`
- 🆕 `CATEGORY_ICON` dict — emoji per category (sensor 👁, light 💡, audio 🔊, heating 🌡, plug 🔌, button 🎛, blind 🪟, appliance 🤖, infrastructure 🧠)
- ✏️ Photo placeholder nyní renderuje ikonu kategorie + "Foto doplnit" pro chybějící obrázek (lepší UX než plain text)

### Co se NEMĚNILO
- Filtry, search box, mobilní layout, styly, ID skriptu — všechno netknuto
- SSOT pipeline — beze změny formátu (jen oprava lookupu)
- Žádné UUID/IP/tokeny v public výstupu (sanitizace zachována)

---

## 3) Stav po opravě (verified)

```
Total devices:          79
Protocols:
  Zigbee                  37
  Z-Wave                  10
  Matter                   8   ← bylo 1, nyní 8 (+7)
  Wi-Fi (Cloud)            7
  Wi-Fi                    6
  Zigbee (Hue Bridge)      5
  Google Cast (Wi-Fi)      3
  Wi-Fi (HA)               2
  Cloud (web)              1
UNKNOWN protocol:          0   ← bylo 11, nyní 0
Total photos on disk:      5   (4 .png + 1 placeholder gen)
Photos missing:           74   (renderuje se kategorie-icon placeholder)
```

**Matter devices verified (8/8):**
- Smart RGBTW Bulb 1 / 2 / 3 → Matter virtual bridge
- Kuchyne 1 / 2 / 3 → Matter virtual bridge
- Zarovka Loznice → Matter virtual bridge
- Zasuvka Kuchyne Kaffe → Meross MSS315 Smart Plug (real Matter)

---

## 4) Co zůstává otevřené

Detail viz `HARDWARE_UNKNOWN_DEVICES_TODO.md`. Stručně:

- **Modely:** žádné zařízení už nemá `model=UNKNOWN`, ale 7 Matter virtuálů má generický popis `Matter virtual device` — user může upřesnit fyzický kus (např. „Smart RGBTW Bulb 1 je Lidl HG06492C"). Nelze zjistit z REST API — virtual driver maskuje původní HW.
- **Fotky:** 74 / 79 chybí na disku. Build skript je toleruje (placeholder s ikonou). Doporučená strategie viz `HARDWARE_PHOTO_SOURCE_REPORT.md`.
- **Žádný photo hotlink na e-shopy** nebyl přidán (license risk + odkaz mortality).

---

## 5) Pravidla zachována (compliance)

- ✅ Žádné UUID v public výstupu
- ✅ Žádné private IP (192.168.*, 10.*)
- ✅ Žádné bearer tokeny / Apps Script tokeny
- ✅ Memory ≠ fakt — SSOT je live REST snapshot z 2026-05-11
- ✅ NO REGRESSION — žádný existující filtr / styl / render neporušen
- ✅ Idempotent: opakované spuštění buildu produkuje identický výstup
