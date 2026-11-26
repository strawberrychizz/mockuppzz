#!/usr/bin/env python3
"""Membangkitkan data contoh (dummy) per tahap ke folder data/.

Ubah angka di STAGES (total PBP, seed, rentang rasio) lalu jalankan:
    python3 scripts/generate_data.py
Hasil (untuk setiap Cutoff C dan Tahap N):
    data/cutoff-C/tahap-N.json         agregat per provinsi (dipakai halaman Ringkasan)
    data/cutoff-C/temuan-tahap-N.csv   contoh baris temuan (dipakai halaman Daftar temuan; bisa diimpor ke Power BI)
Total PBP suatu tahap sama di semua cutoff; yang berubah adalah progres reviu dan temuan.
Tahap 1 memakai PBP asli per provinsi dari data/sumber/ (hanya provinsi yang ada di file); metrik lainnya tetap contoh.
Tahap 1 sudah direviu 100% (sudah_reviu = pbp) di semua cutoff.
Cutoff 1: total Tahap 1+2+3 = data asli "Tersalur 100% per 20 Nov 2026"; Tahap 2 dan 3 = selisih terhadap Tahap 1 (dibagi contoh per provinsi).
Seluruh angka acak tetapi deterministik (seed tetap) dan BUKAN data riil.
"""
import csv, json, os, random

CUTOFFS = {1: "20 November 2026", 2: "30 Desember 2026"}
# tanggal = (Cutoff 1, Cutoff 2); reviu = rentang porsi Sudah Reviu, temuan = rentang porsi Belum Sesuai (terhadap PBP); indeks 0 = Cutoff 1, 1 = Cutoff 2
STAGES = [
    dict(n=1, nama="Tahap 1", tanggal=("25 November 2026", "1 Januari 2027"), sumber="data/sumber/pbp-tahap-1-per-kelurahan.csv", total=None,   seed=20261101, reviu=[(.44, .52), (.70, .80)],   temuan=[(.018, .10), (.03, .12)]),
    dict(n=2, nama="Tahap 2", tanggal=("29 November 2026", "8 Januari 2027"), total=1_535_324, seed=20261111, reviu=[(.66, .77), (.86, .93)],   temuan=[(.026, .145), (.04, .15)]),
    dict(n=3, nama="Tahap 3", tanggal=("5 Desember 2026", "15 Januari 2027"), total=2_341_243, seed=20261120, reviu=[(.86, .97), (.97, .995)],  temuan=[(.03, .17), (.05, .19)]),
]
SAMPLE_ROWS = 2000   # perkiraan jumlah baris contoh di CSV temuan per tahap

PROVINSI = ["Aceh","Sumatera Utara","Sumatera Barat","Riau","Jambi","Sumatera Selatan","Bengkulu","Lampung","Kep. Bangka Belitung","Kepulauan Riau","DKI Jakarta","Jawa Barat","Jawa Tengah","DI Yogyakarta","Jawa Timur","Banten","Bali","Nusa Tenggara Barat","Nusa Tenggara Timur","Kalimantan Barat","Kalimantan Tengah","Kalimantan Selatan","Kalimantan Timur","Kalimantan Utara","Sulawesi Utara","Sulawesi Tengah","Sulawesi Selatan","Sulawesi Tenggara","Gorontalo","Sulawesi Barat","Maluku","Maluku Utara","Papua","Papua Barat","Papua Selatan","Papua Tengah","Papua Pegunungan","Papua Barat Daya"]
BOBOT = {"Jawa Barat":520,"Jawa Tengah":480,"Jawa Timur":500,"Sulawesi Selatan":360,"Sumatera Utara":300,"Lampung":240,"Sumatera Selatan":230,"Banten":160,"DI Yogyakarta":120,"Nusa Tenggara Timur":170,"Aceh":170,"Kalimantan Barat":150,"Bali":90,"DKI Jakarta":90}
KOMPOSISI = [("Normal",.80),("Perwakilan 1 KK",.08),("Perwakilan",.06),("Pengganti",.04),("Kolektif",.02)]
KATEGORI = [("→ Perwakilan 1 KK",.24),("Terima >1x Normal/Peng.",.15),("Normal → Perw. beda KK",.12),("Peng. → Peng. >1x",.08),("Peng. → Perw. beda KK",.06),("Normal → Peng. lok. lain",.05)]
FOTO = [("Sama",.62),("Tidak Sama",.18),("Perlu Reviu",.14),("Ditolak",.06)]
MASK1 = ["Ab","Si","Na","Wa","Ra","Ha","Ju","Su","Ma","Ni","Ta","Yo","Fa","Er","Di","Ko"]
MASK2 = ["Su","Ha","Pu","Ju","Wi","Ka","Ma","Ru","Li","Be","So","Da"]
PET = ["PET LAP Ab***","PET LAP Su***","PET LAP Ha***","PET LAP Ni***","PET LAP Ko***"]
VER = ["Ri*** Mu*** Mi***","Wi*** Ha***","De*** Pu***","An*** Sa***"]

def split(n, w):  # pembagian n menurut bobot w, metode sisa terbesar (jumlah selalu tepat n)
    s = sum(w); raw = [x / s * n for x in w]; b = [int(x) for x in raw]
    for i in sorted(range(len(w)), key=lambda i: -(raw[i] - b[i]))[:n - sum(b)]:
        b[i] += 1
    return b

def jit(r, w, k):
    return [x * (1 + (r.random() - .5) * k) for x in w]

base_rng = random.Random(1234)
BASE = {p: BOBOT.get(p) or base_rng.uniform(28, 110) for p in PROVINSI}

for st in STAGES:
  for co, co_tgl in CUTOFFS.items():
    # PBP per provinsi sama di semua cutoff (seed tahap); sisanya memakai RNG milik cutoff
    r = random.Random(st["seed"])
    rem = None
    if co == 1 and st["n"] in (2, 3):
        # Cutoff 1: total PBP seluruh tahap = data asli "Tersalur 100% per 20 Nov 2026"; selisih terhadap Tahap 1 (asli) dibagi
        # ke Tahap 2 dan 3 secara contoh per provinsi, sehingga Tahap 1+2+3 = total cutoff per provinsi.
        with open("data/sumber/tersalur-cutoff-1-per-provinsi.csv", encoding="utf-8") as f:
            cut1 = {row["provinsi"]: int(row["pbp"]) for row in csv.DictReader(f)}
        t1 = {}
        with open(STAGES[0]["sumber"], encoding="utf-8") as f:
            for w_ in csv.DictReader(f):
                t1[w_["provinsi"]] = t1.get(w_["provinsi"], 0) + int(w_["pbp"])
        assert all(cut1[p] >= t1.get(p, 0) for p in t1), "Tahap 1 melebihi total cutoff"
        rs = random.Random(20261127)  # sama untuk Tahap 2 dan 3 agar jumlahnya = selisih
        rem = {}
        for p in PROVINSI:
            sisa = cut1.get(p, 0) - t1.get(p, 0)
            if sisa > 0:
                a_ = round(sisa * rs.uniform(.40, .70))
                rem[p] = a_ if st["n"] == 2 else sisa - a_
    if rem is not None:
        provs = [p for p in PROVINSI if rem.get(p, 0) > 0]; pbp = [rem[p] for p in provs]; total = sum(pbp)
    elif st.get("sumber"):  # PBP asli per provinsi dari file sumber (hanya provinsi yang ada di file)
        with open(st["sumber"], encoding="utf-8") as f:
            wil = list(csv.DictReader(f))
        src = {}
        for w_ in wil:
            src[w_["provinsi"]] = src.get(w_["provinsi"], 0) + int(w_["pbp"])
        provs = [p for p in PROVINSI if p in src]; pbp = [src[p] for p in provs]; total = sum(pbp)
    else:
        provs = PROVINSI; total = st["total"]
        pbp = split(total, [BASE[p] * r.uniform(.9, 1.1) for p in PROVINSI])
    if co > 1:
        r = random.Random(st["seed"] + 1000 * co)
    os.makedirs(f"data/cutoff-{co}", exist_ok=True)
    out = []
    for p, n in zip(provs, pbp):
        tem = max(2, round(n * r.uniform(*st["temuan"][co - 1])))
        rv = max(tem, round(n * r.uniform(*st["reviu"][co - 1])))
        if st.get("sumber"):
            rv = n  # Tahap 1 sudah direviu 100%
        cm = split(n, jit(r, [w for _, w in KOMPOSISI], .3))
        cc = split(tem, jit(r, [w for _, w in KATEGORI], .7))
        rl = split(n, jit(r, [w for _, w in FOTO], .4))
        out.append({"provinsi": p, "pbp": n, "sudah_reviu": rv, "belum_sesuai": tem,
                    "komposisi": {k: v for (k, _), v in zip(KOMPOSISI, cm)},
                    "kategori_belum_sesuai": {k: v for (k, _), v in zip(KATEGORI, cc)},
                    "review_foto": {k: v for (k, _), v in zip(FOTO, rl)}})
    assert sum(o["pbp"] for o in out) == total
    with open(f"data/cutoff-{co}/tahap-{st['n']}.json", "w", encoding="utf-8") as f:
        json.dump({"cutoff": f"Cutoff {co}", "tanggal_cutoff": co_tgl, "tahap": st["nama"], "tanggal": st["tanggal"][co - 1], "total_pbp": total, **({"catatan": "Cutoff 1: total Tahap 1+2+3 = data asli Tersalur 100% per 20 Nov 2026; pembagian Tahap 2 dan 3 adalah contoh"} if rem is not None else {}), **({"sumber_pbp": "STATUS_VERIFIKASI_BANPANG.xlsx (TAHAP I): PBP asli; hasil reviu, temuan, komposisi, dan foto adalah contoh", "wilayah": "wilayah-tahap-1.csv"} if st.get("sumber") else {}), "provinsi": out}, f, ensure_ascii=False, indent=1)

    # rincian per kelurahan (hanya tahap dengan sumber asli): PBP asli; sudah_reviu dan belum_sesuai = pembagian contoh dari nilai provinsi
    kel_by_prov = {}
    if st.get("sumber"):
        prov_out = {o["provinsi"]: o for o in out}
        with open(f"data/cutoff-{co}/wilayah-tahap-1.csv", "w", encoding="utf-8", newline="") as f:
            wcsv = csv.writer(f)
            wcsv.writerow(["provinsi", "kabupaten_kota", "kecamatan", "kelurahan", "id_wilayah", "pbp", "sudah_reviu", "belum_sesuai"])
            for p in provs:
                ks = [w_ for w_ in wil if w_["provinsi"] == p]
                pb = [int(w_["pbp"]) for w_ in ks]
                rvk = split(prov_out[p]["sudah_reviu"], [x * r.uniform(.7, 1.3) for x in pb])
                tmk = split(prov_out[p]["belum_sesuai"], [x * r.uniform(.6, 1.4) for x in rvk])
                def capped(vals, caps, total):  # batasi per baris, sisa dibagikan ke baris yang masih punya ruang (jumlah tetap)
                    vals = [min(v, c) for v, c in zip(vals, caps)]
                    left = total - sum(vals)
                    while left > 0:
                        room = [i for i, (v, c) in enumerate(zip(vals, caps)) if v < c]
                        assert room, "tidak ada ruang untuk membagi sisa"
                        for i in room[:left]:
                            vals[i] += 1; left -= 1
                    return vals
                rvk = capped(rvk, pb, prov_out[p]["sudah_reviu"])                      # sudah_reviu <= PBP
                tmk = capped(tmk, rvk, prov_out[p]["belum_sesuai"])                    # belum_sesuai <= sudah_reviu
                for i, w_ in enumerate(ks):
                    wcsv.writerow([p, w_["kabupaten_kota"], w_["kecamatan"], w_["kelurahan"], w_["id_wilayah"], pb[i], rvk[i], tmk[i]])
                kel_by_prov[p] = (ks, tmk)

    # contoh baris temuan: proporsional per (provinsi, kategori), minimal 1 baris bila ada temuan
    tot_tem = sum(o["belum_sesuai"] for o in out); frac = SAMPLE_ROWS / tot_tem
    cells = [(o["provinsi"], k, v) for o in out for k, v in o["kategori_belum_sesuai"].items() if v > 0]
    rows = []
    for prov, kat, v in cells:
        for _ in range(min(v, max(1, round(v * frac)))):
            if prov in kel_by_prov and sum(kel_by_prov[prov][1]) > 0:
                ks, tmk = kel_by_prov[prov]
                w_ = r.choices(ks, weights=tmk)[0]
                rows.append([kat, prov, w_["kabupaten_kota"], w_["kecamatan"], w_["kelurahan"]])
            else:
                rows.append([kat, prov, f"Kota {r.randint(1,3)}", f"Kecamatan {r.randint(1,3)}", f"Desa {r.randint(1,4)}"])
    ids = r.sample(range(1_000_000, 1_000_000 + total * 2), len(rows))
    for row, i in zip(rows, ids):
        ss = r.choices(["Diserahkan", "Belum diserahkan"], [92, 8])[0]
        vs = r.choices(["Verified", "Unverified"], [75, 25])[0]
        row += [f"PBP-{i:07d}", f"{r.choice(MASK1)}*** {r.choice(MASK2)}***",
                ss, r.choice(PET) if ss == "Diserahkan" else "",
                vs, r.choice(VER) if vs == "Verified" else "",
                r.choices(["Sudah Sesuai", "Belum Sesuai"], [40, 60])[0],
                r.choices(["Belum Direviu", "Sudah Sesuai", "Belum Sesuai"], [70, 18, 12])[0]]
    with open(f"data/cutoff-{co}/temuan-tahap-{st['n']}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kategori", "provinsi", "kota_kab", "kecamatan", "kel_desa", "no_pbp", "nama_disamarkan", "status_serah", "oleh_serah", "status_verifikasi", "oleh_verifikasi", "hasil_review_data", "hasil_review_foto"])
        w.writerows(rows)
    print(f"Cutoff {co}", st["nama"], "PBP", total, "temuan", tot_tem, "baris contoh", len(rows))
