"""Build data/hardware_inventory.json — sanitized inventory dataset.

Source: C:/Claude_code_SMART_HOME/11_5/homey_devices_2026-05-11.json
Output: data/hardware_inventory.json (NO device IDs, IPs, tokens, MAC)
"""
import sys, io, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

DEVS_JSON = Path(r'C:\Claude_code_SMART_HOME\11_5\homey_devices_2026-05-11.json')
ZONES_JSON = Path(r'C:\Claude_code_SMART_HOME\11_5\homey_zones_2026-05-11.json')

devs = json.load(open(DEVS_JSON, encoding='utf-8'))
zones = json.load(open(ZONES_JSON, encoding='utf-8'))
zone_map = {z.get('id'): z.get('name', 'UNKNOWN') for z in (zones.values() if isinstance(zones, dict) else zones)}

DRIVER_META = {
    'com.fibaro:FGMS-001-PLUS':   {'m':'Fibaro','mod':'FGMS-001 Motion Sensor Plus','p':'Z-Wave','ph':'fibaro-fgms-001.webp'},
    'com.fibaro:FGPB-101':        {'m':'Fibaro','mod':'FGPB-101 Button','p':'Z-Wave','ph':'fibaro-fgpb-101.webp'},
    'com.fibaro:FGS-214':         {'m':'Fibaro','mod':'FGS-214 Single Switch','p':'Z-Wave','ph':'fibaro-fgs-214.webp'},
    'com.fibaro:FGS-223':         {'m':'Fibaro','mod':'FGS-223 Double Switch','p':'Z-Wave','ph':'fibaro-fgs-223.webp'},
    'com.fibaro:FGT-001':         {'m':'Fibaro','mod':'FGT-001 Heat Controller (TRV)','p':'Z-Wave','ph':'fibaro-fgt-001.webp'},
    'com.fibaro:FGWOF-011':       {'m':'Fibaro','mod':'FGWOF-011 Wall Plug Switch','p':'Z-Wave','ph':'fibaro-fgwof-011.webp'},
    'cloud.shelly:shelly':        {'m':'Shelly','mod':'Shelly Plug / Pro series','p':'Wi-Fi (Cloud)','ph':'shelly-plug.webp'},
    'com.android.tv:remote':      {'m':'Android TV','mod':'Android TV remote','p':'Wi-Fi','ph':'android-tv.webp'},
    'com.google.chromecast:cast': {'m':'Google','mod':'Nest / Cast speaker','p':'Google Cast (Wi-Fi)','ph':'nest-mini.png'},
    'com.ikea.tradfri:rollerblind_fyrtur': {'m':'IKEA','mod':'FYRTUR Roller Blind','p':'Zigbee','ph':'ikea-fyrtur.webp'},
    'com.ivyiot.foscam:dome':     {'m':'Foscam','mod':'Dome camera','p':'Wi-Fi','ph':'foscam-dome.webp'},
    'com.ivyiot.foscam:pt':       {'m':'Foscam','mod':'Pan/Tilt camera','p':'Wi-Fi','ph':'foscam-pt.webp'},
    'com.lidl:plug':              {'m':'Lidl Silvercrest','mod':'Smart Plug (Zigbee)','p':'Zigbee','ph':'lidl-plug.webp'},
    'com.lidl:rgb_bulb_E27':      {'m':'Lidl Silvercrest','mod':'RGB Bulb E27','p':'Zigbee','ph':'lidl-bulb.webp'},
    'com.lidl:rgb_led_strip':     {'m':'Lidl Silvercrest','mod':'RGB LED Strip','p':'Zigbee','ph':'lidl-strip.webp'},
    'com.lidl:smart_motion_sensor':{'m':'Lidl Silvercrest','mod':'Smart Motion Sensor','p':'Zigbee','ph':'lidl-motion.webp'},
    'com.meross.official:mss315-eu-matter':{'m':'Meross','mod':'MSS315 Smart Plug','p':'Matter','ph':'meross-mss315.webp'},
    'com.xiaomi-mi:motion.ac02':  {'m':'Xiaomi/Aqara','mod':'Motion Sensor P1','p':'Zigbee','ph':'aqara-motion-p1.webp'},
    'com.xiaomi-mi:remote.b28ac1':{'m':'Xiaomi/Aqara','mod':'Wireless Remote Switch','p':'Zigbee','ph':'aqara-remote.webp'},
    'com.xiaomi-mi:remote.cagl02':{'m':'Xiaomi/Aqara','mod':'Cube T1 Pro','p':'Zigbee','ph':'aqara-cube-t1-pro.png'},
    'com.xiaomi-mi:sen_ill.mgl01':{'m':'Xiaomi','mod':'Light Sensor MGL01','p':'Zigbee','ph':'xiaomi-light-sensor.webp'},
    'com.xiaomi-mi:sensor_switch':{'m':'Xiaomi/Aqara','mod':'Wireless Switch (mini)','p':'Zigbee','ph':'aqara-switch.webp'},
    'com.xiaomi-miio:airpurifier_dmaker_airfresh_t2017':{'m':'Xiaomi','mod':'Air Purifier 4 Lite','p':'Wi-Fi','ph':'xiaomi-airpurifier.webp'},
    'com.xiaomi-miio:vacuum_viomi_vacuum_v7':{'m':'Viomi','mod':'V7 Robot Vacuum','p':'Wi-Fi','ph':'viomi-v7-vacuum.png'},
    'de.mhaid.hp:hp':             {'m':'HP','mod':'HP printer (network)','p':'Wi-Fi','ph':'hp-printer.webp'},
    'io.home-assistant:hass-device':{'m':'Home Assistant','mod':'HA bridge device','p':'Wi-Fi (HA)','ph':'home-assistant.webp'},
    'nl.philips.hue:bulb':        {'m':'Philips','mod':'Hue Bulb','p':'Zigbee (Hue Bridge)','ph':'philips-hue.webp'},
    'no.yr:myr':                  {'m':'Yr.no','mod':'Weather forecast feed','p':'Cloud (web)','ph':'yr-weather.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-02P':{'m':'Sonoff','mod':'SNZB-02P Temp + Humid','p':'Zigbee','ph':'sonoff-snzb-02p.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-03':{'m':'Sonoff','mod':'SNZB-03 Motion (PIR)','p':'Zigbee','ph':'sonoff-snzb-03.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-04':{'m':'Sonoff','mod':'SNZB-04 Door/Window Sensor','p':'Zigbee','ph':'sonoff-snzb-04.webp'},
    'se.styrahem.sonoff.zigbee:SNZB-06P':{'m':'Sonoff','mod':'SNZB-06P Presence (mmWave 24GHz)','p':'Zigbee','ph':'sonoff-snzb-06p.webp'},
    'tech.sonoff:BASICZBR3':      {'m':'Sonoff','mod':'Basic ZBR3 (relay)','p':'Zigbee','ph':'sonoff-basiczbr3.webp'},
    'tech.sonoff:DS01':           {'m':'Sonoff','mod':'DS01 Door/Window Sensor','p':'Zigbee','ph':'sonoff-ds01.webp'},
    'tech.sonoff:TH01':           {'m':'Sonoff','mod':'TH01 Temperature Sensor','p':'Zigbee','ph':'sonoff-th01.webp'},
    'tech.sonoff:WB01':           {'m':'Sonoff','mod':'WB01 Wireless Button','p':'Zigbee','ph':'sonoff-wb01.webp'},
    'tech.sonoff:ZBMINI':         {'m':'Sonoff','mod':'ZBMINI Smart Switch','p':'Zigbee','ph':'sonoff-zbmini.webp'},
    'tech.sonoff:ms01':           {'m':'Sonoff','mod':'MS01 PIR Motion','p':'Zigbee','ph':'sonoff-ms01.webp'},
    'homey:virtualdrivermatter:driver':{'m':'Matter (virtuální)','mod':'Matter virtual device','p':'Matter','ph':'matter-bulb.webp'},
    'homey:virtualdriverzigbee:driver':{'m':'Generic Zigbee','mod':'Zigbee virtual device','p':'Zigbee','ph':'generic-zigbee.webp'},
}

CAT_FROM_CLASS = {
    'sensor': 'sensor', 'light': 'light', 'speaker': 'audio', 'thermostat': 'heating',
    'airpurifier': 'heating', 'socket': 'plug', 'button': 'button', 'blinds': 'blind',
    'vacuumcleaner': 'appliance', 'tv': 'appliance', 'other': 'infrastructure',
}

META_ZONES = {'TOPENI', 'SMART HOME', 'Home', 'test zarizení', 'nefunkcni',
              'připraveno ale zatim nezařazeno'}

# Human-curated notes (jen klíčová zařízení)
NOTES = {
    'Homey Pro 2026': 'Centrální hub — Zigbee/Z-Wave/Matter/Wi-Fi/Thread.',
    'Sensore di Presenza SNZB-06P openspace': 'Primární mmWave presence pro open space (kuchyně+jídelna+pracovna).',
    'Sensore kuchyně Z-wave': 'Fibaro FGMS-001+ — motion + lux + teplota. Sekundární zdroj pro open space.',
    'Cubo T1 Pro': 'Hlavní fyzický ovladač scén — gesturální vstup.',
    'Roleta Fyrtur1': 'Privacy guard — při otevřené roletě se světla v open space neaktivují.',
    'Fibaro Kotel': 'Z-Wave relé pro elektrický kotel 9 kW — řízeno přes sh_heating_*.',
    'Fibaro Radiator jidelna': 'TRV hlavice — termostatická regulace zóny.',
    'Fibaro Radiator koupelna': 'TRV hlavice — baterie 7 %, vyžaduje výměnu.',
    'Fibaro Radiator toaleta': 'TRV hlavice.',
    'Kuchyn': 'Google Nest Mini — primární TTS / briefing / alert výstup.',
    'nest max Ložnice 2': 'Google Nest Hub Max — vizuální + audio dashboard v ložnici.',
    'Speaker koupelna': 'Lokální audio v koupelně.',
    'Button away/home': 'Fibaro FGPB-101 — manuální override presence (1× home, 2× away).',
    'Predsin': 'Předsíňové tlačítko — odchod/příchod scéna.',
    'Sektorka1': 'Hlavní open-space LED pásek (Lidl Zigbee).',
    'Zarovka Loznice': 'Matter virtual — primární světlo v ložnici.',
    'Led pasek postel': 'Nightlight pásek u postele.',
    'Giuseppe': 'Viomi V7 — robot vysavač (Wi-Fi).',
    'Televize v ložnici': 'Android TV remote — Wi-Fi.',
    'Air Purifier 4 Lite (zhimi.airp.rmb1)': 'Xiaomi čistička s PM2.5 měřením.',
    'HP Printer': 'Síťová tiskárna — non-automated, viditelná pro Homey.',
    'Zasuvka Kuchyne Kaffe': 'Meross Matter plug — kávovar (auto-on ráno).',
    'Zasuvka pracka pradelna': 'Fibaro FGWOF-011 — pračka, ENERGY metering.',
    'Sun': 'Home Assistant device — východ/západ slunce pro fázi dne.',
    'Person': 'Home Assistant device — presence aggregator.',
    'Weather': 'Yr.no — předpověď počasí pro topení a briefing.',
}


def detect_energy(d):
    caps = d.get('capabilities', []) or []
    if 'measure_power' in caps or 'meter_power' in caps:
        return 'REAL'
    if (d.get('energy', {}) or {}).get('approximation', {}).get('usageConstant'):
        return 'ESTIMATE'
    if d.get('class') == 'socket':
        return 'UNKNOWN'
    return 'UNKNOWN'


def detect_automation(cls, cat):
    if cat in ('sensor', 'button', 'blind'):
        return 'yes'  # triggers
    if cat in ('light', 'plug', 'audio', 'heating'):
        return 'yes'  # controlled
    if cat in ('appliance', 'infrastructure'):
        return 'unknown'
    return 'unknown'


def detect_status(d, zone):
    if zone in ('nefunkcni', 'test zarizení'):
        return 'legacy'
    if zone == 'připraveno ale zatim nezařazeno':
        return 'planned'
    if not d.get('available'):
        return 'legacy'
    return 'active'


inventory = []
for d in (devs.values() if isinstance(devs, dict) else devs):
    drv_full = d.get('driverId', '')
    drv_key = drv_full.replace('homey:app:', '').replace('homey:', '')
    meta = DRIVER_META.get(drv_key, {})
    cls = d.get('virtualClass') or d.get('class') or 'other'
    cat = CAT_FROM_CLASS.get(cls, 'infrastructure')
    zone = zone_map.get(d.get('zone'), 'UNKNOWN') or 'UNKNOWN'
    name = (d.get('name') or '').strip()

    inventory.append({
        'name': name,
        'public_name': name,
        'category': cat,
        'class': cls,
        'zone': zone,
        'manufacturer': meta.get('m', 'UNKNOWN'),
        'model': meta.get('mod', 'UNKNOWN'),
        'protocol': meta.get('p', 'UNKNOWN'),
        'capabilities': d.get('capabilities', []) or [],
        'automation_used': detect_automation(cls, cat),
        'energy_data': detect_energy(d),
        'status': detect_status(d, zone),
        'image': f"assets/photos/{meta['ph']}" if meta.get('ph') else 'UNKNOWN',
        'note': NOTES.get(name, '')
    })

CAT_ORDER = ['sensor','light','plug','button','heating','audio','blind','appliance','infrastructure']
inventory.sort(key=lambda x: (CAT_ORDER.index(x['category']) if x['category'] in CAT_ORDER else 99,
                              x['zone'], x['name']))

# Strict sanitization assertions
inv_str = json.dumps(inventory, ensure_ascii=False)
assert not re.search(r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b', inv_str), 'UUID found'
assert not re.search(r'\b192\.168\.\d+\.\d+\b', inv_str), 'private IP found'
assert not re.search(r'\b10\.\d+\.\d+\.\d+\b', inv_str), 'private IP found'
assert 'Bearer ' not in inv_str, 'token found'
assert 'AKfycb' not in inv_str, 'apps_script token found'

real_zones = {i['zone'] for i in inventory if i['zone'] not in META_ZONES and i['zone'] != 'UNKNOWN'}

os.makedirs('data', exist_ok=True)
out = 'data/hardware_inventory.json'
payload = {
    'meta': {
        'source': 'Homey Pro 2026 live REST API export (read-only)',
        'snapshot_date': '2026-05-11',
        'total_devices': len(inventory),
        'physical_zones': len(real_zones),
        'meta_zones_excluded': sorted(META_ZONES),
        'sanitized': True,
        'sanitization_notes': 'No device IDs, IPs, tokens, MAC addresses. Manufacturer/model/protocol derived from public driverId mapping.',
        'access_mode': 'read-only — no device control, no flow/variable changes',
    },
    'inventory': inventory,
}
with open(out, 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f'OK Inventory written: {out}')
print(f'  Total: {len(inventory)} devices')
print(f'  Physical zones: {len(real_zones)} ({sorted(real_zones)})')
print(f'  With note: {sum(1 for i in inventory if i["note"])}')
print(f'  Status active: {sum(1 for i in inventory if i["status"]=="active")}')
print(f'  Status legacy: {sum(1 for i in inventory if i["status"]=="legacy")}')
print(f'  Status planned: {sum(1 for i in inventory if i["status"]=="planned")}')
print(f'  Energy REAL: {sum(1 for i in inventory if i["energy_data"]=="REAL")}')
print(f'  Energy ESTIMATE: {sum(1 for i in inventory if i["energy_data"]=="ESTIMATE")}')
print(f'  Energy UNKNOWN: {sum(1 for i in inventory if i["energy_data"]=="UNKNOWN")}')
