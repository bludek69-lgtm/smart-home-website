"""Capture hardware-komplet.html at 1920×1080, 1366×768, 390×844.

Output: _qa/screenshots/hardware/<resolution>_<view>.png
"""
import asyncio
import sys
from pathlib import Path
import http.server
import socketserver
import threading
import os

sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
OUT = ROOT / '_qa' / 'screenshots' / 'hardware'
OUT.mkdir(parents=True, exist_ok=True)

PORT = 8766


def serve_in_background():
    handler = http.server.SimpleHTTPRequestHandler

    class QuietHandler(handler):
        def log_message(self, *a, **kw):
            pass

    os.chdir(str(ROOT))
    httpd = socketserver.TCPServer(('localhost', PORT), QuietHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


VIEWPORTS = [
    (1920, 1080, 'desktop'),
    (1366, 768, 'notebook'),
    (390, 844, 'mobile'),
]


async def capture():
    httpd = serve_in_background()
    print(f'Server up: http://localhost:{PORT}/')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        total = 0

        for w, h, label in VIEWPORTS:
            print(f'\n=== {label} {w}×{h} ===')
            ctx = await browser.new_context(viewport={'width': w, 'height': h})
            page = await ctx.new_page()
            url = f'http://localhost:{PORT}/hardware-komplet.html'
            try:
                await page.goto(url, wait_until='commit', timeout=15000)
            except Exception:
                await page.goto(url, timeout=30000)
            await page.wait_for_timeout(2500)

            # Above-fold (hero + KPI + filters)
            f1 = OUT / f'{label}_{w}x{h}_01_top.png'
            await page.screenshot(path=str(f1), full_page=False)
            print(f'  OK 01_top → {f1.name} ({f1.stat().st_size // 1024} KB)')
            total += 1

            # Scroll to filters region
            await page.evaluate("document.querySelector('.hw-controls').scrollIntoView({block:'start'})")
            await page.wait_for_timeout(500)
            f2 = OUT / f'{label}_{w}x{h}_02_filters.png'
            await page.screenshot(path=str(f2), full_page=False)
            print(f'  OK 02_filters → {f2.name} ({f2.stat().st_size // 1024} KB)')
            total += 1

            # Scroll to first zone section (safe — querySelector may return null)
            await page.evaluate("(()=>{const e=document.querySelector('#sec-matter');if(e)e.scrollIntoView({block:'start'});})()")
            await page.wait_for_timeout(500)
            f3 = OUT / f'{label}_{w}x{h}_03_matter.png'
            await page.screenshot(path=str(f3), full_page=False)
            print(f'  OK 03_matter → {f3.name} ({f3.stat().st_size // 1024} KB)')
            total += 1

            # Toggle to table mode
            await page.click('#hw-mode-table')
            await page.wait_for_timeout(700)
            await page.evaluate("(()=>{const e=document.querySelector('#hw-view-table');if(e)e.scrollIntoView({block:'start'});})()")
            await page.wait_for_timeout(500)
            f4 = OUT / f'{label}_{w}x{h}_04_table.png'
            await page.screenshot(path=str(f4), full_page=False)
            print(f'  OK 04_table → {f4.name} ({f4.stat().st_size // 1024} KB)')
            total += 1

            # Toggle back + UNKNOWN section
            await page.click('#hw-mode-cards')
            await page.wait_for_timeout(500)
            await page.evaluate("(()=>{const e=document.querySelector('#sec-unknown');if(e)e.scrollIntoView({block:'start'});})()")
            await page.wait_for_timeout(1500)  # extra wait for lazy SVGs to load
            await page.wait_for_timeout(500)
            f5 = OUT / f'{label}_{w}x{h}_05_unknown.png'
            await page.screenshot(path=str(f5), full_page=False)
            print(f'  OK 05_unknown → {f5.name} ({f5.stat().st_size // 1024} KB)')
            total += 1

            # Check for horizontal overflow
            overflow = await page.evaluate(
                'document.documentElement.scrollWidth > document.documentElement.clientWidth'
            )
            errors = await page.evaluate(
                'window._jsErrors ? window._jsErrors.length : 0'
            )
            print(f'  Overflow X: {overflow}  ·  JS errors: {errors}')

            await ctx.close()

        await browser.close()

    httpd.shutdown()
    print(f'\n=== TOTAL: {total} screenshots ===')


if __name__ == '__main__':
    asyncio.run(capture())
