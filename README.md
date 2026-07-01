# Ganoderma Detect — Web App Lokal

Web app sederhana untuk menjalankan model YOLO (`best.pt`) hasil training Anda
melalui browser, sesuai struktur folder yang sudah Anda siapkan
(`input/`, `model/`, `output/`).

## Struktur folder

```
ganoderma_web/
├── app.py                 # Backend Flask
├── requirements.txt
├── model/
│   └── best.pt             # ← LETAKKAN model hasil training Anda di sini
├── input/                  # Citra yang diunggah lewat web akan disimpan di sini
├── output/                 # Hasil deteksi YOLO (mirip runs/predict) disimpan di sini
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## Cara menjalankan

1. **Pindahkan model Anda**
   Salin file `best.pt` (dari `model/best.pt` pada project Anda sebelumnya) ke
   dalam folder `model/` project ini.

2. **Buat virtual environment (disarankan)**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependency**
   ```bash
   pip install -r requirements.txt
   ```
   > Catatan: `ultralytics` akan otomatis menarik `torch`. Jika Anda punya GPU
   > dan ingin memakai CUDA, install `torch` versi CUDA terlebih dahulu sesuai
   > panduan di https://pytorch.org sebelum menjalankan perintah di atas.

4. **Jalankan server**
   ```bash
   python app.py
   ```

5. **Buka di browser**
   ```
   http://127.0.0.1:5000
   ```

## Cara pakai

- Tarik-letakkan (drag & drop) atau klik untuk memilih citra pangkal batang.
- Klik gambar → server otomatis menyimpannya ke `input/`, menjalankan
  `model.predict()`, lalu menampilkan hasil anotasi beserta daftar objek yang
  terdeteksi dan tingkat keyakinannya.
- Setiap hasil prediksi tersimpan permanen di `output/predict_<timestamp>/`,
  jadi riwayat deteksi tidak akan tertimpa.

## Kustomisasi cepat

- **Ganti port**: ubah `port=5000` di baris terakhir `app.py`.
- **Ubah ukuran maksimum upload**: ubah `MAX_CONTENT_LENGTH` di `app.py`.
- **Tambah confidence threshold**: tambahkan `conf=0.25` (atau nilai lain)
  pada pemanggilan `model.predict(...)` di `app.py`.
- **Deploy ke jaringan lokal (LAN)**: ganti `host="127.0.0.1"` menjadi
  `host="0.0.0.0"` agar bisa diakses dari perangkat lain di jaringan yang sama.

## Troubleshooting

| Masalah | Penyebab umum |
|---|---|
| Status "best.pt tidak ditemukan" di pojok kanan atas | File model belum ada di `model/best.pt` |
| `ModuleNotFoundError: ultralytics` | Belum menjalankan `pip install -r requirements.txt` |
| Prediksi sangat lambat | Berjalan di CPU; pertimbangkan install `torch` versi CUDA jika ada GPU |
| Error saat load model | Periksa apakah `best.pt` cocok dengan versi `ultralytics` yang terinstall |
