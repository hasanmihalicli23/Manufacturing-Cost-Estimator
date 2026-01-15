```markdown
# 🏭 Maliyet Analizi ve Otomatik Teklif Sistemi

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-007ACC?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)

> **Makine mühendisliği ve imalat sektörü için geliştirilmiş; anlık kur takibi, dinamik maliyet analizi ve otomatik PDF raporlama yapan profesyonel masaüstü otomasyonu.**

---

## 🚀 Proje Hakkında

İmalat sektöründe teklif hazırlamak, genellikle karmaşık Excel dosyaları ve manuel hesaplamalarla yürütülen, hataya açık bir süreçtir. 

Bu proje, bu süreci **dijitalleştirmek ve otomatize etmek** amacıyla geliştirilmiştir. Yazılım, **TCMB (Merkez Bankası)** servislerinden anlık döviz kurlarını çeker, malzeme, işçilik ve fason giderlerini birleştirerek saniyeler içinde **kurumsal teklif formatında PDF** oluşturur.

---

## 🌟 Temel Özellikler

### 1. ⚙️ Dinamik Hesaplama Motoru
* **Malzeme Giderleri:** JSON tabanlı katalogdan ürün seçimi veya manuel giriş.
* **İşçilik Maliyeti:** Adam/Saat bazlı atölye gider hesabı.
* **Fason (Dış Hizmet):** Lazer kesim, kaplama, ısıl işlem vb. harici giderlerin entegrasyonu.

### 2. 💲 Canlı Kur Takibi
* **TCMB Entegrasyonu:** Uygulama açıldığında ve çalıştığı sürece USD ve EUR kurlarını Merkez Bankası'ndan anlık çeker.
* **Otomatik Dönüşüm:** Girilen giderleri (TL/USD/EUR) güncel kur üzerinden çapraz hesaplar.

### 3. 📄 Profesyonel Raporlama
* **PDF Teklifi:** Müşteriye sunulmaya hazır, kaşe/imza alanları içeren resmi teklif formatı.
* **Excel Dökümü:** Detaylı maliyet analizi ve arşivleme için `.xlsx` çıktısı.

### 4. 🎨 Modern Kullanıcı Arayüzü (UI)
* **CustomTkinter:** Standart arayüzler yerine modern, Windows 11 uyumlu ve **Dark Mode** destekli tasarım.
* **Responsive:** Kullanıcı dostu yerleşim ve renk kodlu butonlar.

---

## 🛠️ Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz.

### Gereksinimler
* Python 3.10 veya üzeri
* İnternet bağlantısı (Kur çekme işlemi için)

### 1. Projeyi Klonlayın
Terminal veya Komut İstemi'ni (CMD) açın ve şu komutları girin:
```bash
git clone [https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git](https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git)
cd Manufacturing-Cost-Estimator

```

### 2. Gerekli Kütüphaneleri Yükleyin

```bash
pip install customtkinter pandas requests reportlab openpyxl

```

### 3. Uygulamayı Başlatın

```bash
python maliyet.py

```

---

## 📂 Proje Yapısı

```
Manufacturing-Cost-Estimator/
├── maliyet.py          # Ana uygulama dosyası (Source Code)
├── katalog.json        # Ürün veritabanı (Otomatik oluşur)
├── ayarlar.json        # Kullanıcı ayarları
├── discount.ico        # Uygulama ikonu
├── README.md           # Proje dokümantasyonu
└── TEKLİFLER/          # Oluşturulan PDF ve Excel dosyaları buraya kaydedilir

```

---

## 👨‍💻 Geliştirici

**Hasan Mıhalıçlı** 

Projelerimi incelemek ve iletişime geçmek için:

* [LinkedIn Profilim](https://www.google.com/search?q=https://www.linkedin.com/in/hasanmihalicli23/)
* [GitHub Profilim](https://www.google.com/search?q=https://github.com/hasanmihalicli23)

---

## 📄 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır. Kaynak gösterilerek ticari veya bireysel amaçlarla özgürce kullanılabilir, geliştirilebilir.

```

```
