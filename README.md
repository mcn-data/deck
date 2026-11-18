# Dashboard MCN

Dashboard performa digital MCN (holding). Repo ini menghasilkan dua keluaran:

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
| `scripts/` | `build_data.py`, `build_app.py`: Excel → data → HTML |
| `worker/` | Kode Cloudflare Worker untuk panel Ask |
| `tests/` | Pengujian angka dan tampilan |

## Penting: repo ini Public

Semua berkas di repo ini bisa dibaca siapa pun.

- **Jangan unggah Excel mentah** (`.xlsx`) ke repo. Yang diunggah cukup data hasil agregasi.
- **Jangan pernah menaruh API key** di berkas mana pun. API key Claude disimpan sebagai *secret* di Cloudflare Worker.

## Status

- [x] Repo dibuat
- [ ] GitHub Pages aktif
- [ ] Pemetaan sumber data MCN
- [ ] `build_data.py` dan verifikasi angka
- [ ] Dashboard mandiri (v1)
- [ ] Worker + panel Ask (agentic AI)
