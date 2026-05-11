# Hardware — položky čekající na ruční potvrzení user (2026-05-11)

**Stav:** všechna zařízení mají `protocol != UNKNOWN` a `model != UNKNOWN` po dnešní opravě DRIVER_META. Tento dokument shrnuje zařízení, kde **classification je odvozená z driverId**, ale fyzický kus může být upřesněn user-em (např. konkrétní model lampy za Matter virtual bridge).

---

## A) Matter virtual bridge — 7 položek

DriverId `homey:virtualdrivermatter:driver` znamená "Matter virtual device" — Homey expose jako Matter, ale samotný fyzický hardware může být cokoli (Lidl, Tuya, IKEA…), co je párované přes Matter bridge.

| # | public_name | Zóna | Aktuální popis | User může doplnit |
|---|-------------|------|----------------|--------------------|
| 1 | Smart RGBTW Bulb 1 | Jídelna | Matter virtual device | Konkrétní výrobce + model E27 RGBTW (např. Lidl HG06492C, IKEA Tradfri E27) |
| 2 | Smart RGBTW Bulb 2 | Jídelna | Matter virtual device | dtto |
| 3 | Smart RGBTW Bulb 3 | Jídelna | Matter virtual device | dtto |
| 4 | Kuchyne 1 | Kitchen | Matter virtual device | A19/A60 kuchyně — výrobce |
| 5 | Kuchyne 2 | Kitchen | Matter virtual device | dtto |
| 6 | Kuchyne 3 | Kitchen | Matter virtual device | dtto |
| 7 | Zarovka Loznice | Ložnice | Matter virtual device | Po 4.5.2026 atomic rename z Lidl Zigbee → Matter virtual. **Fyzicky:** stále Lidl HG06492C? (potvrdit) |

> **Pozn.:** REST API neexpose original Zigbee fingerprint pod Matter virtual. Pro upřesnění je potřeba ruční zápis od user.

---

## B) Zigbee virtual / Generic — 4 položky

DriverId `homey:virtualdriverzigbee:driver` = Zigbee zařízení bez konkrétního manufacturer matche v Homey katalogu.

| # | public_name | Zóna | Hypotéza | Akce |
|---|-------------|------|----------|------|
| 8 | 1 žárovka lidl E14 | Ložnice | Lidl Livarno HG06492A E14 | Potvrdit |
| 9 | 2 žárovka lidl E14 | Ložnice | Lidl Livarno HG06492A E14 | Potvrdit |
| 10 | lampicka | Ložnice | Stolní lampička — výrobce ?? | Potvrdit |
| 11 | Zvlhčovač1 | Ložnice | Zvlhčovač s Zigbee modulem | Potvrdit konkrétní typ |

---

## C) Legacy / nefunkční zóna — 4 položky

Tato zařízení jsou ve speciální zóně `nefunkcni` / příp. mají `status=legacy`. Jsou na stránce vidět, ale označená jako legacy. **Žádná akce není kritická** — položky neovládají automatizace.

| # | public_name | Zóna | Stav |
|---|-------------|------|------|
| 12 | Backup | nefunkcni | HA snapshot virtual device (legacy) |
| 13 | Button | nefunkcni | Fibaro FGPB-101 — nezapojený |
| 14 | Sun | nefunkcni | HA sun.sun entita (legacy, virtual) |
| 15 | Giuseppe | Koupelna | Viomi V7 vacuum — fyzicky funkční, zařazené jako legacy (přejmenováno 28.4.) |

**Doporučení:** ponechat jako legacy. Případně rozhodnout, zda Backup + Sun + Button skrýt z hardware stránky úplně (filter `status != legacy`).

---

## D) Otázky pro user (volitelné, žádná nesmí blokovat deploy)

1. **Matter virtual lamps (§A)** — chceš doplnit konkrétní fyzický model do `note` pole inventory? Pokud ano, řekni např. „Smart RGBTW Bulb 1-3 = Lidl Livarno HG06492C E27" a já updatuju `_build_hardware_inventory.py` overrides.
2. **Generic Zigbee (§B)** — stejně.
3. **Legacy section (§C)** — má se v hardware-komplet.html zobrazit toggle "Skrýt legacy"? Aktuálně se zobrazují všechny.
4. **Fotky** — viz `HARDWARE_PHOTO_SOURCE_REPORT.md`, Vlna A (8-10 zařízení) je quick win.

---

## E) NIC z toho neblokuje deploy

Stav `hardware-komplet.html` po dnešní opravě je **plně publikovatelný**:
- ✅ 79 zařízení
- ✅ 8 Matter (matches live system)
- ✅ 0 UNKNOWN protocol
- ✅ 0 UNKNOWN model
- ✅ Placeholder pro 74 chybějících fotek (kategorie ikona + "Foto doplnit")
- ✅ Žádné UUID / private IP / token v HTML
- ✅ Žádný external hotlink

Pokud user nepotvrdí nic z §A-§D, stránka je správně. Tento dokument je čistě **upgrade roadmapa**, ne bug seznam.
