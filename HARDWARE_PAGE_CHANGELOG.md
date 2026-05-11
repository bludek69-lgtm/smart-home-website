# HARDWARE PAGE CHANGELOG

## 2026-05-11 — v2 refresh (OPRAVA_STRANKY_HARDWARE)

**Backup před změnou:** `_archive/hardware_page_before_fix/2026-05-11_1113/`

### Nové soubory
- `_build_hardware_verified.py` — SSOT builder s 22-pole schema
- `_build_hardware_page_v2.py` — HTML renderer (hero + KPI + filtry + card/table mode + UNKNOWN sekce)
- `_qa_capture_hardware.py` — playwright headless QA capture (1920/1366/390)
- `data/hardware_inventory_verified.json` — nový inventory (86 KB)
- `HARDWARE_PAGE_AUDIT.md` — deep audit + gaps
- `HARDWARE_PAGE_QA_REPORT.md` — QA výsledek
- `HARDWARE_PAGE_CHANGELOG.md` — tento soubor
- `_qa/screenshots/hardware/` — 15 PNG (3 viewports × 5 sekcí)

### Změny v existujících
- `hardware-komplet.html` — kompletní refactor (109 KB → 191 KB)
- `hardware_image_sources.csv` — schema upgrade (přidány `source_type`, `license_status` per §5)

### Nezměněno (NO REGRESSION)
- `_build_hardware_inventory.py` — původní pipeline zachována pro backward compat
- `_build_hardware_complete.py` — původní renderer zachován
- `data/hardware_inventory.json` — původní inventory netknutý (paralelní soubor)
- Všechny ostatní stránky webu (index, prozivani, zarizeni, pribeh, blog, kontakt, …)
- Atomicly: 0 jiných HTML/CSS/JS modifikováno

### Klíčové změny obsahu

**Schema upgrade**: 14 polí → **22 polí**
- Přidáno: `name_homey`, `display_name`, `room_group`, `device_class`, `brand`, `driver`, `app`, `role`, `description`, `image_source_url`, `image_license_status`, `verification_status`, `used_in_dashboard`, `matter_device` (yes/no), `matter_class` (physical/virtual_bridge/no)

**Matter klasifikace**: 1 (před ranní opravou) → 8 zařízení
- 1 physical (Meross MSS315 Smart Plug Matter native)
- 7 virtual bridge (3× Smart RGBTW Bulb jídelna + 3× Kuchyne A19/A60 + Zarovka Loznice)

**UNKNOWN kategorie**: jasně označeno 7 položek
- Matter virtual bridge devices (fyzický HW model neověřitelný přes REST)

**Sekce na stránce**:
- Hero + 10 KPI cards (před: 9)
- Filter bar: 7 filtrů + reset + mode toggle (před: 4)
- Mode toggle: Cards / Table (před: jen Cards)
- Matter / Thread / Bridge sekce (před: žádná dedicated)
- Zone-by-zone sekce (před: flat grid)
- Legacy sekce (před: smíchané)
- UNKNOWN / partial sekce (před: žádná dedicated)

**Filtry**:
- search (název / model / capability / brand / zone)
- zóna (10 fyzických + nefunkcni)
- protocol (Zigbee, Z-Wave, Matter, …)
- brand (Fibaro, SONOFF, Aqara, …)
- Matter yes/no
- Automation yes/no
- Energy yes/partial/no
- Reset tlačítko

**Performance**: 0 JS errors napříč 3 viewporty, 0 horizontal overflow.

---

## 2026-05-11 08:09 — Matter 1→8 fix (commit `1c96668`)

První oprava — viz `_archive/hardware_page_before_fix/2026-05-11_1113/HARDWARE_PAGE_FIX_AUDIT.md`.

- DRIVER_META lookup bug fix
- Matter 1 → 8
- UNKNOWN protocol 11 → 0
- Placeholder ikony pro chybějící fotky

---

## 2026-04-30 — initial release

První verze `hardware-komplet.html` (4-pillar mega-menu na website).
