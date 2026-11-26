# Monitoring Anomali Data (Reviu Banpang) — mockup

Mockup dashboard SPI · Reviu TI. **Seluruh angka adalah data contoh (dummy), bukan data riil.**

## Struktur
- `index.html` — tampilan dashboard (Versi 1: Reviu Data; Versi 2: Reviu Data dan Foto)
- `data/cutoff-C/tahap-N.json` — agregat per provinsi untuk Cutoff C, Tahap N (halaman Ringkasan)
- `data/cutoff-C/temuan-tahap-N.csv` — contoh baris temuan untuk Cutoff C, Tahap N (halaman Daftar temuan; juga bisa diimpor ke Power BI)
- `data/cutoff-C/wilayah-tahap-1.csv` — rincian per kelurahan untuk Tahap 1 (PBP asli; sudah reviu dan belum sesuai contoh), dipakai kartu Rincian Wilayah
- `data/sumber/` — sumber PBP asli Tahap 1
- `scripts/generate_data.py` — pembangkit data contoh

## Total PBP per tahap
| Tahap | Tanggal | Total PBP |
|---|---|---|
| 1 | 25 November 2026 | 350.854 (PBP asli, lihat catatan) |
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
| 1 | 25 November 2026 | 1 Januari 2027 |
| 2 | 29 November 2026 | 8 Januari 2027 |
| 3 | 5 Desember 2026 | 15 Januari 2027 |
 Total PBP suatu tahap sama di kedua cutoff; yang berbeda adalah progres reviu dan jumlah temuan (Cutoff 2 lebih maju).

Pilihan Tahap "Semua Tahap (Tahap 1–3)" menjumlahkan ketiga tahap pada cutoff terpilih (dihitung di browser dari file yang sama).

## Sumber PBP asli (Tahap 1)
Jumlah PBP per provinsi untuk Tahap 1 (kedua cutoff) berasal dari `STATUS_VERIFIKASI_BANPANG.xlsx` (sheet TAHAP I, 29 provinsi, total 350.854), dengan rincian per kelurahan di `data/sumber/pbp-tahap-1-per-kelurahan.csv` (1.251 kelurahan, 206 kecamatan, 91 kabupaten/kota). Hanya PBP yang asli; hasil reviu, temuan, komposisi, dan foto tetap data contoh. Tahap 2 dan 3 sepenuhnya contoh.

## Rincian Wilayah
Kartu "Rincian Wilayah" di halaman Ringkasan menelusuri provinsi → kabupaten/kota → kecamatan → kelurahan/desa dengan kotak cari. Hanya tersedia untuk Tahap 1 (data per kelurahan); tahap lain dan "Semua Tahap" menampilkan keterangan. Memilih provinsi di kartu ini ikut menyaring seluruh dashboard. Halaman Daftar temuan punya kotak "Cari wilayah"; pada Tahap 1 baris contoh memakai nama wilayah asli (temuannya tetap contoh).

## Cutoff dan Tahap
- Kartu "Total PBP" menampilkan dua angka: jumlah Cutoff (Tahap 1–3) dan jumlah Tahap yang dipilih. Chart pertama membandingkan porsi tiap tahap terhadap total cutoff; chart lainnya memakai data tahap yang dipilih.
- Cutoff 1 (20 November 2026): total PBP seluruh tahap = 822.696, dari data asli "Tersalur 100% per 20 Nov 2026" (`data/sumber/tersalur-cutoff-1-per-provinsi.csv`). Tahap 1 = 350.854 (asli); Tahap 2 dan 3 = selisih (471.842) yang dibagi secara contoh per provinsi.
- Cutoff 2 (30 Desember 2026): seluruhnya contoh; total cutoff = Tahap 1 + 2 + 3.

## Mengubah data
Ubah `total`, `seed`, atau rentang rasio di `STAGES` pada `scripts/generate_data.py`, lalu jalankan `python3 scripts/generate_data.py`.

## Menjalankan lokal
Halaman membaca file di `data/` lewat `fetch`, jadi harus dibuka lewat server web (klik dua kali file HTML tidak akan memuat data):

    python3 -m http.server 8000   # lalu buka http://localhost:8000

## Catatan
- CSV temuan hanya contoh (±2.000 baris per tahap); jumlah temuan total ada di kartu dan JSON.
- Skema JSON: `cutoff`, `tahap`, dan `provinsi[]` berisi `pbp`, `sudah_reviu`, `belum_sesuai`, `komposisi{}`, `kategori_belum_sesuai{}`, `review_foto{}`.
