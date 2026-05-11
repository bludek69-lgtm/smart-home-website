# Hardware photos — source strategy & status (2026-05-11)

**Cíl:** doplnit foto k 79 zařízením **bezpečně** (bez license violation, bez random e-shop hotlinků).

---

## 1) Současný stav

| Kategorie | Počet |
|-----------|------:|
| Total devices | 79 |
| Foto na disku (`assets/photos/`) | **5** |
| Chybí (renderuje se placeholder ikona) | 74 |

### Skutečně přítomné soubory (`ls assets/photos/`)
```
aqara-cube-t1-pro.png
homey-pro.png
nest-mini.png            (použit 3× — všechny Nest Mini i Nest Hub fallback)
viomi-v7-vacuum.png
```

### Render chování pro chybějící foto
`_build_hardware_complete.py` provádí `if (ROOT / photo_path).exists(): use img ELSE placeholder`. Placeholder od dnešní opravy je vizuálně bohatší:

```html
<div class="hw-photo-ph">
  <div class="hw-photo-ph-icon">💡</div>        <!-- ikona dle category -->
  <div class="hw-photo-ph-text">Foto doplnit</div>
</div>
```

CATEGORY_ICON: sensor 👁 / light 💡 / audio 🔊 / heating 🌡 / plug 🔌 / button 🎛 / blind 🪟 / appliance 🤖 / infrastructure 🧠.

---

## 2) Strategie pro doplnění fotek (bezpečně)

### ✅ POVOLENÉ zdroje (license-safe)

1. **Manufacturer press kits / oficiální produktové stránky**
   - SONOFF: `sonoff.tech/product-document/`
   - Fibaro / Nice: `manuals.fibaro.com`
   - Aqara: `aqara.com/eu/product/...`
   - IKEA: `ikea.com/cz/.../produkty/`
   - Lidl Smart Home: `lidl-service.com`
   - Meross: `meross.com`
   - Shelly: `shelly.com`
   - Foscam: `foscam.com`
   - Xiaomi: `mi.com` / `home.miot-spec.com`
   - Philips Hue: `philips-hue.com/cs-cz`
   - Athom Homey: `homey.app/en-us/store/`
   - HP: `hp.com` (HP press image library)

   → Obrázky stáhnout lokálně do `assets/photos/<vendor>-<model>.webp`, NIKOLI hotlinkovat.

2. **Wikimedia Commons** — fotky elektroniky pod CC-BY / CC-BY-SA / public domain
   - `commons.wikimedia.org/wiki/Category:Smart_home_devices`
   - Vždy přidat atribuci do alt/title nebo do samostatného `assets/photos/ATTRIBUTION.md`

3. **Vlastní foto** (mobil, makro objektiv, neutrální pozadí)
   - 1024×640 px, contained, JPG nebo WebP < 60 KB
   - Lifetime warranty: user fotí sám, žádný license risk

### ❌ ZAKÁZANÉ zdroje

| Zdroj | Důvod |
|-------|-------|
| Alza.cz / CZC.cz / Mall.cz / Heureka | E-shop má license na obrázek od dodavatele, ne na re-publikaci |
| Random Google Image search | Často watermark, copyrighted, link mortality |
| Aliexpress / Amazon listings | Listing photos = vendor copyright, mizí když listing zmizí |
| Hotlink (`<img src="https://example.com/image.jpg">`) | Bandwidth theft, link mortality, nestabilní layout |
| Screenshoty z review videí | Original creator copyright |

---

## 3) Doporučený postup pro user (3 vlny)

### Vlna A — high-impact zařízení (8-10 ks)
Začít s nejvíc viditelnými / nejčastěji zmiňovanými:
- `Homey Pro 2026` (centrální mozek) → `homey.app/store/` press image
- `Sektorka1` (open space master light) → Lidl HG06492C reálná fotka
- `Sensore di Presenza SNZB-06P openspace` → SONOFF SNZB-06P
- `FGS-214 Heating` → Fibaro FGS-214 press
- `Sonoff TRVZB` × 4 (TRV ventily topení) → SONOFF TRVZB
- `Zasuvka Kuchyne Kaffe` (Meross MSS315) → Meross press image
- `Cast – Kuchyn` (Google Nest Mini) → už máš `nest-mini.png`
- `Pracovna PC Powerstrip` (Shelly Plug S Gen3) → Shelly press image

### Vlna B — generic kategorie (vzory pro většinu)
- `philips-hue.webp` — 1 photo pro 5 Hue žárovek (manufacturer press)
- `lidl-plug.webp` — 1 photo pro 4 Lidl plugy
- `sonoff-snzb-03.webp` — pro 2 motion senzory
- `fibaro-fgs-223.webp` — pro 2 Fibaro relé
- `matter-bulb.webp` — generic Matter bulb stock pro 7 virtuálů

### Vlna C — zbytek (long-tail)
Vše ostatní — single-instance zařízení. Bez fotky to vypadá stále OK díky placeholderu s ikonou.

---

## 4) Naming konvence

```
assets/photos/<vendor>-<model>.webp
assets/photos/<vendor>-<model>.png      (pokud webp není dostupný)
```

Příklady:
- `sonoff-snzb-06p.webp` (vendor: sonoff, model: snzb-06p)
- `fibaro-fgs-214.webp`
- `meross-mss315.webp`
- `lidl-bulb.webp` (generic Lidl bulb)

**Inventory už referencuje budoucí filenames** — stačí soubory doplnit, placeholder zmizí automaticky bez rebuildu.

---

## 5) Co tato session udělala / NEUDĚLALA

### ✅ Udělala
- Bezpečný placeholder s ikonou kategorie pro 74 chybějících fotek
- Inventory reference image paths jsou stabilní (post-build změna fotek = 0 změna kódu)
- Žádný hotlink, žádný unsafe zdroj v hardware-komplet.html

### ❌ NEUDĚLALA (z licenčních důvodů)
- Nestáhla žádnou fotku z e-shopů ani z náhodných Google výsledků
- Nepřidala žádný hotlink na external server
- Nevolala manufacturer press URL automaticky (user musí potvrdit, který obrázek je správný produkt)

---

## 6) Akce pro user (pokud chce dokončit)

1. **Vybrat 5-10 zařízení Vlna A** (viz §3)
2. **Stáhnout press image** z manufacturer stránky → save as `assets/photos/<jméno>.webp` (rozměr 1024×640 nebo menší, < 80 KB)
3. **Filename match** s inventory: `python -c "import json; [print(i['image']) for i in json.load(open('data/hardware_inventory.json',encoding='utf-8'))['inventory']]"` ti dá kompletní seznam očekávaných names
4. **Commit + push** — žádný rebuild HTML potřeba není, browser už načte nové soubory

Pokud chce user generický kategorie placeholder, mohu doplnit 9 jednoduchých SVG icon-tile fallbacků (`assets/photos/cat-sensor.webp`, atd.).
