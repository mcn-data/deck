"""
build_app.py — template.html + data.json → berkas siap kirim

Keluaran:
  index.html  + data.js       → untuk GitHub Pages (data terpisah supaya revisi
                                 tampilan cukup mengunggah index.html yang kecil)
  dashboard_mnc.html          → satu berkas, data tertanam; bisa dibuka langsung
                                 dari komputer tanpa server/internet

Setiap build menaikkan nomor Build (tercetak di pojok kiri bawah). Nomor itu
satu-satunya cara memastikan yang dibuka user bukan salinan lama dari cache.
"""
import os, json, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
p = lambda *a: os.path.join(ROOT, *a)

build_file = p('BUILD')
build = int(open(build_file).read().strip()) + 1 if os.path.exists(build_file) else 1
open(build_file, 'w').write(str(build))
tanggal = datetime.datetime.now().strftime('%d %b %Y %H:%M')

tpl = open(p('template.html'), encoding='utf-8').read()
data = open(p('data.json'), encoding='utf-8').read()
json.loads(data)  # gagal di sini lebih baik daripada dashboard kosong di browser

# Cegah "</script>" di dalam data (mis. nama channel) memotong tag script.
data_js = 'window.DATA=' + data.replace('</', '<\\/') + ';'
tpl = tpl.replace('__BUILD__', str(build)).replace('__BUILD_DATE__', tanggal)

# ?v=build memaksa browser mengambil data.js baru setelah update.
open(p('index.html'), 'w', encoding='utf-8').write(
    tpl.replace('<!--DATA-->', f'<script src="data.js?v={build}"></script>'))
open(p('data.js'), 'w', encoding='utf-8').write(data_js)
open(p('dashboard_mnc.html'), 'w', encoding='utf-8').write(
    tpl.replace('<!--DATA-->', f'<script>{data_js}</script>'))

kb = lambda f: os.path.getsize(p(f)) / 1024
print(f'Build {build}: index.html {kb("index.html"):.0f} KB, data.js {kb("data.js"):.0f} KB, '
      f'dashboard_mnc.html {kb("dashboard_mnc.html"):.0f} KB')
