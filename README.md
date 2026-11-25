# Monitoring Anomali Data (Reviu Banpang) — mockup

Mockup dashboard SPI · Reviu TI. **Seluruh angka adalah data contoh (dummy), bukan data riil.**

## Struktur
- `index.html` — tampilan dashboard (Versi 1: Reviu Data; Versi 2: Reviu Data dan Foto)
- `data/cutoff-C/tahap-N.json` — agregat per provinsi untuk Cutoff C, Tahap N (halaman Ringkasan)
- `data/cutoff-C/temuan-tahap-N.csv` — contoh baris temuan untuk Cutoff C, Tahap N (halaman Daftar temuan; juga bisa diimpor ke Power BI)
- `scripts/generate_data.py` — pembangkit data contoh

## Total PBP per tahap
| Tahap | Tanggal | Total PBP |
|---|---|---|
| 1 | 20 November 2026 | 822.000 |
| 2 | 29 November 2026 | 1.535.324 |
| 3 | 5 Desember 2026 | 2.341.243 |

## Cutoff
| Cutoff | Tanggal |
|---|---|
| 1 | 20 November 2026 |
| 2 | 30 Desember 2026 |

Setiap cutoff memuat Tahap 1–3 dengan tanggal berbeda:

| Tahap | Cutoff 1 | Cutoff 2 |
|---|---|---|
| 1 | 20 November 2026 | 1 Januari 2027 |
| 2 | 29 November 2026 | 8 Januari 2027 |
| 3 | 5 Desember 2026 | 15 Januari 2027 |
 Total PBP suatu tahap sama di kedua cutoff; yang berbeda adalah progres reviu dan jumlah temuan (Cutoff 2 lebih maju).

## Mengubah data
Ubah `total`, `seed`, atau rentang rasio di `STAGES` pada `scripts/generate_data.py`, lalu jalankan `python3 scripts/generate_data.py`.

## Menjalankan lokal
Halaman membaca file di `data/` lewat `fetch`, jadi harus dibuka lewat server web (klik dua kali file HTML tidak akan memuat data):

    python3 -m http.server 8000   # lalu buka http://localhost:8000

## Catatan
- CSV temuan hanya contoh (±2.000 baris per tahap); jumlah temuan total ada di kartu dan JSON.
- Skema JSON: `cutoff`, `tahap`, dan `provinsi[]` berisi `pbp`, `sudah_reviu`, `belum_sesuai`, `komposisi{}`, `kategori_belum_sesuai{}`, `review_foto{}`.
