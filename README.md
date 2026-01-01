# Vodafone Tarife Scraper

Vodafone ve benzeri operatör sitelerinden tarife bilgilerini otomatik olarak çekip Excel'e kaydeden Python ajanı.

## 🚀 Hızlı Başlangıç

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Playwright tarayıcısını kur
playwright install chromium

# Scripti çalıştır
python scraper.py
```

## 📁 Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `scraper.py` | Ana scraping scripti |
| `config.json` | URL listesi ve ayarlar |
| `tarifeler.xlsx` | Çıktı dosyası (çalıştırınca oluşur) |

## ⚙️ Yapılandırma

`config.json` dosyasını düzenleyerek yeni siteler ekleyebilirsiniz:

```json
{
  "urls": [
    {
      "name": "Vodafone",
      "url": "https://www.vodafone.com.tr/numara-tasima-yeni-hat/tarifeler"
    }
  ],
  "output_file": "tarifeler.xlsx"
}
```

## 🔄 Düzenli Çalıştırma (Cron)

Her gün saat 09:00'da çalıştırmak için:

```bash
crontab -e
# Ekle:
0 9 * * * cd /path/to/project && python scraper.py
```

## 📊 Çıktı Formatı

Excel dosyasında şu kolonlar bulunur:
- Paket Adı
- İnternet (GB)
- Dakika
- SMS
- Fiyat (₺/ay)
- Kaynak
- Tarih
