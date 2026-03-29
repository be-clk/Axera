# Axera

Web sitesi: 
https://axera-snowy.vercel.app


🚀 TUA AXERA — Hibrit Görev Kontrol Merkezi
TUA AXERA, gerçek zamanlı verileri modern web teknolojileriyle birleştiren bir fırlatma karar destek sistemi ve 3D uçuş simülasyonudur. Bu proje, meteorolojik limitler ve uzay havası parametrelerini analiz ederek bir roket fırlatma operasyonunun güvenliğini denetler.

📑 Proje Özeti
Sistem, OpenWeather ve NOAA API'lerinden gelen anlık verileri kullanarak karmaşık bir fırlatma analizi gerçekleştirir. Kullanıcı arayüzü, Three.js tabanlı motoru sayesinde telemetri verilerini görsel bir şölene dönüştürürken, backend servisi her fırlatmanın mühendislik limitlerini (kriyojenik yakıt ısısı, iyonosferik riskler, rüzgar makaslaması vb.) denetler.

✨ Temel Özellikler
Gerçek Zamanlı Veri Entegrasyonu: OpenWeather ile yerel hava durumu, NOAA ile Kp-Index (Jeomanyetik) ve radyasyon fırtınası verilerinin anlık takibi.

Gelişmiş 3D Simülasyon: Three.js kullanılarak oluşturulan; 1. kademe ayrılması (Stage Separation), motor alev efektleri ve dinamik atmosferik shader'lar içeren motor.

Akıllı Karar Mekanizması: Rüzgar hızı, görüş mesafesi, bulut yoğunluğu ve 20'den fazla teknik parametreye dayalı "GO / SCRUB" analizi.

Telemetri Paneli: İrtifa, hız, G-kuvveti ve motor basıncı gibi kritik verilerin canlı grafiksel takibi.

Görev Günlüğü: Geçmiş fırlatma denemelerinin nedenleriyle birlikte CSV formatında loglanması ve incelenmesi.

🛠 Teknik Mimari
Backend (Python/Flask)
API: NOAA ve OpenWeather JSON servisleri ile veri alışverişi.

Mühendislik: Fırlatma sahasının enlemine bağlı olarak $1670 \cdot \cos(\text{lat})$ formülüyle ekvatoral hız desteği hesaplaması.

Veri Yönetimi: Fırlatma kararlarının analizi ve axera_firlatma_loglari.csv dosyasına kaydedilmesi.

Frontend (JavaScript/Three.js/HTML5)
Görselleştirme: WebGL tabanlı roket modelleri, parçacık sistemleri (egzoz dumanı) ve dinamik ışıklandırma.

HUD & UI: Orbitron ve Share Tech Mono fontları ile tasarlanmış, siber-punk estetiğine sahip kontrol paneli.

Shader'lar: Güneşin konumuna göre değişen Rayleigh saçılması simülasyonu.

🚀 Kurulum ve Çalıştırma
Gereksinimleri Yükleyin:

Bash
pip install flask flask-cors requests
Backend Sunucusunu Başlatın:

Bash
python backend.py
Arayüzü Açın:
index.html dosyasını tarayıcınızda açarak kontrol merkezine giriş yapın.

🛰 Fırlatma Sahaları & Envanter
Proje kapsamında aşağıdaki stratejik noktalar desteklenmektedir:

Kismaayo (Somali - TUA Ana Ekvator Üssü)

Kennedy Space Center (ABD)

Kourou (Fransız Guyanası)

Hambantota (Sri Lanka)
