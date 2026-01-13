import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
import threading
import re
import json
import os
import locale
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# Türkçe yerel ayarları
try: locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except:
    try: locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except: pass

# --- TEMA AYARLARI ---
THEME = {
    "bg_main": "#F5F7F9",       
    "bg_panel": "#FFFFFF",      
    "bg_header": "#162232",     
    "fg_header": "#FFFFFF",     
    "fg_text": "#455A64",       
    "fg_muted": "#90A4AE",      
    "accent_blue": "#1976D2",
    "accent_yellow": "#FBC02D", 
    "accent_green": "#388E3C",  
    "accent_teal": "#00897B",   
    "accent_pink": "#D81B60",   
    "accent_red": "#D32F2F",    
    "accent_orange": "#F57C00", 
    "accent_purple": "#7B1FA2", 
    "accent_grey": "#546E7A",
    "border_color": "#CFD8DC"   
}

# --- FONT STANDARTLARI ---
FONT_HEADER_TITLE = ("Segoe UI", 10, "bold") 
FONT_LABEL = ("Segoe UI", 9)                 
FONT_ENTRY = ("Segoe UI", 9)                 
FONT_BTN = ("Segoe UI", 9, "bold")           
FONT_RES_TITLE = ("Segoe UI", 9, "bold")     
FONT_RES_LBL = ("Segoe UI", 9)               
FONT_RES_VAL = ("Consolas", 10)              
FONT_TOTAL = ("Consolas", 11, "bold")        

# --- GLOBAL DEĞİŞKENLER ---
# --- GLOBAL DEĞİŞKENLER ---
# --- GLOBAL DEĞİŞKENLER ---
proje_verileri = []
oto_kayit_job = None 
ANA_KAYIT_YOLU = None  # (Bunu önceki adımda eklemiştik)
ACIK_DOSYA_YOLU = None # <-- YENİ: Bunu ekle (Açık olan dosyanın adresini tutacak)

# --- KATALOG ---
varsayilan_katalog = {
    "Motorlar": ["Asenkron Motor 0.18 kW", "Asenkron Motor 0.37 kW", "Asenkron Motor 0.55 kW", "Asenkron Motor 1.5 kW", "Servo Motor 750W"],
    "Redüktörler": ["Sonsuz Vida 30 Gövde", "Sonsuz Vida 50 Gövde", "Helisel Dişli", "Planet Redüktör"],
    "Sürücüler": ["Hız Kontrol 0.37 kW", "Hız Kontrol 0.75 kW", "Hız Kontrol 1.5 kW", "Hız Kontrol 2.2 kW"],
    "Rulmanlar": ["UCFL 204", "UCFL 205", "UCP 204", "6204 ZZ", "Lineer Rulman"],
    "Konveyör Parçaları": ["Denge Ayağı M10", "Denge Ayağı M12", "Modüler Bant Dişlisi", "Rulo Ø50"],
    "Hammadde: Saclar": ["DKP Sac 1mm", "DKP Sac 2mm", "Paslanmaz Sac 1mm", "Galvaniz Sac"],
    "Hammadde: Profiller": ["Kutu Profil 30x30", "Kutu Profil 40x40", "Sigma Profil 30x30", "Sigma Profil 45x45"],
    "Hammadde: Dolu": ["Lama 30x5", "Lama 40x10", "Transmisyon Mili Ø20", "Civa Çeliği Ø20"],
    "Civatalar": ["M6 Civata", "M8 Civata", "M10 Civata", "M8 Somun", "M10 Pul"],
    "Pnömatik": ["Piston Ø32", "Piston Ø50", "Valf 5/2", "Rekorlar", "Hortum"],
    "Diğer / Özel Giriş": ["Diğer (Manuel Giriş)"]
}
DOSYA_ADI = "katalog.json"

# --- YARDIMCI FONKSİYONLAR ---
def format_para(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def format_kur_goster(usd_tutar, kur_usd, kur_eur):
    tl_karsilik = usd_tutar * kur_usd
    eur_karsilik = (usd_tutar * kur_usd) / kur_eur if kur_eur > 0 else 0
    return f"USD: {format_para(usd_tutar):>10}\nEUR: {format_para(eur_karsilik):>10}\n TL: {format_para(tl_karsilik):>10}"

def katalog_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as f: return json.load(f)
        except: return varsayilan_katalog
    else: katalog_kaydet(varsayilan_katalog); return varsayilan_katalog
def katalog_kaydet(veri):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=4)
katalog = katalog_yukle()

def tcmb_kur_getir():
    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        res = requests.get(url)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            for currency in root.findall('Currency'):
                kod = currency.get('Kod')
                if kod == 'USD': entry_kur_usd.delete(0, 'end'); entry_kur_usd.insert(0, currency.find('ForexSelling').text)
                elif kod == 'EUR': entry_kur_eur.delete(0, 'end'); entry_kur_eur.insert(0, currency.find('ForexSelling').text)
            lbl_durum.config(text="✔", fg="#66BB6A") 
        else: lbl_durum.config(text="✘", fg="#EF5350") 
    except: lbl_durum.config(text="✘", fg="#EF5350")
def baslat_kur_thread(): threading.Thread(target=tcmb_kur_getir).start()

# --- KLASÖR VE DOSYA YÖNETİMİ ---
def temizle_dosya_adi(isim):
    return re.sub(r'[\\/*?:<>|]', '_', str(isim).strip())

def klasor_hazirla():
    global ANA_KAYIT_YOLU
    
    proje = entry_proje_adi.get()
    musteri = entry_musteri.get()
    if not proje or not musteri: return None, None 

    proje_clean = temizle_dosya_adi(proje)
    musteri_clean = temizle_dosya_adi(musteri)

    # Eğer henüz bir ana klasör seçilmediyse soralım
    if ANA_KAYIT_YOLU is None:
        messagebox.showinfo("Konum Seçimi", "Lütfen projelerin kaydedileceği ANA KLASÖRÜ seçiniz.")
        secilen_yol = filedialog.askdirectory(title="Projelerin Kaydedileceği Ana Klasörü Seç")
        
        if secilen_yol:
            ANA_KAYIT_YOLU = secilen_yol
        else:
            return None, None # Seçim iptal edildiyse işlem yapma

    # Seçilen klasörün içine "Müşteri - Proje" klasörü aç
    hedef_klasor = os.path.join(ANA_KAYIT_YOLU, f"{musteri_clean} - {proje_clean}")
    
    try:
        os.makedirs(hedef_klasor, exist_ok=True)
        return hedef_klasor, proje_clean
    except: return None, None

def proje_verilerini_topla():
    return {
        "metadata": {
            "proje_adi": entry_proje_adi.get(),
            "musteri": entry_musteri.get(),
            "kur_usd": entry_kur_usd.get(),
            "kur_eur": entry_kur_eur.get(),
            "kar_malzeme": entry_kar_malzeme.get(),
            "kar_iscilik": entry_kar_iscilik.get(),
            "kdv": entry_kdv.get()
        },
        "items": proje_verileri
    }

def projeyi_kaydet(sessiz=False):
    global ACIK_DOSYA_YOLU, ANA_KAYIT_YOLU
    
    # 1. Klasör ve İsim Hesapla
    klasor_yolu, dosya_adi = klasor_hazirla()
    if not klasor_yolu: 
        if not sessiz: messagebox.showwarning("Eksik Bilgi", "Proje Adı ve Müşteri giriniz.")
        return False
    
    yeni_tam_yol = os.path.join(klasor_yolu, f"{dosya_adi}.json")
    veri = proje_verilerini_topla()
    
    try:
        # --- AKILLI KAYIT MANTIĞI ---
        # Eğer zaten açık bir dosya varsa ve yolu yeni hesaplanan yolla aynıysa direkt üstüne yaz
        if ACIK_DOSYA_YOLU and os.path.exists(ACIK_DOSYA_YOLU):
            if ACIK_DOSYA_YOLU == yeni_tam_yol:
                # Yol aynı, direkt üzerine yaz (Sorun yok)
                pass
            else:
                # Yol farklı! Demek ki kullanıcı Proje Adını veya Müşteriyi değiştirdi.
                # Eski dosyayı silip, yeni isimle mi kaydedelim? Yoksa kopya mı oluşturalım?
                # Kullanıcı "yeni dosya oluşmasın" dediği için ESKİSİNİ SİLİP YENİSİNİ YAZACAĞIZ.
                
                cevap = messagebox.askyesno("İsim Değişikliği", 
                                            f"Proje adı değişmiş görünüyor.\n\n"
                                            f"Eski Dosya: {os.path.basename(ACIK_DOSYA_YOLU)}\n"
                                            f"Yeni Dosya: {dosya_adi}.json\n\n"
                                            f"Eski dosyayı silip ismini değiştirerek mi kaydedilsin?\n"
                                            f"(Hayır derseniz eski dosya kalır, yeni bir kopya oluşur.)")
                
                if cevap: # Evet derse eskisini sil
                    try: os.remove(ACIK_DOSYA_YOLU)
                    except: pass
        
        # Dosyayı Kaydet
        with open(yeni_tam_yol, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)
            
        # Kaydettikten sonra açık dosya yolunu güncelle
        ACIK_DOSYA_YOLU = yeni_tam_yol 
        
        if not sessiz: messagebox.showinfo("Kaydedildi", f"Proje kaydedildi:\n{dosya_adi}")
        return True
    except Exception as e:
        if not sessiz: messagebox.showerror("Hata", f"Kaydedilemedi: {e}")
        return False

def projeyi_yukle():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    initial_dir = os.path.join(base_dir, "TEKLIFLER")
    if not os.path.exists(initial_dir): initial_dir = base_dir

    dosya_yolu = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Elif Proje Dosyası", "*.json")])
    if not dosya_yolu: return

    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f: veri = json.load(f)
        
        meta = veri.get("metadata", {})
        entry_proje_adi.delete(0, 'end'); entry_proje_adi.insert(0, meta.get("proje_adi", ""))
        entry_musteri.delete(0, 'end'); entry_musteri.insert(0, meta.get("musteri", ""))
        entry_kur_usd.delete(0, 'end'); entry_kur_usd.insert(0, meta.get("kur_usd", "35.50"))
        entry_kur_eur.delete(0, 'end'); entry_kur_eur.insert(0, meta.get("kur_eur", "38.20"))
        
        entry_kar_malzeme.delete(0, 'end'); entry_kar_malzeme.insert(0, meta.get("kar_malzeme", "30"))
        entry_kar_iscilik.delete(0, 'end'); entry_kar_iscilik.insert(0, meta.get("kar_iscilik", "60"))
        entry_kdv.delete(0, 'end'); entry_kdv.insert(0, meta.get("kdv", "20"))

        global proje_verileri
        proje_verileri = veri.get("items", [])
        tabloyu_guncelle()
        hesapla()
        messagebox.showinfo("Yüklendi", "Proje verileri geri yüklendi.")
    except Exception as e: messagebox.showerror("Hata", f"Dosya yüklenemedi: {e}")

# --- YENİ EKLENTİ: GEÇMİŞ PENCERESİ FONKSİYONLARI ---
def gecmisi_goster():
    """Tüm kayıtlı projeleri listeleyen bir pencere açar."""
    global ANA_KAYIT_YOLU
    
    # Eğer henüz klasör seçilmediyse sor
    if ANA_KAYIT_YOLU is None:
        secilen_yol = filedialog.askdirectory(title="Projelerin Bulunduğu Klasörü Göster")
        if secilen_yol:
            ANA_KAYIT_YOLU = secilen_yol
        else:
            return # Seçmezse açma

    # Popup Pencere
    top = tk.Toplevel(app)
    top.title("Teklif Geçmişi")
    top.geometry("600x400")
    top.configure(bg=THEME["bg_main"])

    tk.Label(top, text=f"Konum: {ANA_KAYIT_YOLU}", font=("Segoe UI", 8), bg=THEME["bg_main"], fg="grey").pack(pady=2)
    tk.Label(top, text="Kayıtlı Projeler (Çift Tıklayarak Aç)", font=FONT_HEADER_TITLE, bg=THEME["bg_main"]).pack(pady=5)

    # Liste Kutusu ve Scrollbar
    frame_list = tk.Frame(top)
    frame_list.pack(fill="both", expand=True, padx=10, pady=5)
    
    scrollbar = ttk.Scrollbar(frame_list)
    scrollbar.pack(side="right", fill="y")
    
    listbox = tk.Listbox(frame_list, font=FONT_LABEL, yscrollcommand=scrollbar.set, height=15)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    # Dosyaları Bul ve Listele
    bulunan_dosyalar = [] 
    
    for root, dirs, files in os.walk(ANA_KAYIT_YOLU):
        for file in files:
            if file.endswith(".json") and file != "katalog.json": # Katalog dosyasını listeleme
                full_path = os.path.join(root, file)
                # Klasör ismini göster ki hangi müşteri olduğu anlaşılsın
                parent_folder = os.path.basename(root)
                display_name = f"{parent_folder}  >>>  {file}"
                listbox.insert("end", display_name)
                bulunan_dosyalar.append(full_path)

    def secileni_yukle(event):
        secim_index = listbox.curselection()
        if not secim_index: return
        dosya_yolu = bulunan_dosyalar[secim_index[0]]
        yukle_from_path(dosya_yolu)
        top.destroy() 

    listbox.bind("<Double-Button-1>", secileni_yukle)

def yukle_from_path(dosya_yolu):
    """Verilen dosya yolundan projeyi yükler (Helper)."""
    global ACIK_DOSYA_YOLU  # <-- BU ÇOK ÖNEMLİ (Hafızaya almak için)
    
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f: veri = json.load(f)
        
        meta = veri.get("metadata", {})
        entry_proje_adi.delete(0, 'end'); entry_proje_adi.insert(0, meta.get("proje_adi", ""))
        entry_musteri.delete(0, 'end'); entry_musteri.insert(0, meta.get("musteri", ""))
        entry_kur_usd.delete(0, 'end'); entry_kur_usd.insert(0, meta.get("kur_usd", "35.50"))
        entry_kur_eur.delete(0, 'end'); entry_kur_eur.insert(0, meta.get("kur_eur", "38.20"))
        
        entry_kar_malzeme.delete(0, 'end'); entry_kar_malzeme.insert(0, meta.get("kar_malzeme", "30"))
        entry_kar_iscilik.delete(0, 'end'); entry_kar_iscilik.insert(0, meta.get("kar_iscilik", "60"))
        entry_kdv.delete(0, 'end'); entry_kdv.insert(0, meta.get("kdv", "20"))

        global proje_verileri
        proje_verileri = veri.get("items", [])
        
        # --- HAFIZAYA ALMA KISMI ---
        ACIK_DOSYA_YOLU = dosya_yolu  # Dosyanın nerede olduğunu kaydettik
        # ---------------------------

        tabloyu_guncelle()
        hesapla()
        messagebox.showinfo("Yüklendi", "Proje başarıyla yüklendi.")
    except Exception as e: messagebox.showerror("Hata", f"Yüklenemedi: {e}")

def excele_aktar():
    if not proje_verileri: messagebox.showwarning("Uyarı", "Liste boş."); return
    klasor_yolu, dosya_adi = klasor_hazirla()
    if not klasor_yolu: return
    
    tam_yol = os.path.join(klasor_yolu, f"{dosya_adi}.xlsx")
    excel_data = []
    for veri in proje_verileri:
        tutar_tl = veri["tutar"] if veri["para"] == "TL" else 0
        tutar_usd = veri["tutar"] if veri["para"] == "USD" else 0
        tutar_eur = veri["tutar"] if veri["para"] == "EUR" else 0
        excel_data.append([veri["tip"], veri["kategori"], veri["urun"], veri["miktar"], veri["birim"], veri["birim_fiyat"], veri["para"], tutar_tl, tutar_usd, tutar_eur])

    df = pd.DataFrame(excel_data, columns=["Tip", "Kategori", "Ürün", "Miktar", "Birim", "Birim Fiyat", "Para", "Tutar (TL)", "Tutar (USD)", "Tutar (EUR)"])
    hesapla()
    try:
        with pd.ExcelWriter(tam_yol, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detaylar', index=False)
            ozet_data = {
                'Kalem': ['Proje Adı', 'Müşteri Firma', 'Tarih', 'USD Kuru', 'EUR Kuru', '---', 'Toplam Ham Maliyet ($)', 'Toplam Teklif Fiyatı ($)', 'KDV Dahil Genel Toplam ($)'],
                'Değer': [entry_proje_adi.get(), entry_musteri.get(), datetime.now().strftime('%d.%m.%Y'), entry_kur_usd.get(), entry_kur_eur.get(), '',
                          lbl_ham_toplam_val.cget("text").split('\n')[0], lbl_satis_toplam_val.cget("text").split('\n')[0], lbl_tl_kdvli_val.cget("text").split('\n')[0]]
            }
            pd.DataFrame(ozet_data).to_excel(writer, sheet_name='Teklif Özeti', index=False)
        
        if messagebox.askyesno("Excel Hazır", f"Dosya oluşturuldu:\n{tam_yol}\n\nKlasörü açmak ister misiniz?"): dosya_konumunu_ac()
    except Exception as e: messagebox.showerror("Hata", str(e))

# --- PDF OLUŞTURMA MOTORU (SADECE USD) ---
def pdf_olustur_ve_ac():
    if not proje_verileri:
        messagebox.showwarning("Uyarı", "Liste boş, PDF oluşturulamaz.")
        return

    # 1. Klasör ve Dosya Ayarı
    klasor_yolu, dosya_adi = klasor_hazirla()
    if not klasor_yolu: return
    pdf_dosya_yolu = os.path.join(klasor_yolu, f"{dosya_adi}.pdf")

    try:
        # Kurları Al (Hesaplama için lazım)
        try:
            kur_usd = float(entry_kur_usd.get().replace(',', '.'))
            kur_eur = float(entry_kur_eur.get().replace(',', '.'))
            kdv_orani = float(entry_kdv.get().replace(',', '.'))
        except:
            messagebox.showerror("Hata", "Kur veya KDV değerleri hatalı.")
            return

        # 2. PDF Başlat
        c = canvas.Canvas(pdf_dosya_yolu, pagesize=A4)
        genislik, yukseklik = A4
        
        # Font Ayarları
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
            font_normal = 'Arial'; font_bold = 'Arial-Bold'
        except:
            font_normal = 'Helvetica'; font_bold = 'Helvetica-Bold'

        # --- TASARIM ---
        
        # LOGO
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(script_dir, "Bursa Elif Makina Logo.png")
            c.drawImage(img_path, 30, yukseklik - 100, width=150, height=80, mask='auto', preserveAspectRatio=True)
        except: pass

        # BAŞLIKLAR
        c.setFont(font_bold, 16)
        c.drawRightString(genislik - 30, yukseklik - 50, "MALİYET RAPORU")
        
        c.setFont(font_normal, 10)
        c.drawRightString(genislik - 30, yukseklik - 70, f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
        
        # MÜŞTERİ KUTUSU
        c.setLineWidth(1)
        c.rect(30, yukseklik - 150, genislik - 60, 40)
        
        c.setFont(font_bold, 10)
        c.drawString(40, yukseklik - 125, "FİRMA:")
        c.drawString(40, yukseklik - 140, "PROJE:")
        
        c.setFont(font_normal, 10)
        c.drawString(100, yukseklik - 125, entry_musteri.get())
        c.drawString(100, yukseklik - 140, entry_proje_adi.get())

        # --- TABLO BAŞLIKLARI ---
        y = yukseklik - 180
        satir_h = 20
        
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(30, y, genislik - 60, satir_h, fill=1)
        c.setFillColorRGB(0, 0, 0)

        c.setFont(font_bold, 9)
        c.drawString(35, y + 6, "KATEGORİ")
        c.drawString(150, y + 6, "ÜRÜN / AÇIKLAMA")
        c.drawString(350, y + 6, "MİKTAR")
        c.drawString(420, y + 6, "BİRİM FİYAT ($)") # Başlık değişti
        c.drawString(500, y + 6, "TUTAR ($)")       # Başlık değişti

        y -= satir_h

        # --- TABLO İÇERİĞİ VE HESAPLAMA ---
        c.setFont(font_normal, 9)
        toplam_teklif_usd = 0 # Toplamı burada biriktireceğiz

        for veri in proje_verileri:
            if y < 100: # Sayfa sonu
                c.showPage(); y = yukseklik - 50; c.setFont(font_normal, 9)

            # HER ŞEYİ USD'YE ÇEVİRME MANTIĞI
            orj_fiyat = veri['birim_fiyat']
            para = veri['para']
            
            # Birim fiyatı USD'ye çevir
            if para == "TL": birim_fiyat_usd = orj_fiyat / kur_usd
            elif para == "EUR": birim_fiyat_usd = (orj_fiyat * kur_eur) / kur_usd
            else: birim_fiyat_usd = orj_fiyat
            
            # Satır tutarını hesapla
            satir_tutar_usd = birim_fiyat_usd * veri['miktar']
            toplam_teklif_usd += satir_tutar_usd

            # Ekrana Yazdır
            urun_adi = veri["urun"][:35] + "..." if len(veri["urun"]) > 35 else veri["urun"]
            
            c.drawString(35, y + 6, veri["kategori"])
            c.drawString(150, y + 6, urun_adi)
            c.drawString(350, y + 6, f"{veri['miktar']:g} {veri['birim']}")
            # Formatlarken format_para kullanıyoruz
            c.drawString(420, y + 6, f"${format_para(birim_fiyat_usd)}") 
            c.drawString(500, y + 6, f"${format_para(satir_tutar_usd)}")
            
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.line(30, y, genislik - 30, y)
            c.setStrokeColorRGB(0, 0, 0)
            y -= satir_h

        # --- TOPLAMLAR (HİZALI VE EŞİT PUNTO) ---
        # KDV Hesabı
        kdv_tutari = toplam_teklif_usd * (kdv_orani / 100)
        genel_toplam = toplam_teklif_usd + kdv_tutari

        y -= 30 # Tablodan biraz daha aşağı inelim
        
        # 1. Ortak Font ve Boyut Ayarı (İkisi de Bold ve 10 Punto)
        c.setFont(font_bold, 10)
        
        # 2. Sabit Sütun Başlangıç Noktaları (X Koordinatları)
        # Bu değerlerle oynayarak sağa/sola kaydırabilirsin
        x_etiket = genislik - 280  # "Ara Toplam..." yazısının başladığı yer
        x_para   = genislik - 100  # "$13.000..." parasının başladığı yer

        # 3. Ara Toplam Satırı
        c.drawString(x_etiket, y, "ARA TOPLAM (KDV HARİÇ):")
        c.drawString(x_para,   y, f"${format_para(toplam_teklif_usd)}")
        
        # 4. Genel Toplam Satırı
        y -= 15 # Alt satıra geçiş boşluğu
        c.drawString(x_etiket, y, "GENEL TOPLAM (KDV DAHİL):")
        c.drawString(x_para,   y, f"${format_para(genel_toplam)}")

        # --- ALT BİLGİ ---
        y -= 60
        c.setFont(font_normal, 8)
        c.drawString(30, y, "* Fiyatlarımıza KDV dahildir (Yukarıda belirtilmiştir).")
        c.drawString(30, y - 10, "* Ödeme günü döviz kuru (TCMB Efektif Satış) geçerlidir.")
        
        c.setFont(font_bold, 10)
        c.drawString(genislik - 150, y, "BURSA ELİF MAKİNA")
        c.drawString(genislik - 150, y - 15, "Kaşe / İmza")

        c.save()
        os.startfile(pdf_dosya_yolu)

    except Exception as e:
        messagebox.showerror("Hata", f"PDF Oluşturulamadı:\n{e}")

def dosya_konumunu_ac():
    klasor_yolu, _ = klasor_hazirla()
    if klasor_yolu and os.path.exists(klasor_yolu): os.startfile(klasor_yolu)

# --- YENİ OTO KAYIT MANTIĞI ---
def oto_kayit_dongusu(interval_ms):
    """Seçilen süreye göre sürekli kayıt yapar."""
    global oto_kayit_job
    # Eğer "Kapalı" seçildiyse döngüyü kır
    if cmb_oto_kayit.get() == "Kapalı":
        return

    # Kayıt işlemini dene (Sessiz modda)
    if entry_proje_adi.get() and entry_musteri.get():
        projeyi_kaydet(sessiz=True)
        # Konsola zaman damgası bas (Test için, kullanıcı görmez)
        print(f"Otomatik Kayıt Yapıldı: {datetime.now().strftime('%H:%M:%S')}")
    
    # Bir sonraki kaydı planla
    oto_kayit_job = app.after(interval_ms, lambda: oto_kayit_dongusu(interval_ms))

def oto_kayit_ayar_degisti(event=None):
    """Combobox değiştiğinde çalışır."""
    global oto_kayit_job
    
    # Mevcut sayacı iptal et (Varsa)
    if oto_kayit_job:
        app.after_cancel(oto_kayit_job)
        oto_kayit_job = None
    
    secim = cmb_oto_kayit.get()
    
    if secim == "Kapalı":
        print("Otomatik Kayıt Durduruldu.")
        return

    # Süreye çevir (Milisaniye)
    ms = 30000 # Varsayılan
    if secim == "30 Saniye": ms = 30000
    elif secim == "1 Dakika": ms = 60000
    elif secim == "2 Dakika": ms = 120000
    elif secim == "5 Dakika": ms = 300000
    
    # Yeni döngüyü başlat
    print(f"Otomatik Kayıt Başladı: {secim}")
    oto_kayit_dongusu(ms)

# --- İŞLEMLER ---
def kategori_degisti(event):
    secilen = cmb_kategori.get()
    cmb_urun['values'] = katalog.get(secilen, [])
    if katalog.get(secilen): cmb_urun.current(0)
    else: cmb_urun.set("")
    manuel_mod_kontrol()

def manuel_mod_kontrol():
    if var_manuel.get() == 1: cmb_urun.config(state="normal"); cmb_urun.set(""); cmb_urun.focus_set()
    else: 
        cmb_urun.config(state="readonly")
        secilen = cmb_kategori.get()
        if katalog.get(secilen) and cmb_urun.get() not in katalog.get(secilen): cmb_urun.current(0)

def veri_ekle(tip, kategori, urun, miktar, birim, birim_fiyat, para_birimi):
    try:
        tutar = float(miktar) * float(birim_fiyat)
        yeni_kayit = {"id": len(proje_verileri) + 1, "tip": tip, "kategori": kategori, "urun": urun,
                      "miktar": float(miktar), "birim": birim, "birim_fiyat": float(birim_fiyat),
                      "para": para_birimi, "tutar": tutar}
        proje_verileri.append(yeni_kayit)
        tabloyu_guncelle()
    except ValueError: messagebox.showerror("Hata", "Sayısal değer hatası.")

def tabloyu_guncelle():
    for i in tablo.get_children(): tablo.delete(i)
    filtre = cmb_filtre.get() 
    for veri in proje_verileri:
        goster = False
        if filtre == "Tümü": goster = True
        elif filtre == "Sadece Malzeme" and veri["tip"] == "MALZEME": goster = True
        elif filtre == "Sadece İşçilik" and veri["tip"] == "ISCILIK": goster = True
        elif filtre == "Sadece Dış Hizmet" and veri["tip"] == "FASON": goster = True
        
        if goster:
            tablo.insert("", "end", values=(veri["kategori"], veri["urun"], f"{veri['miktar']:g} {veri['birim']}",
                                            format_para(veri["birim_fiyat"]), veri["para"], format_para(veri["tutar"]),
                                            veri["tutar"], veri["birim_fiyat"]))

def malzeme_ekle():
    if not entry_fiyat.get(): return
    secilen_kat = cmb_kategori.get(); girilen_urun = cmb_urun.get()
    miktar = entry_adet.get().replace(',', '.'); fiyat = entry_fiyat.get().replace(',', '.')
    veri_ekle("MALZEME", secilen_kat, girilen_urun, miktar, cmb_birim.get(), fiyat, cmb_para.get())
    if secilen_kat in katalog and girilen_urun not in katalog[secilen_kat]:
        katalog[secilen_kat].append(girilen_urun); katalog_kaydet(katalog); cmb_urun['values'] = katalog[secilen_kat]
    entry_adet.delete(0, 'end'); entry_adet.insert(0, "1"); entry_fiyat.delete(0, 'end')

def iscelik_ekle():
    try:
        kisi = entry_isci_kisi.get().replace(',', '.'); saat = entry_isci_saat.get().replace(',', '.')
        ucret = entry_isci_ucret.get().replace(',', '.'); toplam_saat = float(kisi) * float(saat)
        veri_ekle("ISCILIK", "İŞÇİLİK GİDERİ", f"{int(float(kisi))} Kişi Çalışması", toplam_saat, "Saat", ucret, cmb_isci_para.get())
    except: messagebox.showerror("Hata", "İşçilik değerlerini kontrol edin.")

def otomasyon_ekle():
    try:
        fiyat = entry_oto_fiyat.get().replace(',', '.'); tur = cmb_oto_tur.get(); aciklama = entry_oto_aciklama.get()
        urun_adi = f"{tur} - {aciklama}" if aciklama else tur
        veri_ekle("FASON", "DIŞ HİZMET / FASON", urun_adi, 1, "Hizmet", fiyat, cmb_oto_para.get())
        entry_oto_fiyat.delete(0, 'end'); entry_oto_aciklama.delete(0, 'end')
    except: messagebox.showerror("Hata", "Fiyat giriniz.")

def sil():
    secili = tablo.selection()
    if not secili: return
    if messagebox.askyesno("Sil", "Seçili satırlar silinsin mi?"):
        silinecek_indexler = []
        for s in secili:
            vals = tablo.item(s)['values']
            for i, veri in enumerate(proje_verileri):
                if veri["urun"] == vals[1] and format_para(veri["tutar"]) == vals[5]:
                    silinecek_indexler.append(i); break
        for i in sorted(silinecek_indexler, reverse=True): del proje_verileri[i]
        tabloyu_guncelle()

def sifirla():
    if messagebox.askyesno("Sıfırla", "Tüm liste ve proje bilgileri silinecek?"):
        proje_verileri.clear(); tabloyu_guncelle()
        entry_proje_adi.delete(0, 'end'); entry_musteri.delete(0, 'end')
        for lbl in [lbl_ham_malzeme_val, lbl_ham_iscilik_val, lbl_ham_toplam_val, lbl_satis_malzeme_val, lbl_satis_iscilik_val, lbl_satis_toplam_val, lbl_tl_teklif_val, lbl_tl_kdvli_val]:
            lbl.config(text="...")

def hesapla():
    try:
        kur_usd = float(entry_kur_usd.get().replace(',', '.')); kur_eur = float(entry_kur_eur.get().replace(',', '.'))
        marj_malzeme = float(entry_kar_malzeme.get().replace(',', '.')); marj_iscilik = float(entry_kar_iscilik.get().replace(',', '.'))
        kdv_orani = float(entry_kdv.get().replace(',', '.'))

        ham_malzeme_usd = 0; ham_iscilik_usd = 0; satis_malzeme_usd = 0; satis_iscilik_usd = 0
        for veri in proje_verileri:
            tutar_usd = veri["tutar"]
            if veri["para"] == "TL": tutar_usd /= kur_usd
            elif veri["para"] == "EUR": tutar_usd = (veri["tutar"] * kur_eur) / kur_usd
            
            if veri["tip"] == "ISCILIK":
                ham_iscilik_usd += tutar_usd; satis_iscilik_usd += tutar_usd * (1 + (marj_iscilik / 100))
            else:
                ham_malzeme_usd += tutar_usd; satis_malzeme_usd += tutar_usd * (1 + (marj_malzeme / 100))

        ham_toplam_usd = ham_malzeme_usd + ham_iscilik_usd
        satis_toplam_usd = satis_malzeme_usd + satis_iscilik_usd
        teklif_usd = satis_toplam_usd; kdvli_usd = teklif_usd * (1 + kdv_orani/100)
        
        lbl_ham_malzeme_val.config(text=format_kur_goster(ham_malzeme_usd, kur_usd, kur_eur))
        lbl_ham_iscilik_val.config(text=format_kur_goster(ham_iscilik_usd, kur_usd, kur_eur))
        lbl_ham_toplam_val.config(text=format_kur_goster(ham_toplam_usd, kur_usd, kur_eur))
        lbl_satis_malzeme_val.config(text=format_kur_goster(satis_malzeme_usd, kur_usd, kur_eur))
        lbl_satis_iscilik_val.config(text=format_kur_goster(satis_iscilik_usd, kur_usd, kur_eur))
        lbl_satis_toplam_val.config(text=format_kur_goster(satis_toplam_usd, kur_usd, kur_eur))
        lbl_tl_teklif_val.config(text=format_kur_goster(teklif_usd, kur_usd, kur_eur))
        lbl_tl_kdvli_val.config(text=format_kur_goster(kdvli_usd, kur_usd, kur_eur))
    except ValueError: messagebox.showerror("Hata", "Oranları ve kurları kontrol edin.")

def sirala(col, reverse):
    l = []
    for k in tablo.get_children(''):
        val = tablo.set(k, col)
        if col == "Tutar": val = float(tablo.set(k, "ham_tutar"))
        elif col == "Birim Fiyat": val = float(tablo.set(k, "gizli_birim_fiyat"))
        elif col == "Miktar": 
            try: val = float(val.split()[0])
            except: val = 0
        l.append((val, k))
    l.sort(reverse=reverse, key=lambda x: x[0])
    for index, (val, k) in enumerate(l): tablo.move(k, '', index)
    tablo.heading(col, command=lambda: sirala(col, not reverse))

def listeden_sil_buton():
    secilen_kat = cmb_kategori.get(); secilen_urun = cmb_urun.get()
    if secilen_kat in katalog and secilen_urun in katalog[secilen_kat]:
        if messagebox.askyesno("Sil", f"'{secilen_urun}' veritabanından silinsin mi?"):
            katalog[secilen_kat].remove(secilen_urun); katalog_kaydet(katalog); cmb_urun['values'] = katalog[secilen_kat]; cmb_urun.set("")

#ARAYÜZ ----------------------------------------

app = tk.Tk()
app.title("Bursa Elif Makina - Teklif Hazırlama")
app.geometry("1350x950")
app.configure(bg=THEME["bg_main"])

style = ttk.Style(); style.theme_use('clam')
style.configure(".", background=THEME["bg_main"], foreground=THEME["fg_text"], font=FONT_LABEL)
style.configure("Treeview", font=FONT_LABEL, rowheight=28)
style.configure("Treeview.Heading", font=FONT_BTN, background=THEME["bg_main"])
style.configure("TCombobox", padding=5)

def create_label(parent, text, font=FONT_LABEL, fg=THEME["fg_text"], bg=THEME["bg_panel"]):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg)
def create_entry(parent, width, justify="left"):
    return tk.Entry(parent, width=width, justify=justify, bg="white", fg="black", font=FONT_ENTRY, relief="solid", bd=1)
def create_button(parent, text, command, bg, width=None):
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg="white", font=FONT_BTN, relief="flat", padx=10, pady=5, cursor="hand2")
    if width: btn.config(width=width)
    return btn

frame_head = tk.Frame(app, bg=THEME["bg_header"], pady=15, padx=20)
frame_head.pack(fill="x")

f_left = tk.Frame(frame_head, bg=THEME["bg_header"])
f_left.pack(side="left")

create_label(f_left, "PROJE ADI:", FONT_BTN, THEME["fg_header"], THEME["bg_header"]).pack(side="left")
entry_proje_adi = create_entry(f_left, width=20) 
entry_proje_adi.pack(side="left", padx=(5, 15)) 
entry_proje_adi.insert(0, "Yeni Proje")

create_label(f_left, "MÜŞTERİ:", FONT_BTN, THEME["fg_header"], THEME["bg_header"]).pack(side="left")
entry_musteri = create_entry(f_left, width=20)
entry_musteri.pack(side="left", padx=5)

f_right = tk.Frame(frame_head, bg=THEME["bg_header"])
f_right.pack(side="right")

lbl_durum = create_label(f_right, "...", ("Segoe UI", 14), "white", THEME["bg_header"])
lbl_durum.pack(side="right", padx=(10, 0)) 

entry_kur_eur = create_entry(f_right, width=7, justify="center")
entry_kur_eur.pack(side="right", padx=2)
entry_kur_eur.insert(0, "38.20")
create_label(f_right, "EUR", FONT_BTN, "#FFC107", THEME["bg_header"]).pack(side="right", padx=(10, 2))

entry_kur_usd = create_entry(f_right, width=7, justify="center")
entry_kur_usd.pack(side="right", padx=2)
entry_kur_usd.insert(0, "35.50")
create_label(f_right, "USD", FONT_BTN, "#4CAF50", THEME["bg_header"]).pack(side="right", padx=(5, 2))

f_center = tk.Frame(frame_head, bg=THEME["bg_header"])
f_center.pack(side="left", expand=True) 

create_label(f_center, "Otomatik Kayıt:", FONT_BTN, "#FFFFFF", THEME["bg_header"]).pack(side="left", padx=5)
cmb_oto_kayit = ttk.Combobox(f_center, values=["Kapalı", "30 Saniye", "1 Dakika", "2 Dakika", "5 Dakika"], state="readonly", width=14)
cmb_oto_kayit.current(0)
cmb_oto_kayit.pack(side="left")
cmb_oto_kayit.bind("<<ComboboxSelected>>", oto_kayit_ayar_degisti)

frame_input = tk.Frame(app, bg=THEME["bg_main"]); frame_input.pack(fill="x", padx=15, pady=10)

def create_input_panel(parent, title):
    f = tk.LabelFrame(parent, text=title, bg=THEME["bg_panel"], fg=THEME["fg_text"], font=FONT_HEADER_TITLE, bd=1, relief="solid", padx=10, pady=10)
    return f

p1 = create_input_panel(frame_input, "1. Malzeme & Hammadde"); p1.pack(side="left", fill="both", expand=True, padx=(0,10))
p1.columnconfigure(1, weight=1)
create_label(p1, "Kategori:").grid(row=0, column=0, sticky="e", pady=5)
cmb_kategori = ttk.Combobox(p1, values=list(katalog.keys()), state="readonly"); cmb_kategori.grid(row=0, column=1, sticky="ew", padx=5); cmb_kategori.current(0); cmb_kategori.bind("<<ComboboxSelected>>", kategori_degisti)
var_manuel = tk.IntVar(); tk.Checkbutton(p1, text="Elle Yaz", variable=var_manuel, command=manuel_mod_kontrol, bg=THEME["bg_panel"]).grid(row=0, column=2, sticky="w")
create_label(p1, "Ürün:").grid(row=1, column=0, sticky="e", pady=5)
cmb_urun = ttk.Combobox(p1); cmb_urun.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)
create_button(p1, "X", listeden_sil_buton, THEME["accent_red"]).grid(row=1, column=3)
create_label(p1, "Miktar/Fiyat:").grid(row=2, column=0, sticky="e", pady=5)
f_p1_sub = tk.Frame(p1, bg=THEME["bg_panel"]); f_p1_sub.grid(row=2, column=1, columnspan=3, sticky="w")
entry_adet = create_entry(f_p1_sub, 6, "center"); entry_adet.pack(side="left", padx=5); entry_adet.insert(0, "1")
cmb_birim = ttk.Combobox(f_p1_sub, values=["Adet", "Kg", "Mt", "Tk", "Lt"], width=5, state="readonly"); cmb_birim.current(0); cmb_birim.pack(side="left")
entry_fiyat = create_entry(f_p1_sub, 9, "right"); entry_fiyat.pack(side="left", padx=(10,5))
cmb_para = ttk.Combobox(f_p1_sub, values=["TL", "USD", "EUR"], width=5, state="readonly"); cmb_para.current(0); cmb_para.pack(side="left")
create_button(p1, "LİSTEYE EKLE (+)", malzeme_ekle, THEME["accent_blue"]).grid(row=3, column=0, columnspan=4, sticky="ew", pady=(10,0))
kategori_degisti(None)

p2 = create_input_panel(frame_input, "2. Dış Hizmet / Fason"); p2.pack(side="left", fill="both", expand=True, padx=(0,10))
p2.columnconfigure(1, weight=1)
create_label(p2, "İşlem:").grid(row=0, column=0, sticky="e", pady=5)
cmb_oto_tur = ttk.Combobox(p2, values=["Lazer Kesim", "Abkant", "Taşlama", "Kaplama", "Otomasyon", "Nakliye"], state="readonly"); cmb_oto_tur.current(0); cmb_oto_tur.grid(row=0, column=1, sticky="ew", padx=5)
create_label(p2, "Açıklama:").grid(row=1, column=0, sticky="e", pady=5)
entry_oto_aciklama = create_entry(p2, 20); entry_oto_aciklama.grid(row=1, column=1, sticky="ew", padx=5)
create_label(p2, "Fiyat:").grid(row=2, column=0, sticky="e", pady=5)
f_p2_sub = tk.Frame(p2, bg=THEME["bg_panel"]); f_p2_sub.grid(row=2, column=1, sticky="w")
entry_oto_fiyat = create_entry(f_p2_sub, 9, "right"); entry_oto_fiyat.pack(side="left", padx=5)
cmb_oto_para = ttk.Combobox(f_p2_sub, values=["TL", "USD", "EUR"], width=5, state="readonly"); cmb_oto_para.current(0); cmb_oto_para.pack(side="left")
create_button(p2, "EKLE (+)", otomasyon_ekle, THEME["accent_blue"]).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10,0))

p3 = create_input_panel(frame_input, "3. Atölye İşçilik"); p3.pack(side="left", fill="both", expand=True)
p3.columnconfigure(1, weight=1)
create_label(p3, "Kişi Sayısı:").grid(row=0, column=0, sticky="e", pady=5)
entry_isci_kisi = create_entry(p3, 6, "center"); entry_isci_kisi.grid(row=0, column=1, sticky="w", padx=5); entry_isci_kisi.insert(0, "1")
create_label(p3, "Saat/Kişi:").grid(row=1, column=0, sticky="e", pady=5)
entry_isci_saat = create_entry(p3, 6, "center"); entry_isci_saat.grid(row=1, column=1, sticky="w", padx=5)
create_label(p3, "Saat Ücreti:").grid(row=2, column=0, sticky="e", pady=5)
f_p3_sub = tk.Frame(p3, bg=THEME["bg_panel"]); f_p3_sub.grid(row=2, column=1, sticky="w")
entry_isci_ucret = create_entry(f_p3_sub, 9, "right"); entry_isci_ucret.pack(side="left", padx=5); entry_isci_ucret.insert(0, "1100")
cmb_isci_para = ttk.Combobox(f_p3_sub, values=["TL", "USD", "EUR"], width=5, state="readonly"); cmb_isci_para.current(0); cmb_isci_para.pack(side="left")
create_button(p3, "EKLE (+)", iscelik_ekle, THEME["accent_blue"]).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10,0))

f_ctrl = tk.Frame(app, bg=THEME["bg_main"], pady=10, padx=20)
f_ctrl.pack(fill="x")

f_left = tk.Frame(f_ctrl, bg=THEME["bg_main"])
f_left.pack(side="left")

create_label(f_left, "Filtre:", FONT_BTN, bg=THEME["bg_main"]).pack(side="left")
cmb_filtre = ttk.Combobox(f_left, values=["Tümü", "Sadece Malzeme", "Sadece İşçilik", "Sadece Dış Hizmet"], state="readonly", width=15)
cmb_filtre.current(0); cmb_filtre.pack(side="left", padx=5)
cmb_filtre.bind("<<ComboboxSelected>>", lambda e: tabloyu_guncelle())

f_buttons = tk.Frame(f_ctrl, bg=THEME["bg_main"])
f_buttons.pack(side="right")

BTN_GENISLIK = 14   
BTN_BOSLUK   = 5    

create_button(f_buttons, "Klasörü Aç", dosya_konumunu_ac, THEME["accent_grey"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)
create_button(f_buttons, "Projeyi Yükle", projeyi_yukle, THEME["accent_purple"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)
create_button(f_buttons, "Teklif Geçmişi", gecmisi_goster, THEME["accent_blue"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)
create_button(f_buttons, "Projeyi Kaydet", lambda: projeyi_kaydet(False), THEME["accent_yellow"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)
create_button(f_buttons, "PDF Oluştur", pdf_olustur_ve_ac, THEME["accent_pink"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)
create_button(f_buttons, "Excel Oluştur", excele_aktar, THEME["accent_green"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)
create_button(f_buttons, "Sıfırla", sifirla, THEME["accent_red"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)
create_button(f_buttons, "Sil", sil, THEME["accent_orange"], width=BTN_GENISLIK).pack(side="right", padx=BTN_BOSLUK)

f_list = tk.Frame(app, bg=THEME["bg_main"]); f_list.pack(fill="both", expand=True, padx=15, pady=(0,10))
scroll = ttk.Scrollbar(f_list); scroll.pack(side="right", fill="y")
cols = ("k", "u", "m", "f", "p", "t", "ht", "gbf") 
tablo = ttk.Treeview(f_list, columns=cols, show="headings", selectmode="extended", yscrollcommand=scroll.set)
tablo.pack(side="left", fill="both", expand=True); scroll.config(command=tablo.yview)
headers = ["Kategori", "Ürün / Açıklama", "Miktar", "Birim Fiyat", "Para", "Toplam Tutar", "", ""]
widths = [150, 350, 100, 100, 70, 120, 0, 0]
for col, t, w in zip(cols, headers, widths):
    tablo.heading(col, text=t, command=lambda c=col: sirala(c, False))
    tablo.column(col, width=w, anchor="w" if col in ["k","u"] else "center")
tablo.column("ht", width=0, stretch=False); tablo.column("gbf", width=0, stretch=False)

f_foot = tk.Frame(app, bg=THEME["bg_panel"], padx=15, pady=10); f_foot.pack(fill="x", side="bottom")

p_calc = tk.LabelFrame(f_foot, text="Hesaplama", bg=THEME["bg_panel"], font=FONT_HEADER_TITLE, padx=10, pady=5)
p_calc.pack(side="left", fill="y", padx=(0,15))
p_calc.columnconfigure(1, weight=1)

create_label(p_calc, "Malzeme %:").grid(row=0, column=0, sticky="e")
entry_kar_malzeme = create_entry(p_calc, 5, "center"); entry_kar_malzeme.grid(row=0, column=1, pady=2); entry_kar_malzeme.insert(0, "30")
create_label(p_calc, "İşçilik %:").grid(row=1, column=0, sticky="e")
entry_kar_iscilik = create_entry(p_calc, 5, "center"); entry_kar_iscilik.grid(row=1, column=1, pady=2); entry_kar_iscilik.insert(0, "60")
create_label(p_calc, "KDV %:", fg=THEME["accent_orange"]).grid(row=2, column=0, sticky="e")
entry_kdv = create_entry(p_calc, 5, "center"); entry_kdv.grid(row=2, column=1, pady=2); entry_kdv.insert(0, "20")
create_button(p_calc, "HESAPLA", hesapla, THEME["accent_orange"], width=12).grid(row=3, column=0, columnspan=2, pady=(5,0))

f_res = tk.Frame(f_foot, bg=THEME["bg_panel"]); f_res.pack(side="right", fill="both", expand=True)
def create_res_card(parent, title, bg):
    c = tk.Frame(parent, bg=bg, padx=10, pady=10, bd=1, relief="solid")
    tk.Label(c, text=title, font=FONT_RES_TITLE, bg=bg).pack(anchor="w", pady=(0,5))
    return c

c1 = create_res_card(f_res, "1. Ham Maliyet", "#E8F5E9"); c1.pack(side="left", fill="both", expand=True, padx=(0,10))
create_label(c1, "Malzeme:", FONT_RES_LBL, bg="#E8F5E9").pack(anchor="w"); lbl_ham_malzeme_val = create_label(c1, "...", FONT_RES_VAL, bg="#E8F5E9"); lbl_ham_malzeme_val.pack(anchor="e")
create_label(c1, "İşçilik:", FONT_RES_LBL, bg="#E8F5E9").pack(anchor="w"); lbl_ham_iscilik_val = create_label(c1, "...", FONT_RES_VAL, bg="#E8F5E9"); lbl_ham_iscilik_val.pack(anchor="e")
tk.Frame(c1, height=1, bg="#A5D6A7").pack(fill="x", pady=5)
create_label(c1, "TOPLAM HAM:", FONT_RES_TITLE, THEME["accent_blue"], "#E8F5E9").pack(anchor="w"); lbl_ham_toplam_val = create_label(c1, "...", FONT_RES_VAL, THEME["accent_blue"], "#E8F5E9"); lbl_ham_toplam_val.pack(anchor="e")

c2 = create_res_card(f_res, "2. Teklif Fiyatı", "#E3F2FD"); c2.pack(side="left", fill="both", expand=True, padx=(0,10))
create_label(c2, "Malzeme:", FONT_RES_LBL, bg="#E3F2FD").pack(anchor="w"); lbl_satis_malzeme_val = create_label(c2, "...", FONT_RES_VAL, bg="#E3F2FD"); lbl_satis_malzeme_val.pack(anchor="e")
create_label(c2, "İşçilik:", FONT_RES_LBL, bg="#E3F2FD").pack(anchor="w"); lbl_satis_iscilik_val = create_label(c2, "...", FONT_RES_VAL, bg="#E3F2FD"); lbl_satis_iscilik_val.pack(anchor="e")
tk.Frame(c2, height=1, bg="#90CAF9").pack(fill="x", pady=5)
create_label(c2, "TOPLAM TEKLİF:", FONT_RES_TITLE, THEME["accent_green"], "#E3F2FD").pack(anchor="w"); lbl_satis_toplam_val = create_label(c2, "...", FONT_RES_VAL, THEME["accent_green"], "#E3F2FD"); lbl_satis_toplam_val.pack(anchor="e")

c3 = create_res_card(f_res, "3. Müşteri Özeti", "#FFF3E0"); c3.pack(side="left", fill="both", expand=True)
create_label(c3, "Ara Toplam (KDV'siz):", FONT_RES_LBL, bg="#FFF3E0").pack(anchor="w"); lbl_tl_teklif_val = create_label(c3, "...", FONT_RES_VAL, bg="#FFF3E0"); lbl_tl_teklif_val.pack(anchor="e")
tk.Frame(c3, height=2, bg=THEME["accent_orange"]).pack(fill="x", pady=5)
create_label(c3, "KDV DAHİL:", FONT_RES_TITLE, THEME["accent_orange"], "#FFF3E0").pack(anchor="w"); lbl_tl_kdvli_val = create_label(c3, "...", FONT_TOTAL, THEME["accent_orange"], "#FFF3E0"); lbl_tl_kdvli_val.pack(anchor="e")

baslat_kur_thread()
app.mainloop()