"""Build hardware_inventory_verified.json with extended schema.

Source of truth: live Homey REST snapshot.
Extends previous hardware_inventory.json with:
  - name_homey, display_name, room_group
  - device_class, driver, app
  - used_in_automation, used_in_dashboard, energy_measured, matter_device (yes/no/unknown)
  - role, description
  - image_file, image_source_url, image_license_status (own/official/allowed/unknown)
  - verification_status (verified/partial/unknown)
  - notes

Also produces hardware_image_sources.csv with full schema.

NEVER hardcoded devices — vše z live data.
"""
import sys
import json
import csv
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).parent
LIVE_DEVICES = Path(r'C:\Claude_code_SMART_HOME\11_5\homey_devices_2026-05-11.json')
LIVE_ZONES = Path(r'C:\Claude_code_SMART_HOME\11_5\homey_zones_2026-05-11.json')
LIVE_ADVFLOWS = Path(r'C:\Claude_code_SMART_HOME\11_5\homey_advflows_2026-05-11.json')
PREV_INV = ROOT / 'data' / 'hardware_inventory.json'  # has hand-curated notes/role
DASH_DIR = Path(r'C:\Claude_code_SMART_HOME\dashboards')

OUT_JSON = ROOT / 'data' / 'hardware_inventory_verified.json'
OUT_CSV = ROOT / 'hardware_image_sources.csv'

DATE = datetime.now().strftime('%Y-%m-%d')

# ─── Load sources ──────────────────────────────────────────
def load(p):
    if not p.exists():
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


DEVICES = load(LIVE_DEVICES) or {}
ZONES = load(LIVE_ZONES) or {}
ADVFLOWS = load(LIVE_ADVFLOWS) or {}
PREV = load(PREV_INV) or {}
PREV_BY_NAME = {it['name']: it for it in PREV.get('inventory', [])}

# Aggregate dashboard HTML content for "used_in_dashboard" detection
DASH_TEXT = ''
for fn in ['smart_home_v7_1920.html', 'smart_home_v7_2880.html',
           'smart_home_v8_1_rpi_control.html']:
    p = DASH_DIR / fn
    if p.exists():
        DASH_TEXT += p.read_text(encoding='utf-8', errors='ignore')

# Aggregate flow JSON for "used_in_automation" detection
FLOWS_TEXT = json.dumps(ADVFLOWS, ensure_ascii=False) if ADVFLOWS else ''

# ─── Driver/protocol classification ────────────────────────
PROTOCOL_FROM_DRIVER = {
    # Pattern: driverId substring → (protocol, app_label)
    'com.fibaro': ('Z-Wave', 'Fibaro'),
    'com.qubino': ('Z-Wave', 'Qubino'),
    'com.aeotec': ('Z-Wave', 'Aeotec'),
    'com.aqara': ('Zigbee', 'Aqara'),
    'com.xiaomi': ('Zigbee', 'Xiaomi'),
    'com.sonoff': ('Zigbee', 'SONOFF'),
    'com.ewelink': ('Zigbee', 'eWeLink'),
    'com.lidl': ('Zigbee', 'Lidl Smart Home'),
    'com.ikea': ('Zigbee', 'IKEA'),
    'com.philips.hue': ('Zigbee (Hue Bridge)', 'Philips Hue'),
    'nl.philips.hue': ('Zigbee (Hue Bridge)', 'Philips Hue'),
    'philips_hue': ('Zigbee (Hue Bridge)', 'Philips Hue'),
    'com.meross.official': ('Wi-Fi (Cloud)', 'Meross'),
    'com.allterco.shelly': ('Wi-Fi', 'Shelly'),
    'cloud.shelly': ('Wi-Fi (Cloud)', 'Shelly Cloud'),
    'com.athom.google': ('Google Cast (Wi-Fi)', 'Google Cast'),
    'com.google.chromecast': ('Google Cast (Wi-Fi)', 'Google Cast'),
    'com.android.tv': ('Wi-Fi', 'Android TV'),
    'com.foscam': ('Wi-Fi (Cloud)', 'Foscam'),
    'com.ivyiot.foscam': ('Wi-Fi (Cloud)', 'Foscam IvyIoT'),
    'de.mhaid.hp': ('Wi-Fi (LAN)', 'HP Printer'),
    'io.home-assistant': ('Wi-Fi (HA)', 'Home Assistant'),
    'no.yr': ('Cloud (web)', 'Yr.no weather'),
    'com.athom.homeyduino': ('Wi-Fi', 'Homeyduino'),
    'no.nordicsemi.thread': ('Thread', 'Thread'),
    'homeassistant': ('Wi-Fi (HA)', 'Home Assistant'),
    'home_assistant': ('Wi-Fi (HA)', 'Home Assistant'),
    'virtualdrivermatter': ('Matter', 'Matter virtual bridge'),
    'virtualdriverzigbee': ('Zigbee', 'Generic Zigbee virtual'),
    'mss315-eu-matter': ('Matter', 'Meross Matter'),
    'pollux': ('Cloud (web)', 'Web service'),
    'yr.no': ('Cloud (web)', 'Yr.no weather'),
}


def detect_protocol(driver_id, flags):
    """Return (protocol, app_label)."""
    if not driver_id:
        return ('UNKNOWN', 'UNKNOWN')
    d = driver_id.lower()
    for key, (proto, app) in PROTOCOL_FROM_DRIVER.items():
        if key in d:
            return (proto, app)
    # Fallback from flags
    if 'matter' in flags or 'matter' in d:
        return ('Matter', 'Matter')
    if 'zwave' in flags:
        return ('Z-Wave', 'Z-Wave')
    if 'zigbee' in flags:
        return ('Zigbee', 'Zigbee')
    return ('UNKNOWN', 'UNKNOWN')


def matter_classification(driver_id, protocol):
    """
    Returns one of:
      - 'physical' (Meross MSS315 Matter, real Matter device)
      - 'virtual_bridge' (Matter virtual driver — Homey vystavuje něco jiného přes Matter)
      - 'no' (vše ostatní)
    """
    if not driver_id:
        return 'no'
    d = driver_id.lower()
    if 'virtualdrivermatter' in d:
        return 'virtual_bridge'
    if 'matter' in d and 'virtualdrivermatter' not in d:
        return 'physical'
    return 'no'


def matter_yn(matter_class):
    return 'yes' if matter_class in ('physical', 'virtual_bridge') else 'no'


# ─── Manufacturer + model inference from driverId ──────────
def derive_brand_model(driver_id, prev_item):
    """Try to derive brand + model from prev hand-curated + driver fallback."""
    if prev_item:
        brand = prev_item.get('manufacturer', 'UNKNOWN')
        model = prev_item.get('model', 'UNKNOWN')
        if brand and brand != 'UNKNOWN':
            return brand, model
    # Fallback from driver
    if not driver_id:
        return 'UNKNOWN', 'UNKNOWN'
    d = driver_id.lower()
    if 'fgt-001' in d: return 'Fibaro', 'FGT-001 TRV'
    if 'fgs-214' in d: return 'Fibaro', 'FGS-214 single switch'
    if 'fgs-223' in d: return 'Fibaro', 'FGS-223 double switch'
    if 'fgms-001' in d: return 'Fibaro', 'FGMS-001 Motion Sensor'
    if 'fgwof-011' in d: return 'Fibaro', 'FGWOF-011 Wall plug'
    if 'fgpb-101' in d: return 'Fibaro', 'FGPB-101 Button'
    if 'fibaro' in d: return 'Fibaro', 'UNKNOWN Fibaro model'
    if 'snzb-06p' in d: return 'SONOFF', 'SNZB-06P Presence'
    if 'snzb-03' in d: return 'SONOFF', 'SNZB-03 Motion'
    if 'snzb-04' in d: return 'SONOFF', 'SNZB-04 Door/Window'
    if 'snzb-02' in d: return 'SONOFF', 'SNZB-02 Temp/Humidity'
    if 'th01' in d: return 'SONOFF', 'TH01 Temperature'
    if 'ms01' in d: return 'SONOFF', 'MS01 Motion'
    if 'ds01' in d: return 'SONOFF', 'DS01 Door'
    if 'wb01' in d: return 'SONOFF', 'WB01 Button'
    if 'zbmini' in d: return 'SONOFF', 'ZBMINI Relay'
    if 'basiczbr3' in d: return 'SONOFF', 'BASICZBR3 Relay'
    if 'trvzb' in d: return 'SONOFF', 'TRVZB Thermostat'
    if 'sonoff' in d: return 'SONOFF', 'UNKNOWN SONOFF model'
    if 'mss315-eu-matter' in d: return 'Meross', 'MSS315 Smart Plug (Matter)'
    if 'meross' in d: return 'Meross', 'UNKNOWN Meross model'
    if 'plug-s-gen3' in d: return 'Shelly', 'Plug S Gen3'
    if 'shellyplus-pm-mini-gen3' in d: return 'Shelly', 'Plus PM Mini Gen3'
    if 'shelly' in d: return 'Shelly', 'UNKNOWN Shelly model'
    if 'aqara' in d: return 'Aqara', 'UNKNOWN Aqara model'
    if 'xiaomi' in d: return 'Xiaomi', 'UNKNOWN Xiaomi model'
    if 'lidl' in d: return 'Lidl Smart Home', 'UNKNOWN Lidl model'
    if 'philips' in d or 'hue' in d: return 'Philips Hue', 'UNKNOWN Hue model'
    if 'ikea' in d or 'tradfri' in d: return 'IKEA', 'UNKNOWN IKEA model'
    if 'foscam' in d: return 'Foscam', 'UNKNOWN Foscam model'
    if 'chromecast' in d or 'google' in d: return 'Google', 'Nest speaker/display'
    if 'android' in d: return 'Android TV', 'UNKNOWN TV model'
    if 'virtualdrivermatter' in d: return 'Matter virtual bridge', 'Matter virtual device'
    if 'virtualdriverzigbee' in d: return 'Generic Zigbee virtual', 'Zigbee virtual device'
    if 'homeassistant' in d: return 'Home Assistant', 'HA virtual entity'
    if 'yr.no' in d: return 'Yr.no', 'Weather forecast'
    if 'pollux' in d: return 'Pollux', 'Web service'
    return 'UNKNOWN', 'UNKNOWN'


# ─── Role from class ───────────────────────────────────────
ROLE_FROM_CLASS = {
    'light': 'Osvětlení (lighting)',
    'sensor': 'Environmentální senzor',
    'thermostat': 'Termostat / TRV',
    'socket': 'Síťová zásuvka / spínač',
    'button': 'Tlačítko / scéna trigger',
    'speaker': 'Reproduktor / audio výstup',
    'camera': 'Bezpečnostní kamera',
    'tv': 'TV / streaming endpoint',
    'windowcoverings': 'Roleta / žaluzie',
    'vacuumcleaner': 'Vysavač / robot',
    'heater': 'Topení (boiler)',
    'fan': 'Ventilátor',
    'lock': 'Zámek dveří',
    'doorbell': 'Domovní zvonek',
    'curtain': 'Záclony / roletka',
    'kettle': 'Konvice',
    'coffeemachine': 'Kávovar',
    'remote': 'Dálkový ovladač',
    'other': 'Speciální / složené',
}


def role_from_class(cls, brand):
    base = ROLE_FROM_CLASS.get(cls, f'class={cls}' if cls else 'UNKNOWN')
    return base


# ─── Image license status ─────────────────────────────────
def image_license_status(img_path):
    """Map image to license category."""
    if not img_path:
        return 'unknown'
    p = ROOT / img_path
    if not p.exists():
        return 'unknown'
    # Local PNG/JPG/WebP exist
    return 'own/local'  # User-controlled; either własna nebo from public source already downloaded


# ─── Build single device ──────────────────────────────────
def build_device(dev_id, dev_data):
    name = dev_data.get('name', 'UNKNOWN')
    cls = dev_data.get('class', 'UNKNOWN')
    driver = dev_data.get('driverId', '')
    flags = dev_data.get('flags', [])
    zone_id = dev_data.get('zone', '')
    caps = dev_data.get('capabilities', []) or []
    energy_obj = dev_data.get('energyObj') or {}

    # Zone resolve
    zone_obj = ZONES.get(zone_id, {}) if isinstance(ZONES, dict) else {}
    zone_name = zone_obj.get('name', 'UNKNOWN') if zone_obj else 'UNKNOWN'

    # Previous hand-curated
    prev = PREV_BY_NAME.get(name, {})

    # Protocol / app
    proto, app = detect_protocol(driver, flags)
    matter_class = matter_classification(driver, proto)
    matter = matter_yn(matter_class)

    brand, model = derive_brand_model(driver, prev)
    role = role_from_class(cls, brand)

    # Energy measured = has measure_power capability or non-trivial energyObj.W
    has_power = 'measure_power' in caps or 'meter_power' in caps
    has_energy_meta = energy_obj.get('W') is not None
    if has_power:
        energy_measured = 'yes'
    elif has_energy_meta:
        energy_measured = 'partial'
    else:
        energy_measured = 'no'

    # Used in automation — search flow JSON for device id or name
    in_auto = 'unknown'
    if dev_id in FLOWS_TEXT:
        in_auto = 'yes'
    elif name and name in FLOWS_TEXT:
        in_auto = 'yes'
    else:
        in_auto = 'no'

    # Used in dashboard — search dashboard HTML for name
    in_dash = 'unknown'
    if name and name in DASH_TEXT:
        in_dash = 'yes'
    else:
        in_dash = 'no'

    # Image — reuse from prev
    img_file = prev.get('image', '')
    img_license = image_license_status(img_file)
    img_local_exists = bool(img_file and (ROOT / img_file).exists())
    img_source_url = ''  # User fills manually per safe policy

    # Verification status — strict criteria
    # verified  = brand + model + protocol known AND not a Matter virtual bridge
    # partial   = some uncertainty (Matter virtual = physical HW unknown; or brand/model UNKNOWN)
    # unknown   = protocol UNKNOWN OR everything UNKNOWN
    if proto == 'UNKNOWN':
        verification = 'unknown'
    elif brand == 'UNKNOWN' or model == 'UNKNOWN':
        verification = 'partial'
    elif matter_class == 'virtual_bridge':
        verification = 'partial'  # We know virtual, underlying physical model UNKNOWN
    else:
        verification = 'verified'  # Photo absence handled separately in CSV
    # Photo absence does NOT downgrade verification — tracked in hardware_image_sources.csv

    # Description from prev or auto
    description = prev.get('note', '') or f'{role}. Protokol {proto}, ovládá se přes {app}.'

    # Room group — first word of zone normalized
    room_group_map = {
        'Jídelna': 'open_space',
        'Kitchen': 'open_space',
        'Spolecne': 'open_space',
        'Pc Setup': 'open_space',
        'Ložnice': 'bedroom',
        'Koupelna': 'bathroom',
        'Pracovna': 'office',
        'Prádelna': 'utility',
        'Předsíň': 'entry',
        'Toaleta': 'bathroom',
    }
    zname_clean = zone_name.strip()
    room_group = room_group_map.get(zname_clean, 'other')

    return {
        'name_homey': name,
        'display_name': prev.get('public_name', name).strip(),
        'zone': zname_clean,
        'room_group': room_group,
        'device_class': cls,
        'brand': brand,
        'model': model,
        'protocol': proto,
        'driver': driver,
        'app': app,
        'capabilities': caps,
        'used_in_automation': in_auto,
        'used_in_dashboard': in_dash,
        'energy_measured': energy_measured,
        'matter_device': matter,
        'matter_class': matter_class,  # extra granularity
        'role': role,
        'description': description,
        'image_file': img_file if img_local_exists else '',
        'image_source_url': img_source_url,
        'image_license_status': img_license if img_local_exists else 'unknown',
        'verification_status': verification,
        'notes': prev.get('note', ''),
        # Internal — useful for filtering
        '_dev_id': dev_id,
        '_available': dev_data.get('available', False),
    }


# ─── Main ──────────────────────────────────────────────────
def main():
    print(f'Build verified inventory: {DATE}')
    print(f'  Source: {LIVE_DEVICES.name} ({len(DEVICES)} devices)')
    print(f'  Prev inv: {len(PREV_BY_NAME)} hand-curated entries')
    print(f'  Dashboard text: {len(DASH_TEXT):,} chars (for used_in_dashboard)')
    print(f'  Flow text: {len(FLOWS_TEXT):,} chars (for used_in_automation)')
    print()

    items = []
    if isinstance(DEVICES, dict):
        for dev_id, dev_data in DEVICES.items():
            if not isinstance(dev_data, dict):
                continue
            items.append(build_device(dev_id, dev_data))

    # Stats
    from collections import Counter
    by_proto = Counter(it['protocol'] for it in items)
    by_zone = Counter(it['zone'] for it in items)
    by_matter = Counter(it['matter_device'] for it in items)
    by_matter_class = Counter(it['matter_class'] for it in items)
    by_verification = Counter(it['verification_status'] for it in items)
    by_auto = Counter(it['used_in_automation'] for it in items)
    by_dash = Counter(it['used_in_dashboard'] for it in items)
    by_energy = Counter(it['energy_measured'] for it in items)

    output = {
        'meta': {
            'generated': datetime.now().isoformat(timespec='seconds'),
            'date': DATE,
            'source': str(LIVE_DEVICES.name),
            'total': len(items),
            'protocols': dict(by_proto),
            'zones': dict(by_zone),
            'matter': dict(by_matter),
            'matter_class': dict(by_matter_class),
            'verification': dict(by_verification),
            'used_in_automation': dict(by_auto),
            'used_in_dashboard': dict(by_dash),
            'energy_measured': dict(by_energy),
        },
        'inventory': items,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'OK Written {OUT_JSON.name} ({OUT_JSON.stat().st_size // 1024} KB)')
    print(f'  Total: {len(items)}')
    print(f'  Protocols: {dict(by_proto)}')
    print(f'  Matter: {dict(by_matter)} (class: {dict(by_matter_class)})')
    print(f'  Verification: {dict(by_verification)}')
    print(f'  In automation: {dict(by_auto)}')
    print(f'  In dashboard: {dict(by_dash)}')

    # CSV with image sources schema per prompt §5
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['device_name', 'brand', 'model', 'image_file', 'image_source_url',
                    'source_type', 'license_status', 'notes'])
        for it in items:
            source_type = 'local' if it['image_file'] else 'placeholder'
            w.writerow([
                it['display_name'],
                it['brand'],
                it['model'],
                it['image_file'],
                it['image_source_url'],
                source_type,
                it['image_license_status'],
                it['notes'],
            ])
    print(f'OK Written {OUT_CSV.name} ({len(items)} rows)')


if __name__ == '__main__':
    main()
