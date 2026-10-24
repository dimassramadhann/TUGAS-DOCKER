# Image dasar Python yang ringan untuk menjalankan aplikasi Flask.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instal dependensi terlebih dahulu agar layer dependency dapat digunakan kembali.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin source code aplikasi ke image.
COPY app.py .
COPY templates/ ./templates/

# Aplikasi dilayani Gunicorn pada port 5000 di dalam container.
EXPOSE 5000

# Jalankan sebagai user non-root untuk mengurangi hak akses proses aplikasi.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
