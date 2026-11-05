# Sistem Pemetaan Sentimen & Persepsi Publik Pembangunan Kota Padang 2026
### Inspektorat Daerah Kota Padang (Aparat Pengawasan Intern Pemerintah - APIP)

Repositori ini berisi sistem pemetaan sentimen publik, pipeline *Machine Learning / NLP*, laporan telaah risiko kebijakan, dan *dashboard* pengawasan interaktif untuk mengawal **9 Program Unggulan (Progul) Wali Kota Padang (Padang Satujuan)** periode September–November 2026.

---

## 📁 Struktur Direktori Bersih

```
Sentimen/
├── README.md                      # Panduan utama sistem pengawasan
├── data/                          # Dataset pengaduan dan persepsi publik
│   ├── padang_social_media.csv    # Master dataset 260 rekaman (tautan berita/medsos riil)
│   ├── padang_social_media_template.csv # Templat format baku penarikan data
│   └── records_clean.json         # Dataset bersih berformat JSON untuk dashboard web
├── web/                           # Dashboard Antarmuka Pengawasan Eksekutif
│   ├── index.html                 # Dashboard interaktif utama (Antislop UI, standalone)
│   └── dashboard_inspektorat_padang_2026.html
├── scripts/                       # Skrip otomatisasi & pemrosesan data
│   └── youtube_api_ingestor.py    # Skrip ingest komentar YouTube Data API v3 + dialek Minang
├── notebooks/                     # Analisis Sains Data & Pemodelan NLP
│   └── PADANG_SENTIMENT_ANALYSIS_2026.ipynb # Pipeline scikit-learn (Naive Bayes, SVM, RF)
├── reports/                       # Dokumen Laporan Pengawasan & Matriks Tindak Lanjut
│   ├── ANALISIS_MENDALAM_GEMINI_2026.md     # Diseksi analitis mendalam & kuadran risiko AI
│   ├── LAPORAN_PENGAWASAN_INSPEKTORAT.md    # Telaah strategis APIP untuk pimpinan
│   ├── MATRIKS_REKOMENDASI_OPD.md           # Rincian peta masalah & aksi 5 OPD teknis
│   └── LAPORAN_PEMETAAN_SENTIMEN_FINAL.md   # Laporan komprehensif sentimen & persepsi
├── outputs/                       # Hasil ekspor model dan prediksi uji
│   ├── model_comparison.csv       # Evaluasi metrik (Akurasi Naive Bayes: 90.4%)
│   ├── test_predictions.csv       # Sampel prediksi data uji
│   └── padang_social_media_clean.csv # Dataset hasil prapemrosesan teks
└── archive/                       # Arsip file starter legacy
    ├── PADANG-SENTIMENT-ANALYSIS-2026-starter/
    └── PADANG-SENTIMENT-ANALYSIS-2026-starter.zip
```

---

## 🚀 Panduan Penggunaan Singkat

### 1. Menampilkan Dashboard di Monitor Inspektur / Pimpinan
Dashboard dirancang menggunakan standar *Antislop UI* (bebas distraksi, kontras tinggi, elegan, dan ringan) tanpa memerlukan server backend tambahan:
- Buka file **`web/index.html`** langsung menggunakan browser (Google Chrome, Microsoft Edge, atau Firefox).
- Dapat diproyeksikan langsung ke layar monitor ruang kerja Inspektur atau ruang rapat Sekda/Wali Kota.
- Dilengkapi fitur pencarian langsung (*live search*), filter kronologis per bulan (Nov 2026 -> Jan 2026), filter skala prioritas (*Tinggi*, *Sedang*, *Rendah*), filter 5 OPD teknis, tautan bukti riil, dan tombol cetak laporan (*Print to PDF*).
- **Fitur 1-Klik Gemini AI:** Pada tab *Matriks Rekomendasi*, klik tombol **"✨ Ringkas Sekarang dengan Gemini AI"** untuk mensintesis seluruh 47 data aduan riil menjadi telaah risiko pimpinan dan matriks aksi 30/90 hari 5 OPD secara otomatis menggunakan API Key Google AI Studio Anda.

### 2. Sintesis Cerdas via Terminal / CLI (Python Gemini Ingestor)
Anda juga dapat menjalankan sintesis AI langsung dari terminal untuk menghasilkan dokumen laporan markdown resmi di `reports/`:
```bash
python scripts/summarize_with_gemini.py AIzaSy_KUNCI_API_STUDIO_ANDA
```
Hasil sintesis akan tersimpan rapi di `reports/RINGKASAN_AI_GEMINI_REKOMENDASI.md`.

### 3. Mengintegrasikan Data Baru dari YouTube Data API v3
Jika Anda memiliki hasil tarikan data komentar dari YouTube API v3 (format `.json` atau `.csv`):
```bash
# Jalankan skrip penarikan otomatis dari folder utama:
python scripts/youtube_api_ingestor.py path/ke/file_komentar_youtube.json
```
*Fitur Skrip:*
- Menormalisasi dialek Minang secara otomatis (*indak -> tidak*, *tasumbek -> tersumbat*, *sarok -> sampah*, dll).
- Melakukan klasifikasi sentimen awal dan mendeteksi fokus isu (misalnya *Revitalisasi Pasar Raya*).
- Menggabungkan rekaman baru ke dalam `data/padang_social_media.csv` tanpa duplikasi.

### 3. Menjalankan Notebook Analisis Machine Learning
Jalankan file Jupyter Notebook di lingkungan Python:
```bash
jupyter notebook notebooks/PADANG_SENTIMENT_ANALYSIS_2026.ipynb
```
*Hasil Model Terbaik:*
- **Multinomial Naive Bayes:** Akurasi **90.4%** | F1-Macro **91.3%**
- **Linear Support Vector Machine (LinearSVC):** Akurasi **88.5%** | F1-Macro **89.2%**
- **Random Forest:** Akurasi **88.5%** | F1-Macro **89.3%**

---

## 🏛️ Fokus Pengawasan 5 OPD Teknis
Pengawasan difokuskan secara tajam pada dinas teknis utama dengan volume sentimen keluhan publik tertinggi:
1. **Dinas PUPR:** Penanganan banjir/drainase tersumbat (Koto Tangah, Ulak Karang) dan lubang jalan By Pass.
2. **Dinas Perhubungan:** Kemacetan tanjakan Sitinjau Lauik, penataan parkir Taplau, dan perluasan Trans Padang koridor 2 & 3.
3. **Dinas Perdagangan:** Aksesibilitas tangga/eskalator Fase VII Pasar Raya, penurunan omset pedagang, dan penataan PKL basah.
4. **Dinas Lingkungan Hidup (DLH):** Bau dan pengelolaan sampah TPA Air Dingin serta TPS liar sepanjang By Pass.
5. **Satpol PP:** Penertiban humanis tanpa kekerasan terhadap PKL liar Pantai Padang dan pemberantasan pungli parkir.

---

## ⚖️ Prinsip Integritas Bukti Pengawasan (APIP)
- **Immutabilitas Data:** Dataset rekaman publik tidak menerapkan fungsi *edit/delete* bebas (tanpa CRUD penuh) guna menjaga integritas dan keaslian bukti audit (*audit trail*) di hadapan hukum dan regulasi pengawasan.
- **Humanized Wording:** Seluruh narasi telaah risiko dan rekomendasi bebas dari istilah *AI slop*, disusun murni dengan bahasa kedinasan pengawasan yang lugas, terukur, dan berorientasi solusi konkret.

