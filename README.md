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

Harika bir fikir. İnsanlar genelde en çok bu kısımda takılır, o yüzden burayı **"Adım Adım ve Çok Net"** anlatmak projenin kullanılabilirliğini artırır.

Aşağıdaki bloğu kopyalayıp `README.md` dosyasındaki ilgili **"Kurulum ve Çalıştırma"** başlığının altına yapıştırabilirsin. Hem samimi hem de teknik bir dille yazdım.

---

### 🛠️ Kurulum ve Çalıştırma Rehberi

Projeyi kendi bilgisayarınızda çalıştırmak ve geliştirmek için aşağıdaki adımları sırasıyla uygulayabilirsiniz.

> **Ön Bilgi:** Bu proje **Python** ile geliştirilmiştir. Bilgisayarınızda Python'un yüklü olduğundan emin olun. (Eğer yüklü değilse [python.org](https://www.python.org/) adresinden indirebilirsiniz.)

#### Adım 1: Projeyi Bilgisayarınıza İndirin

Öncelikle terminalinizi (veya CMD) açın ve projeyi klonlamak için şu komutu yapıştırın:

```bash
git clone https://github.com/hasanmihalicli23/Manufacturing-Cost-Estimator.git

```

Ardından proje klasörünün içine girin:

```bash
cd Manufacturing-Cost-Estimator

```

#### Adım 2: Gerekli Kütüphaneleri Yükleyin

Projenin çalışması için bazı modern arayüz ve raporlama kütüphanelerine ihtiyacı var. Bunları tek komutla yükleyebilirsiniz:

```bash
pip install customtkinter pandas requests reportlab openpyxl

```

#### Adım 3: Uygulamayı Başlatın 🚀

Her şey hazır! Şimdi arayüzü başlatmak için aşağıdaki komutu çalıştırın:

```bash
python maliyet.py

```

> **Not:** Uygulama açıldığında TCMB'den güncel kurları çekmek için internet bağlantısına ihtiyaç duyar. Kurlar otomatik güncellendiğinde sağ üstte "Kurlar Güncel ✔" uyarısını göreceksiniz.


<div align="center">

  ### 👨‍💻 Geliştirici
  
  **Hasan Mıhalıçlı**

  <a href="https://www.linkedin.com/in/hasanmihalicli23/" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin" />
  </a>
  <a href="https://github.com/hasanmihalicli23" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github" />
  </a>

</div>
