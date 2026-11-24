# Dashboard MNC Group

Dashboard performa digital ekosistem MNC Group, dibangun bertahap: 3TV (RCTI, GTV, MNCTV) dulu, lalu IMG dan unit lain. Repo ini menghasilkan dua keluaran:

1. **Dashboard mandiri**: HTML statis di GitHub Pages, tidak butuh Claude atau server.
2. **Dashboard + Ask (agentic AI)**: dashboard yang sama, ditambah panel tanya-jawab ke Claude lewat penghubung (Cloudflare Worker), dan bisa dibuka siapa pun lewat link.

Link: https://mcn-data.github.io/deck/

## Alur data

```
Excel sumber ──► build_data.py ──► data.json ─┬─► index.html + data.js   (Dashboard mandiri)
                                               └─► panel Ask ──► Worker ──► Claude API
```

Data dipra-agregasi di `data.json`, jadi dashboard tidak perlu server.

## Struktur (akan terisi bertahap)

| Berkas / folder | Peran |
|---|---|
| `index.html` | Halaman dashboard yang tayang di GitHub Pages |
| `data.js` | Data hasil agregasi, dimuat oleh `index.html` |
| `template.html` | Sumber tampilan dashboard (diedit di sini, bukan di `index.html`) |
| `scripts/` | `build_data.py` (Excel → `data.json`), `build_app.py` (template + data → `index.html`, `data.js`) |
| `worker/` | Kode Cloudflare Worker untuk panel Ask |
| `tests/` | Pengujian angka dan tampilan |

## Penting: repo ini Public

Semua berkas di repo ini bisa dibaca siapa pun.

- **Jangan unggah Excel mentah** (`.xlsx`) ke repo. Yang diunggah cukup data hasil agregasi.
- **Jangan pernah menaruh API key** di berkas mana pun. API key Claude disimpan sebagai *secret* di Cloudflare Worker.

## Status

- [x] Repo dibuat
- [x] GitHub Pages aktif
- [x] Pemetaan sumber data tahap 1: 3TV (RCTI, GTV, MNCTV) YouTube
- [x] `build_data.py` dan verifikasi angka
- [x] Dashboard mandiri (v1)
- [ ] Worker + panel Ask (agentic AI)

## Cara update data

```bash
python3 scripts/build_data.py raw/     # Excel di folder raw/ (tidak ikut ke repo)
python3 scripts/build_app.py           # menaikkan nomor Build
python3 tests/test_dashboard.py        # wajib lolos sebelum unggah
```
Unggah `index.html` dan `data.js`, lalu buka link dengan **Ctrl+F5** dan cocokkan nomor Build.
