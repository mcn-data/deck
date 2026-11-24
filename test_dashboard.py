"""Uji dashboard: tanpa error JS, dan KPI cocok dengan angka acuan Excel."""
import sys, os
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1243/chrome-linux64/chrome')
    pg = b.new_page(viewport={'width': 1400, 'height': 1000})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.goto('file://' + ROOT + '/index.html'); pg.wait_for_timeout(500)
    kpi = lambda k: pg.inner_text(f'.kpi[data-k={k}] .val')
    print('Default (YTD 2026 vs 2025):', {k: kpi(k) for k in ['views','revenue','rpm','avd','ctr']})
    pg.screenshot(path='/tmp/shot_default.png', full_page=True)
    # Setahun 2025 penuh, semua unit → acuan: views 3.872,55 jt, revenue 12.691,99 jt
    pg.select_option('#fFrom', '2025-01'); pg.select_option('#fTo', '2025-12')
    print('2025 full:', kpi('views'), kpi('revenue'), '| warn:', pg.is_visible('#cmpWarn'))
    pg.select_option('#fFrom', '2026-01'); pg.select_option('#fTo', '2026-10')
    pg.click('.chip[data-u=GTV]')
    print('GTV 2026:', kpi('views'), kpi('revenue'))
    pg.select_option('#fCh', 'GTV Sports')
    print('GTV Sports rows:', pg.locator('#rank tbody tr').count())
    pg.screenshot(path='/tmp/shot_channel.png', full_page=True)
    pg.click('.chip[data-u=ALL]')
    pg.hover('#trend svg', position={'x': 400, 'y': 150}); pg.wait_for_timeout(100)
    print('tooltip visible:', pg.is_visible('#tip'))
    b.close()
print('ERROR JS :', errs if errs else 'tidak ada')
if errs: sys.exit('GAGAL')
