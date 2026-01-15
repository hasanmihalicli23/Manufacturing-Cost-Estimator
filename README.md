# 🏭 Maliyet Analizi ve Otomatik Teklif Sistemi (Manufacturing Cost Estimator)

> **Makine mühendisliği ve imalat sektörü için geliştirilmiş, Python tabanlı profesyonel maliyet hesaplama ve teklif oluşturma otomasyonu.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-007ACC)
![Status](https://img.shields.io/badge/Status-Stable-green)

---

## 🚀 Proje Hakkında

Bu proje, geleneksel yöntemlerle (Excel, defter-kalem) yapılan maliyet hesaplama ve teklif hazırlama süreçlerindeki zaman kaybını ve hata riskini ortadan kaldırmak için geliştirilmiştir. 

Yazılım, **TCMB (Merkez Bankası)** üzerinden anlık döviz kurlarını çeker, malzeme/işçilik giderlerini dinamik olarak hesaplar ve tek tıkla müşteriye sunulabilir **Profesyonel PDF Teklifi** oluşturur.

---

## 🌟 Temel Özellikler

* **🎨 Modern Arayüz (UI):** `CustomTkinter` kütüphanesi ile geliştirilmiş, kullanıcı dostu ve Dark Mode destekli arayüz.
* **live 💲 Canlı Kur Takibi:** TCMB entegrasyonu sayesinde USD ve EUR kurlarını anlık olarak çeker ve hesaplamalara yansıtır.
* **⚙️ Dinamik Hesaplama:** * **Hammadde & Malzeme:** Katalogdan seçim veya manuel giriş.
    * **Dış Hizmet (Fason):** Lazer kesim, kaplama, ısıl işlem vb. giderler.
    * **İşçilik:** Adam/Saat bazlı atölye maliyet hesabı.
* **📄 Otomatik Raporlama:**
    * **PDF:** Kaşe/İmza alanları hazır, kurumsal formatta teklif çıktısı.
    * **Excel:** Detaylı maliyet analizi ve veri dökümü.
* **💾 Akıllı Veritabanı:** Sık kullanılan ürünleri `JSON` tabanlı katalogda tutar, tekrar yazma zahmetinden kurtarır.
* **⏱️ Oto-Kayıt & Geçmiş:** Projeleri belirlediğiniz aralıklarla otomatik yedekler ve eski tekliflere erişim sağlar.

---

## 🛠️ Kurulum ve Çalıştırma

Projeyi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz.

### 1. Projeyi Klonlayın
```bash
git clone [https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git](https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git)
cd Manufacturing-Cost-Estimator
