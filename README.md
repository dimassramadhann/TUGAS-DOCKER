# Task Manager — Praktikum Komputasi Awan

Aplikasi web sederhana untuk menambah, melihat, menyelesaikan, dan menghapus tugas. Stack: Flask, Gunicorn, MySQL 8.4, Docker, dan Docker Compose.

## File utama
- `app.py`: route Flask dan operasi database.
- `Dockerfile`: membangun image aplikasi sendiri.
- `compose.yaml`: service aplikasi dan MySQL, network terpisah, volume, health check, dan restart policy.
- `.env.example`: contoh variabel lingkungan. Salin sebagai `.env` dan ganti nilainya.
- `.gitignore`: mengecualikan `.env` dari Git.

## Menjalankan lokal
1. Salin `.env.example` menjadi `.env`.
2. Ganti seluruh password dan secret contoh di `.env`.
3. Jalankan `docker compose config` untuk memeriksa konfigurasi.
4. Jalankan `docker compose up -d --build`.
5. Periksa dengan `docker compose ps` dan buka `http://localhost`.

## Catatan keamanan
Database tidak mem-publish port ke host dan hanya berada di network `backend` dengan `internal: true`. Service aplikasi terhubung ke network `frontend` dan `backend`. Jangan commit file `.env` ke repository.
