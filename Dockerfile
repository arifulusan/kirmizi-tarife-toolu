# Playwright'ın resmi Python imajını kullanıyoruz (Sistem bağımlılıkları yüklü gelir)
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli dosyaları kopyala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Port ayarı (Render PORT environment variable kullanır)
ENV PORT=8000

# Uygulamayı başlat
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT}"]
