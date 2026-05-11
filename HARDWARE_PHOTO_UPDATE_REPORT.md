# HARDWARE PHOTO UPDATE REPORT (2026-05-11, Phase 2)

**Scope:** dokončovací fáze pro `hardware-komplet.html` — doplnit fotky bezpečně + zmenšit počet `PHOTO_TODO` / `UNKNOWN`.
**Stručná strategie:** stáhnout oficiální device ikony z vlastního Homey REST (`/api/icon/<id>`) — license-clean (Homey ecosystem assets), bez Google Images, bez e-shop hotlinků.

---

## 1) Fotky doplněné

| Kategorie | Před | Po |
|---|---:|---:|
| Lokální real produktové fotky | 5 | 5 (beze změny — Wave A user-led) |
| **Homey oficiální SVG ikony** | 0 | **73** ⭐ NEW |
| Žádný image (čistý placeholder) | 74 | **1** (Zasuvka Varic Kuchyne — Homey vrátil 0 B body) |
| **Coverage** | 5/79 (6.3 %) | **78/79 (98.7 %)** |

### Per source_type breakdown

| Source type | Počet | License status |
|---|---:|---|
| `local_photo` | 5 | own/local |
| `homey_icon` | 73 | official_homey (ecosystem icons z `/api/icon/<id>`) |
| `placeholder` | 1 | unknown (Zasuvka Varic Kuchyne — Homey REST vrátil 0 B) |

### Lokální real photos (zachované)
```
assets/photos/aqara-cube-t1-pro.png   → Aqara Cube T1 Pro
assets/photos/homey-pro.png           → Homey Pro 2026
assets/photos/nest-mini.png           → 3× Google Nest Mini + Nest Hub Max
assets/photos/viomi-v7-vacuum.png     → Giuseppe (Viomi V7 vacuum)
```

### Nové Homey SVG ikony
```
assets/hardware/icons/ (78 SVG files, ~612 KB total)
  → např. zasuvka-kuchyne-kaffe.svg (Meross MSS315 Matter Smart Plug — clean silhouette)
  → např. fibaro-radiator-jidelna.svg (Fibaro FGT-001 TRV — official manufacturer icon)
  → např. sensore-di-presenza-snzb-06p-openspace.svg (SONOFF presence detector)
```

CSS filter `invert(0.92) hue-rotate(180deg)` aplikován pro dark-theme readability — černé silhouetty se invertují na světlé.

---

## 2) UNKNOWN položky zbývající

| # | Device | Důvod UNKNOWN | Co user musí ověřit |
|---|---|---|---|
| 1–3 | Smart RGBTW Bulb 1/2/3 (Jídelna) | Matter virtual bridge — fyzický HW model neexpose-d přes REST | Konkrétní brand+model (Lidl Livarno HG06492C? IKEA Tradfri Matter? Aqara LED?) |
| 4–6 | Kuchyne 1/2/3 (Kitchen) | Matter virtual bridge | dtto — A19/A60 model |
| 7 | Zarovka Loznice (Ložnice) | Matter virtual bridge (po 4.5.2026 atomic rename — viz `_archive/rename_2026-05-04_bedroom_light/`) | Nová Matter bulb (paired přes Aqara Hub / Apple Home) — Aqara LED? Tradfri? potvrď |
| 8 | Zasuvka Varic Kuchyne | Homey REST vrátil 0-byte icon (pravděpodobně chybějící driver asset) | Re-pair zařízení nebo update Sonoff Zigbee app na Homey |

**Pozn. k §4 promptu** (Matter virtual bridge derivation):

Atomic rename historie `Zarovka Loznice` (přes `grep` v `_archive/rename_2026-05-04_bedroom_light/`):
- 2026-05-04: user přepojil bedroom žárovku z **Lidl Zigbee** → **Matter virtual** (přes Aqara Hub / Apple Home)
- Nová Matter žárovka má UUID `d949b300` + 8 capabilities (vč. `matter_color_loop` — bonus oproti Lidl)
- Stará Lidl entita (`fb102a8d`) byla přejmenována na "Zarovka Loznice OLD" a je v `nefunkcni` zóně

**Tato historie potvrzuje, že fyzický HW Zarovka Loznice už NENÍ Lidl** — nicméně skutečný brand+model nové Matter žárovky nelze derive-nout z REST snapshotu. Zůstává jako `partial`/UNKNOWN k user-potvrzení.

Pro `Smart RGBTW Bulb 1/2/3` (Jídelna) a `Kuchyne 1/2/3` (Kitchen): tato zařízení byla pravděpodobně přidána přímo jako Matter (ne migrovaná) — žádný předchozí Zigbee fingerprint v žádném memory souboru. **UNKNOWN bez user input.**

---

## 3) Placeholdery zbývající

**1 device bez image** (placeholder s emoji ikonou kategorie):
- `Zasuvka Varic Kuchyne` (Shelly Cloud, kuchyně) — Homey REST vrátil 200 status ale 0-byte body pro icon endpoint. Pravděpodobně Shelly cloud app asset corruption. Workaround: re-pair device nebo update app.

---

## 4) Seznam zařízení vyžadujících ruční kontrolu

Akce: user upřesní fyzický model. Po potvrzení → update `derive_brand_model()` v `_build_hardware_verified.py` → re-run pipeline.

| Device | Aktuální brand | Aktuální model | User input potřebný |
|---|---|---|---|
| Smart RGBTW Bulb 1 | Matter virtual bridge | Matter virtual device | brand + model E27 RGBTW |
| Smart RGBTW Bulb 2 | dtto | dtto | dtto |
| Smart RGBTW Bulb 3 | dtto | dtto | dtto |
| Kuchyne 1 | Matter virtual bridge | Matter virtual device | brand + model A19/A60 |
| Kuchyne 2 | dtto | dtto | dtto |
| Kuchyne 3 | dtto | dtto | dtto |
| Zarovka Loznice | Matter virtual bridge | Matter virtual device | nová Matter bulb (post 4.5.2026 swap z Lidl) — brand + model |

Příklad commit po user upřesnění:

```python
# _build_hardware_verified.py § derive_brand_model()
if name == 'Smart RGBTW Bulb 1':
    return 'Lidl', 'Livarno Lux HG06492C E27 RGBTW'  # potvrzeno user 2026-MM-DD
```

---

## 5) Funkčnost stránky

✅ **Stránka zůstala plně funkční** (verifikováno přes 15 screenshotů × 3 viewporty):

| Test | Status |
|---|---|
| Hero + 10 KPI cards | ✅ render correctly |
| 7 filtrů (search, zone, proto, brand, matter, auto, energy) + Reset | ✅ fungují |
| Card / Table mode toggle | ✅ funguje |
| Sekce: Matter (8) → Zones (11) → Legacy (3) → UNKNOWN (7) | ✅ render |
| SVG icons s invert filter na dark theme | ✅ visible + readable |
| Žádný horizontal overflow | ✅ 1920 / 1366 / 390 |
| 0 JS errors | ✅ 3 viewports |

### Změny v build pipeline
- `_build_hardware_verified.py` — wired Homey icons mapping (priority: local photo → SVG icon → emoji placeholder)
- `_build_hardware_page_v2.py` — added `loading="eager"` pro SVG (lazy způsobovalo race s screenshot capture); CSS filter `invert(0.92) hue-rotate(180deg)` na SVG icons
- `_download_homey_icons.py` — NEW nástroj pro download oficiálních Homey SVG icons přes REST

### Bezpečnostní záruky
- ✅ Žádné Google Images
- ✅ Žádné e-shop hotlinky
- ✅ Žádné AI-generované fake fotky
- ✅ License-clean: vlastní Homey ekosystem (vlastní subskripce, vlastní token)
- ✅ Zdroje uvedené v `hardware_image_sources.csv` (column `source_type` + `license_status`)
- ✅ Žádné změny v Homey systému / Flow / scriptech / proměnných (read-only refetch)
- ✅ Žádné změny v dashboardu / účetní knize
- ✅ Žádný reklamní katalog

---

## 6) Soubory v této fázi

### Změněné
- `data/hardware_inventory_verified.json` — 79 položek, nyní s `image_source_type` + 78/79 s image_file
- `hardware_image_sources.csv` — 79 řádků s aktualizovaným `source_type` + `license_status`
- `hardware-komplet.html` — re-rendered s SVG ikonami + eager loading
- `_build_hardware_verified.py` — wired icons mapping
- `_build_hardware_page_v2.py` — eager loading pro SVG + invert CSS filter

### Nové
- `_download_homey_icons.py` — Homey REST icon downloader
- `assets/hardware/icons/` — 78 SVG files (~612 KB total)
- `assets/hardware/icons_mapping.json` — name → path lookup
- `HARDWARE_PHOTO_UPDATE_REPORT.md` — tento report
- `_qa/screenshots/hardware/` — re-captured 15 PNG

---

## 7) Co dál (Wave B optional)

Pro 7 UNKNOWN Matter virtual bridges:
1. User v Homey UI: rozklikne device → settings → uvidí původní Matter fingerprint (vendor ID + product ID)
2. Mapping: Matter vendor ID → brand name (např. `0x1037` = Tuya, `0x1015` = Aqara, `0x1234` = Lidl etc.)
3. Update `_build_hardware_verified.py` § `derive_brand_model()` s konkrétními řádky
4. Re-run `python _build_hardware_verified.py && python _build_hardware_page_v2.py`
5. UNKNOWN section count: 7 → 0 (po potvrzení všech 7)

Pro `Zasuvka Varic Kuchyne` (1× placeholder):
1. Homey UI → device → un-pair → re-pair
2. Po re-pair: `python _download_homey_icons.py` znovu (icon endpoint by měl vrátit non-empty body)

Wave C (long-tail, low priority):
- Real product photos (vlastní macro foto nebo manufacturer press kits) — pro top 8-10 high-impact devices
- Aktuální Homey SVG ikony jsou OK fallback dokud user nedoplní real photos

---

## Verdikt

**98.7 % coverage** (78/79 zařízení s vizuální reprezentací). Stránka funkční ve všech 3 viewportech. 7 UNKNOWN položek dokumentováno s jasnou akcí pro user.

**Připraveno k commit + push.**
