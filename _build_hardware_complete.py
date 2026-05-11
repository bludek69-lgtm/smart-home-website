"""Build hardware-komplet.html — single-pass generator from live Homey export.

Reads C:/Claude_code_SMART_HOME/11_5/homey_devices_2026-05-11.json,
sanitizes (no IPs, no IDs, no tokens), groups by category/zone/protocol,
generates a self-contained HTML page with filters + cards + table.
"""
import sys, io, json, re, html as _html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\lbudi\code\smart-home-website")
SRC_DEVS = Path(r"C:\Claude_code_SMART_HOME\11_5\homey_devices_2026-05-11.json")
SRC_ZONES = Path(r"C:\Claude_code_SMART_HOME\11_5\homey_zones_2026-05-11.json")

# ─── Driver / app → human meta (manufacturer + model + protocol) ───────────
DRIVER_META = {
    'com.fibaro:FGMS-001-PLUS':         {'manuf': 'Fibaro', 'model': 'FGMS-001 Motion Sensor Plus', 'proto': 'Z-Wave', 'photo': 'fibaro-fgms-001.webp'},
    'com.fibaro:FGPB-101':              {'manuf': 'Fibaro', 'model': 'FGPB-101 Button',             'proto': 'Z-Wave', 'photo': 'fibaro-fgpb-101.webp'},
    'com.fibaro:FGS-214':               {'manuf': 'Fibaro', 'model': 'FGS-214 Single Switch',       'proto': 'Z-Wave', 'photo': 'fibaro-fgs-214.webp'},
    'com.fibaro:FGS-223':               {'manuf': 'Fibaro', 'model': 'FGS-223 Double Switch',       'proto': 'Z-Wave', 'photo': 'fibaro-fgs-223.webp'},
    'com.fibaro:FGT-001':               {'manuf': 'Fibaro', 'model': 'FGT-001 Heat Controller (TRV)','proto': 'Z-Wave','photo': 'fibaro-fgt-001.webp'},
    'com.fibaro:FGWOF-011':             {'manuf': 'Fibaro', 'model': 'FGWOF-011 Wall Plug Switch',  'proto': 'Z-Wave', 'photo': 'fibaro-fgwof-011.webp'},
    'cloud.shelly:shelly':              {'manuf': 'Shelly', 'model': 'Shelly Plug / Pro řada',      'proto': 'Wi-Fi (Cloud)', 'photo': 'shelly-plug.webp'},
    'com.android.tv:remote':            {'manuf': 'Android TV', 'model': 'Android TV remote',      'proto': 'Wi-Fi', 'photo': 'android-tv.webp'},
    'com.google.chromecast:cast':       {'manuf': 'Google',  'model': 'Nest / Cast speaker',       'proto': 'Google Cast (Wi-Fi)', 'photo': 'nest-mini.png'},
    'com.ikea.tradfri:rollerblind_fyrtur': {'manuf': 'IKEA', 'model': 'FYRTUR Roller Blind',       'proto': 'Zigbee', 'photo': 'ikea-fyrtur.webp'},
    'com.ivyiot.foscam:dome':           {'manuf': 'Foscam', 'model': 'Dome camera',                 'proto': 'Wi-Fi', 'photo': 'foscam-dome.webp'},
    'com.ivyiot.foscam:pt':             {'manuf': 'Foscam', 'model': 'Pan/Tilt camera',            'proto': 'Wi-Fi', 'photo': 'foscam-pt.webp'},
    'com.lidl:plug':                    {'manuf': 'Lidl Silvercrest', 'model': 'Smart Plug (Zigbee)','proto': 'Zigbee', 'photo': 'lidl-plug.webp'},
    'com.lidl:rgb_bulb_E27':            {'manuf': 'Lidl Silvercrest', 'model': 'RGB Bulb E27',     'proto': 'Zigbee', 'photo': 'lidl-bulb.webp'},
    'com.lidl:rgb_led_strip':           {'manuf': 'Lidl Silvercrest', 'model': 'RGB LED Strip',    'proto': 'Zigbee', 'photo': 'lidl-strip.webp'},
    'com.lidl:smart_motion_sensor':     {'manuf': 'Lidl Silvercrest', 'model': 'Smart Motion Sensor','proto': 'Zigbee','photo': 'lidl-motion.webp'},
    'com.meross.official:mss315-eu-matter': {'manuf': 'Meross', 'model': 'MSS315 Smart Plug',      'proto': 'Matter', 'photo': 'meross-mss315.webp'},
    'com.xiaomi-mi:motion.ac02':        {'manuf': 'Xiaomi/Aqara', 'model': 'Motion Sensor P1',     'proto': 'Zigbee', 'photo': 'aqara-motion-p1.webp'},
    'com.xiaomi-mi:remote.b28ac1':      {'manuf': 'Xiaomi/Aqara', 'model': 'Wireless Remote Switch','proto': 'Zigbee','photo': 'aqara-remote.webp'},
    'com.xiaomi-mi:remote.cagl02':      {'manuf': 'Xiaomi/Aqara', 'model': 'Cube T1 Pro',          'proto': 'Zigbee', 'photo': 'aqara-cube-t1-pro.png'},
    'com.xiaomi-mi:sen_ill.mgl01':      {'manuf': 'Xiaomi',  'model': 'Light Sensor MGL01',        'proto': 'Zigbee', 'photo': 'xiaomi-light-sensor.webp'},
    'com.xiaomi-mi:sensor_switch':      {'manuf': 'Xiaomi/Aqara', 'model': 'Wireless Switch (mini)','proto': 'Zigbee','photo': 'aqara-switch.webp'},
    'com.xiaomi-miio:airpurifier_dmaker_airfresh_t2017': {'manuf': 'Xiaomi','model': 'Air Purifier 4 Lite','proto': 'Wi-Fi','photo': 'xiaomi-airpurifier.webp'},
    'com.xiaomi-miio:vacuum_viomi_vacuum_v7': {'manuf': 'Viomi','model': 'V7 Robot Vacuum','proto': 'Wi-Fi','photo': 'viomi-v7-vacuum.png'},
    'de.mhaid.hp:hp':                   {'manuf': 'HP', 'model': 'HP printer (network)',           'proto': 'Wi-Fi', 'photo': 'hp-printer.webp'},
    'io.home-assistant:hass-device':    {'manuf': 'Home Assistant','model': 'HA bridge device',    'proto': 'Wi-Fi (HA)', 'photo': 'home-assistant.webp'},
    'nl.philips.hue:bulb':              {'manuf': 'Philips', 'model': 'Hue Bulb',                  'proto': 'Zigbee (Hue Bridge)', 'photo': 'philips-hue.webp'},
    'no.yr:myr':                        {'manuf': 'Yr.no', 'model': 'Weather forecast',            'proto': 'Cloud (web)', 'photo': 'yr-weather.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-02P':{'manuf': 'Sonoff','model': 'SNZB-02P Temp + Humid',      'proto': 'Zigbee', 'photo': 'sonoff-snzb-02p.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-03':{'manuf': 'Sonoff','model': 'SNZB-03 Motion (PIR)',        'proto': 'Zigbee', 'photo': 'sonoff-snzb-03.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-04':{'manuf': 'Sonoff','model': 'SNZB-04 Door/Window Sensor',  'proto': 'Zigbee', 'photo': 'sonoff-snzb-04.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-06P':{'manuf': 'Sonoff','model': 'SNZB-06P Presence (mmWave 24GHz)','proto': 'Zigbee','photo': 'sonoff-snzb-06p.webp'},
    'tech.sonoff:BASICZBR3':            {'manuf': 'Sonoff', 'model': 'Basic ZBR3 (relay)',         'proto': 'Zigbee', 'photo': 'sonoff-basiczbr3.webp'},
    'tech.sonoff:DS01':                 {'manuf': 'Sonoff', 'model': 'DS01 Door/Window Sensor',    'proto': 'Zigbee', 'photo': 'sonoff-ds01.webp'},
    'tech.sonoff:TH01':                 {'manuf': 'Sonoff', 'model': 'TH01 Temperature Sensor',    'proto': 'Zigbee', 'photo': 'sonoff-th01.webp'},
    'tech.sonoff:WB01':                 {'manuf': 'Sonoff', 'model': 'WB01 Wireless Button',       'proto': 'Zigbee', 'photo': 'sonoff-wb01.webp'},
    'tech.sonoff:ZBMINI':               {'manuf': 'Sonoff', 'model': 'ZBMINI Smart Switch',        'proto': 'Zigbee', 'photo': 'sonoff-zbmini.webp'},
    'tech.sonoff:ms01':                 {'manuf': 'Sonoff', 'model': 'MS01 PIR Motion',            'proto': 'Zigbee', 'photo': 'sonoff-ms01.webp'},
    'homey:virtualdrivermatter:driver': {'manuf': 'Matter (virtuální bridge)','model': 'Matter virtual device','proto': 'Matter','photo': 'matter-bulb.webp'},
    'homey:virtualdriverzigbee:driver': {'manuf': 'Generic Zigbee','model': 'Zigbee virtual device','proto': 'Zigbee','photo': 'generic-zigbee.webp'},
}

CLASS_LABELS = {
    'sensor':       'Senzor',
    'light':        'Světlo',
    'socket':       'Zásuvka',
    'button':       'Tlačítko',
    'thermostat':   'Termostat / TRV',
    'speaker':      'Reproduktor',
    'blinds':       'Roleta',
    'airpurifier':  'Čistička',
    'vacuumcleaner':'Robot vysavač',
    'tv':           'TV',
    'other':        'Ostatní',
}

CATEGORY_FROM_CLASS = {
    'sensor': 'senzory',
    'light': 'svetla',
    'socket': 'zasuvky',
    'button': 'ovladace',
    'thermostat': 'topeni',
    'speaker': 'audio',
    'blinds': 'rolety',
    'airpurifier': 'topeni',
    'vacuumcleaner': 'spotrebice',
    'tv': 'spotrebice',
    'other': 'ostatni',
}


def sanitize_zone(z):
    return (z or 'UNKNOWN').strip() or 'UNKNOWN'


def detect_energy(d):
    """Return REAL / ESTIMATE / UNKNOWN based on capabilities."""
    caps = d.get('capabilities', []) or []
    has_real_meter = 'measure_power' in caps or 'meter_power' in caps
    has_constant = (d.get('energy', {}) or {}).get('approximation', {}).get('usageConstant')
    if has_real_meter:
        return 'REAL'
    if has_constant:
        return 'ESTIMATE'
    if d.get('class') == 'socket':
        return 'UNKNOWN'
    return 'N/A'


def detect_role(d):
    cls = d.get('class') or d.get('virtualClass') or 'other'
    if cls == 'sensor': return 'sensor'
    if cls == 'light': return 'light'
    if cls == 'speaker': return 'audio'
    if cls == 'thermostat' or cls == 'airpurifier': return 'heating'
    if cls == 'socket': return 'energy'
    if cls == 'blinds': return 'safety'
    if cls == 'button': return 'control'
    if cls == 'vacuumcleaner' or cls == 'tv': return 'appliance'
    if cls == 'other': return 'infrastructure'
    return 'unknown'


# Load
devs = json.load(open(SRC_DEVS, encoding='utf-8'))
zones_raw = json.load(open(SRC_ZONES, encoding='utf-8'))
zone_map = {z.get('id'): z.get('name','UNKNOWN') for z in (zones_raw.values() if isinstance(zones_raw, dict) else zones_raw)}

# Non-physical zones to exclude from "real zone count"
META_ZONES = {'TOPENI', 'SMART HOME', 'Home', 'test zarizení', 'nefunkcni', 'připraveno ale zatim nezařazeno'}

# Build list
items = []
for d in (devs.values() if isinstance(devs, dict) else devs):
    drv = d.get('driverId','')
    # Convert from "homey:app:com.fibaro:FGMS-001-PLUS" → "com.fibaro:FGMS-001-PLUS"
    drv_key = drv.replace('homey:app:', '').replace('homey:', '')
    meta = DRIVER_META.get(drv_key, {})
    cls = d.get('virtualClass') or d.get('class') or 'other'
    # Homey API returns 'zone' as ID — map via zone_map
    zone_id = d.get('zone')
    zone = sanitize_zone(zone_map.get(zone_id, '') or d.get('zoneName',''))
    name = (d.get('name') or '').strip()

    items.append({
        'name': name,
        'zone': zone,
        'class': cls,
        'class_label': CLASS_LABELS.get(cls, cls),
        'category': CATEGORY_FROM_CLASS.get(cls, 'ostatni'),
        'manuf': meta.get('manuf', 'UNKNOWN'),
        'model': meta.get('model', 'UNKNOWN'),
        'proto': meta.get('proto', 'UNKNOWN'),
        'photo': meta.get('photo', ''),
        'available': d.get('available', True),
        'role': detect_role(d),
        'energy': detect_energy(d),
        'state': 'active' if d.get('available') else 'legacy',
    })

# Sort: by category, then zone, then name
CAT_ORDER = ['senzory','svetla','zasuvky','ovladace','topeni','audio','rolety','spotrebice','ostatni']
items.sort(key=lambda x: (CAT_ORDER.index(x['category']) if x['category'] in CAT_ORDER else 99, x['zone'], x['name']))

# Stats
total_devices = len(items)
zones_real = sorted({i['zone'] for i in items if i['zone'] not in META_ZONES and i['zone'] != 'UNKNOWN'})
protocols_used = sorted({i['proto'] for i in items if i['proto'] != 'UNKNOWN'})
by_class = defaultdict(int)
for i in items:
    by_class[i['class']] += 1

print(f'Devices: {total_devices}')
print(f'Real zones: {len(zones_real)}  → {zones_real}')
print(f'Protocols: {protocols_used}')
print(f'Class breakdown: {dict(by_class)}')

# ─── Generate HTML ──────────────────────────────────────────────────────────

def card_html(it):
    has_photo = bool(it['photo'])
    photo_src = f"assets/photos/{it['photo']}" if has_photo else ''
    # Use existing photos when available; otherwise show "Foto doplnit" placeholder
    photo_html = ''
    if has_photo:
        # Check if local file exists; if not, fallback to placeholder
        local_path = ROOT / 'assets' / 'photos' / it['photo']
        if local_path.exists():
            photo_html = f'<img src="{photo_src}" alt="{_html.escape(it["model"])}" loading="lazy" />'
        else:
            photo_html = f'<div class="hw-photo-ph" data-name="{_html.escape(it["photo"])}">Foto doplnit</div>'
    else:
        photo_html = '<div class="hw-photo-ph">Foto doplnit</div>'

    energy_badge = ''
    if it['energy'] in ('REAL', 'ESTIMATE'):
        energy_badge = f'<span class="hw-badge hw-energy-{it["energy"].lower()}">⚡ {it["energy"]}</span>'

    state_badge = f'<span class="hw-badge hw-state-{it["state"]}">{it["state"]}</span>'

    return f'''<article class="hw-card" data-category="{_html.escape(it['category'])}" data-zone="{_html.escape(it['zone'])}" data-protocol="{_html.escape(it['proto'])}" data-state="{_html.escape(it['state'])}" data-search="{_html.escape((it['name']+' '+it['model']+' '+it['manuf']).lower())}">
  <div class="hw-photo">{photo_html}</div>
  <div class="hw-card-body">
    <h3 class="hw-card-title">{_html.escape(it['name'])}</h3>
    <p class="hw-model">{_html.escape(it['manuf'])} · {_html.escape(it['model'])}</p>
    <div class="hw-badges">
      <span class="hw-badge hw-proto">{_html.escape(it['proto'])}</span>
      <span class="hw-badge hw-cat">{_html.escape(it['class_label'])}</span>
      <span class="hw-badge hw-zone">📍 {_html.escape(it['zone'])}</span>
      {energy_badge}
      {state_badge}
    </div>
  </div>
</article>'''


def stats_card(value, label):
    return f'<div class="hw-stat"><div class="hw-stat-val">{value}</div><div class="hw-stat-lbl">{label}</div></div>'


cards_html = '\n'.join(card_html(it) for it in items)

# Zone-aggregated counts
zone_counts = defaultdict(int)
for i in items:
    if i['zone'] not in META_ZONES and i['zone'] != 'UNKNOWN':
        zone_counts[i['zone']] += 1

proto_counts = defaultdict(int)
for i in items:
    if i['proto'] != 'UNKNOWN':
        proto_counts[i['proto']] += 1

# Zone view HTML
zone_rows = ''
for zone in sorted(zone_counts.keys()):
    devs_in_zone = [i for i in items if i['zone'] == zone]
    devs_by_class = defaultdict(int)
    for d in devs_in_zone:
        devs_by_class[d['class_label']] += 1
    detail = ', '.join(f"{n}× {lab}" for lab, n in sorted(devs_by_class.items(), key=lambda x: -x[1]))
    zone_rows += f'<tr><td><strong>{_html.escape(zone)}</strong></td><td>{zone_counts[zone]}</td><td>{detail}</td></tr>\n'

# Protocol view
PROTO_DESC = {
    'Zigbee': 'Mesh síť, baterie + USB hub. Hlavně senzory, tlačítka, Hue světla, Lidl, Sonoff Zigbee.',
    'Z-Wave': 'Stabilní mesh pro kritická zařízení — TRV hlavice, Fibaro motion (kuchyně), kotel relé.',
    'Wi-Fi': 'Spotřebiče (čistička, vysavač, HP tiskárna, kamery Foscam, AndroidTV).',
    'Wi-Fi (Cloud)': 'Shelly Plug S přes cloud relay (Pro řada). Měřené zásuvky.',
    'Matter': 'Nový standard přes Homey Matter bridge. Meross plug + 7 virtuálních RGBTW bulbů.',
    'Google Cast': 'Google Nest Mini / Hub Max — TTS, briefing, audio scény.',
    'Wi-Fi (HA)': 'Home Assistant bridge — Sun + Person device pro presence.',
    'Cloud (web)': 'Yr.no weather forecast feed (text).',
}
proto_rows = ''
for p in sorted(proto_counts.keys()):
    desc = PROTO_DESC.get(p, '—')
    proto_rows += f'<tr><td><strong>{_html.escape(p)}</strong></td><td>{proto_counts[p]}</td><td>{_html.escape(desc)}</td></tr>\n'

# Big table — all devices
table_rows = ''
for it in items:
    table_rows += (
        f'<tr data-category="{_html.escape(it["category"])}" data-zone="{_html.escape(it["zone"])}" data-protocol="{_html.escape(it["proto"])}" data-state="{_html.escape(it["state"])}">'
        f'<td>{_html.escape(it["name"])}</td>'
        f'<td>{_html.escape(it["class_label"])}</td>'
        f'<td>{_html.escape(it["zone"])}</td>'
        f'<td>{_html.escape(it["proto"])}</td>'
        f'<td>{_html.escape(it["role"])}</td>'
        f'<td>{"ano" if it["available"] else "—"}</td>'
        f'<td>{_html.escape(it["energy"])}</td>'
        f'<td>{_html.escape(it["state"])}</td>'
        '</tr>\n')

# Filter options
all_zones = sorted({i['zone'] for i in items if i['zone'] != 'UNKNOWN'})
all_protos = sorted({i['proto'] for i in items if i['proto'] != 'UNKNOWN'})

zone_options = '\n'.join(f'<option value="{_html.escape(z)}">{_html.escape(z)}</option>' for z in all_zones)
proto_options = '\n'.join(f'<option value="{_html.escape(p)}">{_html.escape(p)}</option>' for p in all_protos)

# Stats
stats_block = f'''
  <div class="hw-stats">
    {stats_card(total_devices, 'zařízení')}
    {stats_card(len(zones_real), 'zón')}
    {stats_card(len(protocols_used), 'protokolů')}
    {stats_card(by_class.get('sensor',0), 'senzorů')}
    {stats_card(by_class.get('light',0), 'světel')}
    {stats_card(by_class.get('speaker',0), 'reproduktorů')}
    {stats_card(by_class.get('socket',0), 'zásuvek')}
    {stats_card(by_class.get('thermostat',0), 'TRV')}
    {stats_card(by_class.get('button',0), 'tlačítek')}
  </div>'''

# ─── Final HTML ─────────────────────────────────────────────────────────────

# Read existing index.html for nav template
index_html = (ROOT / 'index.html').read_text(encoding='utf-8')

# Extract header / footer chunks
m_head_end = index_html.find('</head>')
m_nav_start = index_html.find('<header')
m_nav_end = index_html.find('</header>')
m_footer_start = index_html.rfind('<footer')
m_footer_end = index_html.rfind('</footer>')

# Use head as-is from index.html, then replace title/meta and inject our CSS
head_block = index_html[:m_head_end]
head_block = re.sub(r'<title>[^<]+</title>',
                     '<title>Kompletní hardware chytré domácnosti | SMART HOME Semily</title>', head_block, count=1)
head_block = re.sub(r'<meta name="description" content="[^"]+"',
                     '<meta name="description" content="Přehled reálně používaného hardwaru v projektu SMART HOME: Homey Pro 2026, senzory, světla, topení, audio, zásuvky, rolety, dashboard a infrastruktura."',
                     head_block, count=1, flags=re.IGNORECASE)
# Open Graph
if '<meta property="og:title"' in head_block:
    head_block = re.sub(r'<meta property="og:title" content="[^"]+"',
                         '<meta property="og:title" content="Kompletní hardware chytré domácnosti | SMART HOME Semily"',
                         head_block, count=1)
else:
    head_block = head_block.replace('</head>', '')
if '<meta property="og:description"' in head_block:
    head_block = re.sub(r'<meta property="og:description" content="[^"]+"',
                         '<meta property="og:description" content="Reálný přehled hardwaru SMART HOME v Semilech — 79 zařízení, 11 zón, 7+ protokolů."',
                         head_block, count=1)

extra_css = '''
<style>
/* ─── Hardware-komplet page (2026-05-11) ─────────────────────────── */
.hw-page { max-width:1320px; margin:0 auto; padding:1.5rem 1.25rem 4rem; }
.hw-hero { padding:2rem 0 1.5rem; border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:1.5rem; }
.hw-hero h1 { font-size:clamp(1.6rem,3vw,2.4rem); margin:0 0 0.5rem; }
.hw-hero p  { opacity:0.85; max-width:780px; }

.hw-stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr)); gap:0.8rem; margin:1.4rem 0 0; }
.hw-stat  { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:1rem 0.6rem; text-align:center; }
.hw-stat-val { font-size:1.6rem; font-weight:700; color:#7cd6ff; }
.hw-stat-lbl { font-size:0.78rem; opacity:0.7; text-transform:uppercase; letter-spacing:0.5px; margin-top:0.25rem; }

.hw-controls { display:flex; flex-wrap:wrap; gap:0.6rem; align-items:center; margin:1.5rem 0 1rem; padding:0.9rem 1rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px; }
.hw-controls select, .hw-controls input { padding:0.45rem 0.7rem; border-radius:8px; border:1px solid rgba(255,255,255,0.12); background:rgba(255,255,255,0.04); color:inherit; font-size:0.9rem; min-width:130px; }
.hw-controls input { flex:1; min-width:170px; }
.hw-controls label { font-size:0.78rem; opacity:0.7; text-transform:uppercase; letter-spacing:0.5px; }
.hw-count { margin-left:auto; font-size:0.85rem; opacity:0.8; }

.hw-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; margin-top:1.2rem; }
.hw-card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:14px; overflow:hidden; display:flex; flex-direction:column; transition:transform 0.15s, border-color 0.15s; }
.hw-card:hover { transform:translateY(-2px); border-color:rgba(124,214,255,0.3); }
.hw-photo { aspect-ratio:16/10; background:rgba(255,255,255,0.06); display:flex; align-items:center; justify-content:center; overflow:hidden; }
.hw-photo img { width:100%; height:100%; object-fit:contain; padding:0.5rem; }
.hw-photo-ph { color:rgba(255,255,255,0.45); font-size:0.8rem; font-style:italic; text-align:center; }
.hw-card-body { padding:0.9rem 1rem 1rem; }
.hw-card-title { font-size:0.98rem; margin:0 0 0.25rem; line-height:1.25; }
.hw-model { font-size:0.78rem; opacity:0.7; margin:0 0 0.7rem; line-height:1.35; }
.hw-badges { display:flex; flex-wrap:wrap; gap:0.3rem; }
.hw-badge { font-size:0.7rem; padding:0.2rem 0.55rem; border-radius:999px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.1); white-space:nowrap; }
.hw-proto  { background:rgba(124,214,255,0.15); border-color:rgba(124,214,255,0.25); color:#7cd6ff; }
.hw-cat    { background:rgba(255,200,100,0.13); border-color:rgba(255,200,100,0.2); color:#ffc864; }
.hw-zone   { background:rgba(140,255,160,0.10); border-color:rgba(140,255,160,0.2); color:#9cf2a6; }
.hw-energy-real     { background:rgba(255,100,100,0.15); border-color:rgba(255,100,100,0.25); color:#ff8080; }
.hw-energy-estimate { background:rgba(180,140,255,0.13); border-color:rgba(180,140,255,0.2); color:#c8a6ff; }
.hw-state-active { background:rgba(80,200,120,0.13); border-color:rgba(80,200,120,0.2); color:#7cdc94; }
.hw-state-legacy { background:rgba(150,150,150,0.13); border-color:rgba(150,150,150,0.2); color:#a8a8a8; }

.hw-section-h2 { margin-top:2.5rem; padding-bottom:0.4rem; border-bottom:1px solid rgba(255,255,255,0.08); font-size:1.3rem; }
.hw-table-wrap { overflow-x:auto; margin-top:0.8rem; border-radius:12px; border:1px solid rgba(255,255,255,0.08); }
.hw-table { width:100%; border-collapse:collapse; font-size:0.88rem; min-width:760px; }
.hw-table th { background:rgba(124,214,255,0.1); padding:0.7rem 0.8rem; text-align:left; font-weight:600; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.5px; border-bottom:1px solid rgba(255,255,255,0.1); }
.hw-table td { padding:0.55rem 0.8rem; border-bottom:1px solid rgba(255,255,255,0.05); }
.hw-table tr:hover td { background:rgba(255,255,255,0.03); }

.hw-note { background:rgba(255,200,100,0.06); border-left:3px solid #ffc864; padding:0.9rem 1.1rem; border-radius:6px; margin:1.5rem 0; font-size:0.88rem; }
.hw-note strong { color:#ffc864; }

@media (max-width: 720px) {
  .hw-controls { flex-direction:column; align-items:stretch; }
  .hw-controls select, .hw-controls input { width:100%; }
  .hw-count { margin-left:0; }
}
</style>
'''

new_head = head_block + extra_css + '\n</head>'

# Header / nav: use whole header from index, but mark "hardware-komplet" as active later
header_block = index_html[m_nav_start:m_nav_end + len('</header>')]
# Footer
footer_block = index_html[m_footer_start:m_footer_end + len('</footer>')]

# Body skeleton (after header, before footer)
body_main = f'''
<main class="hw-page">
  <div class="hw-hero">
    <h1>Kompletní hardware systému SMART HOME</h1>
    <p>Reálný přehled zařízení, senzorů, světel, audio prvků, měření, infrastruktury a řídicí vrstvy v bytě v Semilech. Data ze živého Homey Pro 2026 exportu (snapshot 2026-05-11).</p>
    {stats_block}
  </div>

  <div class="hw-note">
    <strong>Bezpečnost a transparentnost:</strong> Stránka <strong>nezobrazuje</strong> interní device ID, IP adresy, MAC adresy ani API tokeny.
    Zobrazena jsou pouze obecná data (název v systému, výrobce, model, protokol, zóna, role). Kamery jsou uvedené jen popisem role — stream není veřejný.
  </div>

  <div class="hw-controls" role="region" aria-label="Filtry hardwaru">
    <label for="hw-cat">Kategorie:
      <select id="hw-cat">
        <option value="">vše</option>
        <option value="senzory">Senzory</option>
        <option value="svetla">Světla</option>
        <option value="zasuvky">Zásuvky</option>
        <option value="ovladace">Tlačítka</option>
        <option value="topeni">Topení / klima</option>
        <option value="audio">Audio</option>
        <option value="rolety">Rolety</option>
        <option value="spotrebice">Spotřebiče</option>
        <option value="ostatni">Ostatní</option>
      </select>
    </label>
    <label for="hw-zone">Zóna:
      <select id="hw-zone">
        <option value="">vše</option>
        {zone_options}
      </select>
    </label>
    <label for="hw-proto">Protokol:
      <select id="hw-proto">
        <option value="">vše</option>
        {proto_options}
      </select>
    </label>
    <label for="hw-state">Stav:
      <select id="hw-state">
        <option value="">vše</option>
        <option value="active">active</option>
        <option value="legacy">legacy</option>
      </select>
    </label>
    <input type="search" id="hw-search" placeholder="Hledat (název, model, výrobce)" aria-label="Hledat zařízení" />
    <span class="hw-count"><span id="hw-count-num">{total_devices}</span> z {total_devices}</span>
  </div>

  <section aria-labelledby="hw-grid-h">
    <h2 id="hw-grid-h" class="hw-section-h2">Karty zařízení</h2>
    <div class="hw-grid" id="hw-grid">
{cards_html}
    </div>
  </section>

  <section aria-labelledby="hw-zone-h">
    <h2 id="hw-zone-h" class="hw-section-h2">Hardware podle zón</h2>
    <p style="opacity:0.85; max-width:780px;">Hardware je distribuovaný po reálných obytných zónách. Zóny jako <em>TOPENI</em>, <em>SMART HOME</em>, <em>Home</em> jsou meta-skupiny pro logiku a nepočítají se mezi obytné prostory.</p>
    <div class="hw-table-wrap">
      <table class="hw-table">
        <thead><tr><th>Zóna</th><th>Počet zařízení</th><th>Co tam je</th></tr></thead>
        <tbody>
{zone_rows}        </tbody>
      </table>
    </div>
  </section>

  <section aria-labelledby="hw-proto-h">
    <h2 id="hw-proto-h" class="hw-section-h2">Použité protokoly</h2>
    <div class="hw-table-wrap">
      <table class="hw-table">
        <thead><tr><th>Protokol</th><th>Počet zařízení</th><th>K čemu / co na něm běží</th></tr></thead>
        <tbody>
{proto_rows}        </tbody>
      </table>
    </div>
  </section>

  <section aria-labelledby="hw-table-h">
    <h2 id="hw-table-h" class="hw-section-h2">Detailní tabulka (všechna zařízení)</h2>
    <p style="opacity:0.85;">Filtry nahoře platí i pro tuto tabulku.</p>
    <div class="hw-table-wrap">
      <table class="hw-table" id="hw-table">
        <thead><tr>
          <th>Zařízení</th><th>Kategorie</th><th>Zóna</th><th>Protokol</th><th>Role</th><th>Automat.</th><th>Energie</th><th>Stav</th>
        </tr></thead>
        <tbody>
{table_rows}        </tbody>
      </table>
    </div>
  </section>

  <section>
    <h2 class="hw-section-h2">Odkazy</h2>
    <p><a href="senzory.html">Senzory →</a> · <a href="svetla.html">Světla →</a> · <a href="topeni-klima.html">Topení a klima →</a> · <a href="audio.html">Audio a TTS →</a> · <a href="ovladace.html">Ovladače →</a> · <a href="rolety.html">Rolety →</a> · <a href="zasuvky.html">Zásuvky →</a> · <a href="dashboard.html">Dashboard →</a> · <a href="ai-brain.html">AI Brain →</a></p>
  </section>
</main>

<script>
(function() {{
  const cat=document.getElementById('hw-cat'),
        zone=document.getElementById('hw-zone'),
        proto=document.getElementById('hw-proto'),
        state=document.getElementById('hw-state'),
        search=document.getElementById('hw-search'),
        countEl=document.getElementById('hw-count-num'),
        cards=document.querySelectorAll('#hw-grid .hw-card'),
        rows=document.querySelectorAll('#hw-table tbody tr');
  function apply() {{
    const c=cat.value, z=zone.value, p=proto.value, s=state.value;
    const q=(search.value||'').trim().toLowerCase();
    let shown=0;
    cards.forEach(el => {{
      let ok=true;
      if (c && el.dataset.category!==c) ok=false;
      if (ok && z && el.dataset.zone!==z) ok=false;
      if (ok && p && el.dataset.protocol!==p) ok=false;
      if (ok && s && el.dataset.state!==s) ok=false;
      if (ok && q && (el.dataset.search||'').indexOf(q)<0) ok=false;
      el.style.display = ok?'':'none';
      if (ok) shown++;
    }});
    rows.forEach(el => {{
      let ok=true;
      if (c && el.dataset.category!==c) ok=false;
      if (ok && z && el.dataset.zone!==z) ok=false;
      if (ok && p && el.dataset.protocol!==p) ok=false;
      if (ok && s && el.dataset.state!==s) ok=false;
      if (ok && q && (el.textContent||'').toLowerCase().indexOf(q)<0) ok=false;
      el.style.display = ok?'':'none';
    }});
    countEl.textContent = shown;
  }}
  [cat,zone,proto,state].forEach(el => el.addEventListener('change', apply));
  search.addEventListener('input', apply);
}})();
</script>
'''

# Stitch
final = new_head + '\n<body>\n' + header_block + body_main + footer_block + '\n</body>\n</html>'

# Write
out = ROOT / 'hardware-komplet.html'
out.write_text(final, encoding='utf-8')
print(f'\nWritten: {out} ({len(final)} chars)')
PY