"""Download Homey iconObj SVG icons for all 79 devices to assets/hardware/icons/.

Source: Homey REST /api/icon/<icon-id> (own homey, own token, read-only).
Output: assets/hardware/icons/<slug>.svg

These are OFFICIAL Homey ecosystem icons — license-clean for personal documentation.
Each icon is a device-app icon (per driver), so often shows the actual product family.
Better than emoji placeholders, but NOT a true product photo.
"""
import sys
import ssl
import json
import re
import unicodedata
from pathlib import Path

sys.path.insert(0, r'C:\Claude_code_SMART_HOME\tools')
sys.stdout.reconfigure(encoding='utf-8')

ssl._create_default_https_context = ssl._create_unverified_context
import homey_api as h  # noqa: E402
from urllib import request as _r  # noqa: E402

ROOT = Path(__file__).parent
DEVICES = json.load(open(r'C:\Claude_code_SMART_HOME\11_5\homey_devices_2026-05-11.json', encoding='utf-8'))
OUT = ROOT / 'assets' / 'hardware' / 'icons'
OUT.mkdir(parents=True, exist_ok=True)


def slugify(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^a-zA-Z0-9_]+', '-', s).strip('-').lower()
    return s or 'device'


def fetch_icon(path, timeout=30):
    token = h.load_token()
    base = h.get_base_url()
    headers = {'Authorization': f'Bearer {token}', 'Accept': '*/*'}
    req = _r.Request(f'{base}{path}', headers=headers, method='GET')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with _r.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.headers.get('Content-Type', ''), r.read()
    except Exception as e:
        return 0, '', str(e).encode()[:200]


def main():
    total = 0
    ok = 0
    fail = 0
    mapping = {}
    for dev_id, dev in DEVICES.items():
        if not isinstance(dev, dict):
            continue
        total += 1
        name = dev.get('name', dev_id[:8])
        icon = dev.get('iconObj')
        if not icon or 'url' not in icon:
            fail += 1
            print(f'  -- {name}: no iconObj.url')
            continue
        url = icon['url']
        slug = slugify(name)
        out_file = OUT / f'{slug}.svg'
        # Skip if already downloaded
        if out_file.exists() and out_file.stat().st_size > 100:
            mapping[name] = f'assets/hardware/icons/{slug}.svg'
            ok += 1
            continue
        status, ct, body = fetch_icon(url)
        if status != 200 or not body or len(body) < 100:
            fail += 1
            print(f'  -- {name}: status={status}')
            continue
        out_file.write_bytes(body)
        mapping[name] = f'assets/hardware/icons/{slug}.svg'
        ok += 1
        print(f'  OK {name[:40]:40s} → {out_file.name}  ({len(body)} B)')

    print(f'\n=== {ok} / {total} icons downloaded ({fail} failed) ===')
    # Save mapping for use in inventory builder
    map_file = ROOT / 'assets' / 'hardware' / 'icons_mapping.json'
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f'Mapping saved: {map_file.name}')


if __name__ == '__main__':
    main()
