<div align="center">

  # 🏭 Maliyet Analizi ve Otomatik Teklif Sistemi
  
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-007ACC?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge" />

  <br />
  <br />

  > **Makine mühendisliği ve imalat sektörü için geliştirilmiş; anlık kur takibi, dinamik maliyet analizi ve otomatik PDF raporlama yapan profesyonel masaüstü otomasyonu.**

  <br />

  <img src="https://via.placeholder.com/800x400.png?text=Uygulama+Onizleme+(Gorsel+Yukleyin)" alt="Uygulama Önizleme" width="800">

</div>

---

## 🚀 Proje Hakkında

İmalat sektöründe teklif hazırlamak, genellikle karmaşık Excel dosyaları ve manuel hesaplamalarla yürütülen, hataya açık bir süreçtir. 

Bu proje, bu süreci **dijitalleştirmek ve otomatize etmek** amacıyla geliştirilmiştir. Yazılım, **TCMB (Merkez Bankası)** servislerinden anlık döviz kurlarını çeker, malzeme, işçilik ve fason giderlerini birleştirerek saniyeler içinde **kurumsal teklif formatında PDF** oluşturur.

---

## 🌟 Temel Özellikler

| Özellik | Açıklama |
| :--- | :--- |
| **⚙️ Dinamik Hesaplama** | Malzeme, İşçilik ve Fason giderlerini (Lazer, Kaplama vb.) birleştirerek maliyeti çıkarır. |
| **💲 Canlı Kur Takibi** | TCMB'den anlık **USD** ve **EUR** kurlarını çeker, otomatik çapraz kur hesabı yapar. |
| **📄 PDF Raporlama** | Müşteriye sunulmaya hazır, kaşe/imza alanlı **resmi PDF teklif** oluşturur. |
| **📊 Excel Dökümü** | Detaylı maliyet analizi ve arşivleme için `.xlsx` çıktısı verir. |
| **💾 Akıllı Katalog** | Sık kullanılan ürünleri hafızasında tutar, tekrar yazma zahmetinden kurtarır. |
| **🎨 Modern Arayüz** | Windows 11 uyumlu, **Dark Mode** destekli, kullanıcı dostu arayüz. |

---

## 🛠️ Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda denemek için aşağıdaki adımları izleyebilirsiniz:

### 1. Projeyi İndirin
git clone https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git
cd Manufacturing-Cost-Estimator

### 2. Gerekli Kütüphaneleri Yükleyin
pip install customtkinter pandas requests reportlab openpyxl

### 3. Uygulamayı Başlatın
python maliyet.py

---

## 📂 Proje Yapısı

Manufacturing-Cost-Estimator/
├── maliyet.py          # 🐍 Ana Kaynak Kod (Uygulama)
├── katalog.json        # 🗂️ Ürün Veritabanı (Otomatik oluşur)
├── ayarlar.json        # ⚙️ Kullanıcı Ayarları
├── discount.ico        # 🎨 Uygulama İkonu
└── TEKLİFLER/          # 📂 PDF ve Excel Çıktı Klasörü

---

<div align="center">

  ### 👨‍💻 Geliştirici
  
  **Hasan Mihalıçlı** *Makine Mühendisliği Öğrencisi & Python Geliştirici*

  <a href="https://www.linkedin.com/in/hasanmihalicli/" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin" />
  </a>
  <a href="https://github.com/hasanmihalicli23" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github" />
  </a>

</div>
