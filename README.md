# Image Comparison Slider (Flask)

Aplikasi web sederhana untuk membandingkan dua gambar (`Before` vs `After`) dengan slider interaktif pada satu halaman.

## Fitur

- Upload 2 gambar (`.jpg`, `.jpeg`, `.png`)
- Validasi file gambar dan batas ukuran (100MB per gambar)
- Compare slider interaktif (before/after)
- Preview gambar sebelum proses compare
- Tombol `Reset` untuk menghapus hasil compare aktif
- File upload aktif tetap tersedia sampai di-reset atau dibersihkan otomatis (cleanup berdasarkan umur file)
- **Dark Mode / Light Mode** — toggle tema gelap & terang dengan persistensi via `localStorage` (mengikuti preferensi OS secara default)

## Stack

- Python 3.x
- Flask
- Pillow (PIL)
- Tailwind CSS (CDN)
- `img-comparison-slider` (Web Component via CDN)

## Struktur Proyek

```text
compare image/
├─ app.py
├─ requirements.txt
├─ templates/
│  ├─ index.html
│  └─ result.html
├─ uploads/
│  └─ .gitkeep
└─ README.md
```

## Instalasi

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```bash
python app.py
```

Default URL:

- `http://127.0.0.1:5050`

## Konfigurasi Utama

Di `app.py`:

- `MAX_FILE_SIZE = 104857600` (100MB per gambar)
- `app.config["MAX_CONTENT_LENGTH"] = 210239488` (total request)
- `CLEANUP_MAX_AGE_SECONDS = 60 * 60` (cleanup file lama)

## Catatan

- Jika ada warning import di VS Code (Pylance), pastikan interpreter yang dipilih adalah `.venv` project ini.
- Dialog konfirmasi refresh/tab-close bergantung pada kebijakan browser modern (pesan custom tidak selalu ditampilkan).
