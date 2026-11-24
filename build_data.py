"""
build_data.py — Excel Master Data → data.json (Dashboard MNC Group)

Pemakaian:
    python3 scripts/build_data.py raw/            # semua *.xlsx di folder raw/
    python3 scripts/build_data.py raw/Master_Data_3TV.xlsx

Prinsip yang TIDAK boleh dilanggar (alasan di komentar masing-masing):
  1. data.json hanya menyimpan angka yang BISA DIJUMLAHKAN (aditif).
     Rasio (CTR, AVD, %viewed, CPM, RPM) disimpan sebagai pembilang +
     penyebutnya, lalu dihitung ulang setelah agregasi. Merata-ratakan rasio
     antar channel pernah menghasilkan ER 285% (yang benar 0,99%).
  2. AVD dan RPM YouTube dihitung dari ENGAGED VIEWS, bukan Views.
     Diverifikasi ke Master_Data_3TV: pakai Views meleset median 8%,
     pakai Engaged views meleset < 0,3%.
  3. Unique viewers / Unique reach TIDAK aditif (penonton yang sama dihitung
     lagi di bulan/channel lain). Tidak masuk data.json supaya tidak ada yang
     tergoda menjumlahkannya.
"""
import json, sys, glob, os, datetime
import pandas as pd

# Peta Unit → Group. Tambahkan di sini saat ekosistem MNC lain masuk
# (mis. 'iNews': 'IMG'). Unit yang tidak terdaftar membuat build GAGAL,
# supaya unit baru tidak diam-diam jatuh ke grup yang salah.
UNIT_GROUP = {
    'RCTI': '3TV', 'GTV': '3TV', 'MNCTV': '3TV',
}

BULAN = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
         'August', 'September', 'October', 'November', 'December']

# kolom Excel → kunci aditif di data.json
ADITIF = {
    'Views': 'views',
    'Engaged views': 'eng_views',
    'Watch time (hours)': 'watch_hours',
    'Subscribers': 'subs',              # net gain per bulan → boleh dijumlah
    'Videos published': 'videos',
    'Thumbnail impressions': 'impressions',
    'Likes': 'likes',
    'Dislikes': 'dislikes',
    'Shares': 'shares',
    'Comments added': 'comments',
    'End screen element clicks': 'endscreen_clicks',
    'Card clicks': 'card_clicks',
    'Estimated revenue (IDR)': 'revenue',
    'YouTube ad revenue (IDR)': 'ad_revenue',
    'Ad impressions': 'ad_impressions',
    'Estimated monetized playbacks': 'monetized_playbacks',
    'Product clicks': 'product_clicks',
    'Product impressions': 'product_impressions',
    'Total sales (IDR)': 'sales',
    'Orders': 'orders',
    'Earned revenue (IDR)': 'earned_revenue',
    'Earned commission (IDR)': 'earned_commission',
}
# Pembilang turunan: rasio di Excel dikali penyebutnya supaya jadi aditif.
#   imp_clicks  = impressions × CTR%      → CTR = imp_clicks / impressions
#   pct_viewed_w = %viewed × eng_views    → %viewed = pct_viewed_w / eng_views
TURUNAN = ['imp_clicks', 'pct_viewed_w']

KEY = ['period', 'platform', 'group', 'unit', 'channel']


def detik(s):
    if pd.isna(s):
        return None
    p = [int(x) for x in str(s).split(':')]
    return p[0] * 3600 + p[1] * 60 + p[2]


def baca(path):
    df = pd.read_excel(path, sheet_name='Monthly')
    for c in ['Platform', 'Unit', 'Channel', 'Month']:
        df[c] = df[c].astype('string').str.strip()

    # Baris tanpa Channel atau tanpa satu pun angka = baris kosong/cadangan
    # (Master_Data_3TV punya 6 baris begini di Nov–Des 2025, salah satunya
    # "GTV Comedy" berlabel RCTI). Dibuang, dan jumlahnya dilaporkan.
    angka = [c for c in ADITIF if c in df.columns]
    kosong = df['Channel'].isna() | df[angka].isna().all(axis=1)
    print(f'  {os.path.basename(path)}: {len(df)} baris, {kosong.sum()} kosong dibuang')
    df = df[~kosong].copy()

    tak_dikenal = set(df['Unit']) - set(UNIT_GROUP)
    if tak_dikenal:
        sys.exit(f'GAGAL: Unit belum dipetakan ke Group: {tak_dikenal}. Tambahkan di UNIT_GROUP.')

    salah_bulan = set(df['Month']) - set(BULAN)
    if salah_bulan:
        sys.exit(f'GAGAL: nama bulan tidak dikenal: {salah_bulan}')

    df['period'] = df['Year'].astype(int).astype(str) + '-' + \
        df['Month'].map(lambda m: f'{BULAN.index(m) + 1:02d}')
    df['platform'] = df['Platform']
    df['group'] = df['Unit'].map(UNIT_GROUP)
    df['unit'] = df['Unit']
    df['channel'] = df['Channel']

    out = df[KEY].copy()
    for src, k in ADITIF.items():
        out[k] = pd.to_numeric(df[src], errors='coerce') if src in df.columns else None
    out['imp_clicks'] = out['impressions'] * pd.to_numeric(df['Thumbnail click-through rate (%)'], errors='coerce') / 100
    out['pct_viewed_w'] = out['eng_views'] * pd.to_numeric(df['Average percentage viewed (%)'], errors='coerce')
    out['_avd_excel'] = df['Average view duration'].map(detik)
    out['_rpm_excel'] = pd.to_numeric(df['RPM (IDR)'], errors='coerce')
    return out


def verifikasi(df):
    """Rumus rasio harus bisa merekonstruksi angka Excel per baris."""
    import numpy as np
    m = df['eng_views'] > 0
    avd = df.loc[m, 'watch_hours'] * 3600 / df.loc[m, 'eng_views']
    err = ((avd - df.loc[m, '_avd_excel']).abs() / df.loc[m, '_avd_excel'].clip(lower=1)).median()
    r = m & (df['_rpm_excel'] > 0)
    rpm = df.loc[r, 'revenue'] / df.loc[r, 'eng_views'] * 1000
    err2 = ((rpm - df.loc[r, '_rpm_excel']).abs() / df.loc[r, '_rpm_excel']).median()
    print(f'  cek AVD = watch/eng_views : selisih median {err:.3%}')
    print(f'  cek RPM = rev/eng_views   : selisih median {err2:.3%}')
    if err > 0.01 or err2 > 0.01:
        sys.exit('GAGAL: rumus AVD/RPM tidak cocok dengan Excel — periksa sumbernya.')


def main(paths):
    files = []
    for p in paths:
        files += sorted(glob.glob(os.path.join(p, '*.xlsx'))) if os.path.isdir(p) else [p]
    if not files:
        sys.exit('GAGAL: tidak ada berkas .xlsx')
    print('Membaca:')
    df = pd.concat([baca(f) for f in files], ignore_index=True)

    dup = df.duplicated(KEY, keep=False)
    if dup.any():
        print(df.loc[dup, KEY].to_string())
        sys.exit('GAGAL: ada channel × bulan ganda (lihat di atas). '
                 'Kemungkinan dua channel bernama sama — beri nama pembeda di Excel.')

    verifikasi(df)
    df = df.drop(columns=['_avd_excel', '_rpm_excel']).sort_values(KEY)

    metrik = list(ADITIF.values()) + TURUNAN
    rows = []
    for rec in df.itertuples(index=False):
        d = rec._asdict()
        rows.append([d[k] for k in KEY] +
                    [None if pd.isna(d[k]) else round(float(d[k]), 4) for k in metrik])

    build_path = os.path.join(os.path.dirname(__file__), '..', 'data.json')
    data = {
        'meta': {
            'generated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'sources': [os.path.basename(f) for f in files],
            'periods': sorted(df['period'].unique().tolist()),
            'groups': {g: sorted(df.loc[df['group'] == g, 'unit'].unique().tolist())
                       for g in sorted(df['group'].unique())},
            'channels': {u: sorted(df.loc[df['unit'] == u, 'channel'].unique().tolist())
                         for u in sorted(df['unit'].unique())},
        },
        'columns': KEY + metrik,
        'rows': rows,
    }
    with open(build_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    print(f'\ndata.json: {len(rows)} baris, {len(data["meta"]["periods"])} periode '
          f'({data["meta"]["periods"][0]} s/d {data["meta"]["periods"][-1]}), '
          f'{df["channel"].nunique()} channel, {os.path.getsize(build_path)/1024:.0f} KB')
    # Angka acuan: cocokkan ke Excel (pivot sederhana) sebelum menyatakan beres.
    acuan = df.groupby(['unit', df['period'].str[:4]])[['views', 'revenue']].sum() / 1e6
    print('\nAngka acuan (juta):')
    print(acuan.round(2).to_string())


if __name__ == '__main__':
    main(sys.argv[1:] or ['raw'])
