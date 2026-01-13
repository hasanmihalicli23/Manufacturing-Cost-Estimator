import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET
import threading
import re
import json
import os
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# NOT: locale kütüphanesi kaldırıldı çünkü "bad screen distance" hatasına sebep oluyor.
# Para birimi formatlamasını zaten kendi fonksiyonumuzla (format_para) yapıyoruz.

# --- MODERN AYARLAR ---
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue") 
ctk.set_widget_scaling(1.0)  # Ölçekleme sorunu olmaması için standart boyut (Gerekirse 1.0 yapın)

# --- GLOBAL DEĞİŞKENLER ---
proje_verileri = []
oto_kayit_job = None 
ANA_KAYIT_YOLU = None  
ACIK_DOSYA_YOLU = None 
AYAR_DOSYASI = "ayarlar.json"
DOSYA_ADI = "katalog.json"

# --- KATALOG VERİSİ ---
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

# --- YARDIMCI FONKSİYONLAR ---
def format_para(deger):
    # Sayıyı TR formatına (1.234,56) çeviren manuel fonksiyon
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def format_kur_goster(usd_tutar, kur_usd, kur_eur):
    tl_karsilik = usd_tutar * kur_usd
    eur_karsilik = (usd_tutar * kur_usd) / kur_eur if kur_eur > 0 else 0
    return f"USD: {format_para(usd_tutar):>10}\nEUR: {format_para(eur_karsilik):>10}\n TL: {format_para(tl_karsilik):>10}"

def temizle_dosya_adi(isim):
    return re.sub(r'[\\/*?:<>|]', '_', str(isim).strip())

# --- DOSYA VE AYAR YÖNETİMİ ---
def katalog_kaydet(veri):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

def katalog_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as f: return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Katalog Hatası", "katalog.json dosyası bozuk!\nVarsayılan liste yükleniyor.")
            return varsayilan_katalog
        except Exception:
            return varsayilan_katalog
    else: 
        katalog_kaydet(varsayilan_katalog)
        return varsayilan_katalog

katalog = katalog_yukle()

def ayarlari_yukle():
    global ANA_KAYIT_YOLU
    if os.path.exists(AYAR_DOSYASI):
        try:
            with open(AYAR_DOSYASI, "r", encoding="utf-8") as f:
                ANA_KAYIT_YOLU = json.load(f).get("kayit_yolu")
        except: pass

def ayarlari_kaydet():
    if ANA_KAYIT_YOLU:
        try:
            with open(AYAR_DOSYASI, "w", encoding="utf-8") as f:
                json.dump({"kayit_yolu": ANA_KAYIT_YOLU}, f)
        except: pass

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
            lbl_durum.configure(text="Kurlar Güncel ✔", text_color="#00E676") 
        else: lbl_durum.configure(text="Kur Hatası ✘", text_color="#FF5252") 
    except: lbl_durum.configure(text="Kur Hatası ✘", text_color="#FF5252")

def baslat_kur_thread(): 
    threading.Thread(target=tcmb_kur_getir).start()

def klasor_hazirla():
    global ANA_KAYIT_YOLU
    proje, musteri = entry_proje_adi.get(), entry_musteri.get()
    if not proje or not musteri: return None, None 

    proje_clean, musteri_clean = temizle_dosya_adi(proje), temizle_dosya_adi(musteri)

    if ANA_KAYIT_YOLU is None: ayarlari_yukle() 
    if ANA_KAYIT_YOLU is None or not os.path.exists(ANA_KAYIT_YOLU):
        messagebox.showinfo("Konum Seçimi", "Projelerin kaydedileceği ana klasörü seçiniz.\n(Program bunu hatırlayacaktır)")
        secilen_yol = filedialog.askdirectory()
        if secilen_yol:
            ANA_KAYIT_YOLU = secilen_yol; ayarlari_kaydet()
        else: return None, None

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
    
    klasor_yolu, dosya_adi = klasor_hazirla()
    if not klasor_yolu: 
        if not sessiz: messagebox.showwarning("Eksik Bilgi", "Proje Adı ve Müşteri giriniz.")
        return False
    
    yeni_tam_yol = os.path.join(klasor_yolu, f"{dosya_adi}.json")
    veri = proje_verilerini_topla()
    
    try:
        if ACIK_DOSYA_YOLU and os.path.exists(ACIK_DOSYA_YOLU):
            if ACIK_DOSYA_YOLU == yeni_tam_yol: pass
            else:
                cevap = messagebox.askyesno("İsim Değişikliği", 
                                            f"Proje adı değişmiş.\n\nEski Dosya: {os.path.basename(ACIK_DOSYA_YOLU)}\nYeni Dosya: {dosya_adi}.json\n\nEski dosyayı silip yeni isimle mi kaydedilsin?")
                if cevap: 
                    try: os.remove(ACIK_DOSYA_YOLU)
                    except: pass
        
        with open(yeni_tam_yol, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)
            
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
    yukle_from_path(dosya_yolu)

def gecmisi_goster():
    global ANA_KAYIT_YOLU
    if ANA_KAYIT_YOLU is None:
        secilen_yol = filedialog.askdirectory(title="Projelerin Bulunduğu Klasörü Göster")
        if secilen_yol: ANA_KAYIT_YOLU = secilen_yol
        else: return

    # Toplevel Pencere (Hata önleyici .lift() eklendi)
    top = ctk.CTkToplevel(app)
    top.title("Teklif Geçmişi")
    top.geometry("600x450")
    top.after(10, top.lift) # Pencereyi öne getir
    top.focus_force()

    ctk.CTkLabel(top, text=f"Konum: {ANA_KAYIT_YOLU}", text_color="gray").pack(pady=5)
    ctk.CTkLabel(top, text="Kayıtlı Projeler", font=("Segoe UI", 16, "bold")).pack(pady=5)

    frame_list = ctk.CTkFrame(top)
    frame_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Standart Listbox ve CTk Scrollbar entegrasyonu (Daha stabil)
    listbox = tk.Listbox(frame_list, font=("Segoe UI", 11), bg="#2b2b2b", fg="white", 
                         borderwidth=0, highlightthickness=0, selectbackground="#1f538d")
    listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    scrollbar = ctk.CTkScrollbar(frame_list, command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)

    # Dosyaları Listele
    bulunan_dosyalar = [] 
    for root, dirs, files in os.walk(ANA_KAYIT_YOLU):
        for file in files:
            if file.endswith(".json") and file != "katalog.json":
                full_path = os.path.join(root, file)
                display_name = f"{os.path.basename(root)}  >>>  {file}"
                listbox.insert("end", display_name)
                bulunan_dosyalar.append(full_path)

    def secileni_yukle(event):
        if not listbox.curselection(): return
        index = listbox.curselection()[0]
        dosya_yolu = bulunan_dosyalar[index]
        yukle_from_path(dosya_yolu)
        top.destroy() 

    listbox.bind("<Double-Button-1>", secileni_yukle)

def yukle_from_path(dosya_yolu):
    global ACIK_DOSYA_YOLU 
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
        ACIK_DOSYA_YOLU = dosya_yolu
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

def pdf_olustur_ve_ac():
    if not proje_verileri:
        messagebox.showwarning("Uyarı", "Liste boş, PDF oluşturulamaz.")
        return

    klasor_yolu, dosya_adi = klasor_hazirla()
    if not klasor_yolu: return
    pdf_dosya_yolu = os.path.join(klasor_yolu, f"{dosya_adi}.pdf")

    try:
        try:
            kur_usd = float(entry_kur_usd.get().replace(',', '.'))
            kur_eur = float(entry_kur_eur.get().replace(',', '.'))
            kdv_orani = float(entry_kdv.get().replace(',', '.'))
        except:
            messagebox.showerror("Hata", "Kur veya KDV değerleri hatalı.")
            return

        c = canvas.Canvas(pdf_dosya_yolu, pagesize=A4)
        genislik, yukseklik = A4
        
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
            font_normal = 'Arial'; font_bold = 'Arial-Bold'
        except:
            font_normal = 'Helvetica'; font_bold = 'Helvetica-Bold'

        c.setFont(font_bold, 16)
        c.drawRightString(genislik - 30, yukseklik - 50, "MALİYET VE TEKLİF RAPORU")
        
        c.setFont(font_normal, 10)
        c.drawRightString(genislik - 30, yukseklik - 70, f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
        
        gecerlilik_tarihi = (datetime.now() + timedelta(days=15)).strftime('%d.%m.%Y')
        c.setFont(font_normal, 8) 
        c.drawRightString(genislik - 30, yukseklik - 82, f"Geçerlilik: {gecerlilik_tarihi}")
        
        c.setLineWidth(1)
        c.rect(30, yukseklik - 150, genislik - 60, 40)
        
        c.setFont(font_bold, 10)
        c.drawString(40, yukseklik - 125, "FİRMA:")
        c.drawString(40, yukseklik - 140, "PROJE:")
        
        c.setFont(font_normal, 10)
        c.drawString(100, yukseklik - 125, entry_musteri.get())
        c.drawString(100, yukseklik - 140, entry_proje_adi.get())

        y = yukseklik - 180
        satir_h = 20
        
        c.setFillColorRGB(0.95, 0.95, 0.95)
        c.rect(30, y, genislik - 60, satir_h, fill=1)
        c.setFillColorRGB(0, 0, 0)

        c.setFont(font_bold, 9)
        c.drawString(35, y + 6, "KATEGORİ")
        c.drawString(150, y + 6, "ÜRÜN / AÇIKLAMA")
        c.drawString(350, y + 6, "MİKTAR")
        c.drawString(420, y + 6, "BİRİM FİYAT ($)") 
        c.drawString(500, y + 6, "TUTAR ($)")      

        y -= satir_h
        c.setFont(font_normal, 9)
        toplam_teklif_usd = 0 

        for veri in proje_verileri:
            if y < 100: 
                c.showPage(); y = yukseklik - 50; c.setFont(font_normal, 9)

            orj_fiyat = veri['birim_fiyat']
            para = veri['para']
            
            if para == "TL": birim_fiyat_usd = orj_fiyat / kur_usd
            elif para == "EUR": birim_fiyat_usd = (orj_fiyat * kur_eur) / kur_usd
            else: birim_fiyat_usd = orj_fiyat
            
            satir_tutar_usd = birim_fiyat_usd * veri['miktar']
            toplam_teklif_usd += satir_tutar_usd

            urun_adi = veri["urun"][:35] + "..." if len(veri["urun"]) > 35 else veri["urun"]
            
            c.drawString(35, y + 6, veri["kategori"])
            c.drawString(150, y + 6, urun_adi)
            c.drawString(350, y + 6, f"{veri['miktar']:g} {veri['birim']}")
            c.drawString(420, y + 6, f"${format_para(birim_fiyat_usd)}") 
            c.drawString(500, y + 6, f"${format_para(satir_tutar_usd)}")
            
            c.setStrokeColorRGB(0.9, 0.9, 0.9)
            c.line(30, y, genislik - 30, y)
            c.setStrokeColorRGB(0, 0, 0)
            y -= satir_h

        kdv_tutari = toplam_teklif_usd * (kdv_orani / 100)
        genel_toplam = toplam_teklif_usd + kdv_tutari

        y -= 30 
        c.setFont(font_bold, 10)
        x_etiket = genislik - 280  
        x_para   = genislik - 100 

        c.drawString(x_etiket, y, "ARA TOPLAM (KDV HARİÇ):")
        c.drawString(x_para,   y, f"${format_para(toplam_teklif_usd)}")
        
        y -= 15 
        c.drawString(x_etiket, y, "GENEL TOPLAM (KDV DAHİL):")
        c.drawString(x_para,   y, f"${format_para(genel_toplam)}")

        y -= 60
        c.setFont(font_normal, 8)
        c.drawString(30, y, "* Fiyatlarımıza KDV dahildir (Yukarıda belirtilmiştir).")
        c.drawString(30, y - 10, "* Ödeme günü döviz kuru (TCMB Efektif Satış) geçerlidir.")
        
        c.setFont(font_bold, 10)
        c.drawString(genislik - 150, y, "TEKLİF VEREN")
        c.drawString(genislik - 150, y - 15, "Kaşe / İmza")

        c.save()
        os.startfile(pdf_dosya_yolu)
    except Exception as e:
        messagebox.showerror("Hata", f"PDF Oluşturulamadı:\n{e}")

def dosya_konumunu_ac():
    klasor_yolu, _ = klasor_hazirla()
    if klasor_yolu and os.path.exists(klasor_yolu): os.startfile(klasor_yolu)

def oto_kayit_dongusu(interval_ms):
    global oto_kayit_job
    if cmb_oto_kayit.get() == "Kapalı": return
    if entry_proje_adi.get() and entry_musteri.get():
        projeyi_kaydet(sessiz=True)
        print(f"Otomatik Kayıt: {datetime.now().strftime('%H:%M:%S')}")
    oto_kayit_job = app.after(interval_ms, lambda: oto_kayit_dongusu(interval_ms))

def oto_kayit_ayar_degisti(event=None):
    global oto_kayit_job
    if oto_kayit_job: app.after_cancel(oto_kayit_job); oto_kayit_job = None
    secim = cmb_oto_kayit.get()
    if secim == "Kapalı": return
    ms = 30000 
    if secim == "30 Saniye": ms = 30000
    elif secim == "1 Dakika": ms = 60000
    elif secim == "2 Dakika": ms = 120000
    elif secim == "5 Dakika": ms = 300000
    oto_kayit_dongusu(ms)

# --- İŞLEMLER ---
def kategori_degisti(event):
    secilen = cmb_kategori.get()
    cmb_urun.configure(values=katalog.get(secilen, []))
    if katalog.get(secilen): cmb_urun.set(katalog.get(secilen)[0])
    else: cmb_urun.set("")
    manuel_mod_kontrol()

def manuel_mod_kontrol():
    if var_manuel.get() == 1: 
        cmb_urun.configure(state="normal")
        cmb_urun.set("")
        cmb_urun.focus_set()
    else: 
        cmb_urun.configure(state="readonly")
        secilen = cmb_kategori.get()
        if katalog.get(secilen) and cmb_urun.get() not in katalog.get(secilen): 
            cmb_urun.set(katalog.get(secilen)[0])

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
        katalog[secilen_kat].append(girilen_urun); katalog_kaydet(katalog); cmb_urun.configure(values=katalog[secilen_kat])
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
            lbl.configure(text="...")

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
        
        lbl_ham_malzeme_val.configure(text=format_kur_goster(ham_malzeme_usd, kur_usd, kur_eur))
        lbl_ham_iscilik_val.configure(text=format_kur_goster(ham_iscilik_usd, kur_usd, kur_eur))
        lbl_ham_toplam_val.configure(text=format_kur_goster(ham_toplam_usd, kur_usd, kur_eur))
        lbl_satis_malzeme_val.configure(text=format_kur_goster(satis_malzeme_usd, kur_usd, kur_eur))
        lbl_satis_iscilik_val.configure(text=format_kur_goster(satis_iscilik_usd, kur_usd, kur_eur))
        lbl_satis_toplam_val.configure(text=format_kur_goster(satis_toplam_usd, kur_usd, kur_eur))
        lbl_tl_teklif_val.configure(text=format_kur_goster(teklif_usd, kur_usd, kur_eur))
        lbl_tl_kdvli_val.configure(text=format_kur_goster(kdvli_usd, kur_usd, kur_eur))
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
            katalog[secilen_kat].remove(secilen_urun); katalog_kaydet(katalog); cmb_urun.configure(values=katalog[secilen_kat]); cmb_urun.set("")

# --- ARAYÜZ (CustomTkinter) ---

app = ctk.CTk()
app.title("Teklif Hazırlama ve Maliyet Analizi")
# HATA ÖNLEME: Eğer 'zoomed' hatası alırsan burayı sil, yerine app.geometry("1000x800") yaz.
app.after(0, lambda: app.state('zoomed'))

# Treeview için Stil Ayarı (CustomTkinter'da direkt Treeview olmadığı için stil ile uyduruyoruz)
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", 
                background="#2b2b2b", 
                foreground="white", 
                fieldbackground="#2b2b2b", 
                rowheight=30,
                font=("Segoe UI", 10))
style.configure("Treeview.Heading", 
                background="#1f1f1f", 
                foreground="white", 
                relief="flat",
                font=("Segoe UI", 11, "bold"))
style.map("Treeview", background=[('selected', '#1f538d')]) # Seçilince mavi

# Header (Başlık) Frame
frame_head = ctk.CTkFrame(app, corner_radius=0) # Köşeleri dik olsun
frame_head.pack(fill="x", padx=0, pady=0)

f_left = ctk.CTkFrame(frame_head, fg_color="transparent")
f_left.pack(side="left", padx=20, pady=15)

ctk.CTkLabel(f_left, text="PROJE ADI:", font=("Segoe UI", 12, "bold")).pack(side="left")
entry_proje_adi = ctk.CTkEntry(f_left, width=200, placeholder_text="Yeni Proje")
entry_proje_adi.pack(side="left", padx=10)

ctk.CTkLabel(f_left, text="MÜŞTERİ:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(10, 0))
entry_musteri = ctk.CTkEntry(f_left, width=200, placeholder_text="Müşteri Firma")
entry_musteri.pack(side="left", padx=10)

f_right = ctk.CTkFrame(frame_head, fg_color="transparent")
f_right.pack(side="right", padx=20)

lbl_durum = ctk.CTkLabel(f_right, text="...", font=("Segoe UI", 14, "bold"))
lbl_durum.pack(side="right", padx=10)

entry_kur_eur = ctk.CTkEntry(f_right, width=60, justify="center"); entry_kur_eur.insert(0, "38.20"); entry_kur_eur.pack(side="right")
ctk.CTkLabel(f_right, text="EUR", text_color="#FBC02D", font=("Segoe UI", 12, "bold")).pack(side="right", padx=5)

entry_kur_usd = ctk.CTkEntry(f_right, width=60, justify="center"); entry_kur_usd.insert(0, "35.50"); entry_kur_usd.pack(side="right")
ctk.CTkLabel(f_right, text="USD", text_color="#00E676", font=("Segoe UI", 12, "bold")).pack(side="right", padx=5)

f_center = ctk.CTkFrame(frame_head, fg_color="transparent")
f_center.pack(side="left", expand=True)
ctk.CTkLabel(f_center, text="Oto Kayıt:", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
cmb_oto_kayit = ctk.CTkComboBox(f_center, values=["Kapalı", "30 Saniye", "1 Dakika", "2 Dakika", "5 Dakika"], width=120, command=oto_kayit_ayar_degisti)
cmb_oto_kayit.pack(side="left")

# Input Alanı
frame_input = ctk.CTkFrame(app, fg_color="transparent")
frame_input.pack(fill="x", padx=15, pady=10)

def create_card(parent, title):
    f = ctk.CTkFrame(parent)
    ctk.CTkLabel(f, text=title, font=("Segoe UI", 13, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=5)
    return f

# Panel 1: Malzeme
p1 = create_card(frame_input, "1. Malzeme & Hammadde")
p1.pack(side="left", fill="both", expand=True, padx=(0,10))

grid_f = ctk.CTkFrame(p1, fg_color="transparent")
grid_f.pack(fill="both", expand=True, padx=10, pady=5)

ctk.CTkLabel(grid_f, text="Kategori:").grid(row=0, column=0, sticky="e", pady=5)
cmb_kategori = ctk.CTkComboBox(grid_f, values=list(katalog.keys()), width=180, command=kategori_degisti)
cmb_kategori.grid(row=0, column=1, sticky="w", padx=5)
var_manuel = tk.IntVar()
ctk.CTkCheckBox(grid_f, text="Elle Yaz", variable=var_manuel, command=manuel_mod_kontrol, width=20, height=20).grid(row=0, column=2, sticky="w", padx=5)

ctk.CTkLabel(grid_f, text="Ürün:").grid(row=1, column=0, sticky="e", pady=5)
cmb_urun = ctk.CTkComboBox(grid_f, width=250); cmb_urun.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
ctk.CTkButton(grid_f, text="X", width=30, fg_color="#D32F2F", hover_color="#B71C1C", command=listeden_sil_buton).grid(row=1, column=3, padx=5)

ctk.CTkLabel(grid_f, text="Miktar/Fiyat:").grid(row=2, column=0, sticky="e", pady=5)
sub_f1 = ctk.CTkFrame(grid_f, fg_color="transparent")
sub_f1.grid(row=2, column=1, columnspan=3, sticky="w")
entry_adet = ctk.CTkEntry(sub_f1, width=50, justify="center"); entry_adet.insert(0, "1"); entry_adet.pack(side="left", padx=5)
cmb_birim = ctk.CTkComboBox(sub_f1, values=["Adet", "Kg", "Mt", "Tk", "Lt"], width=70); cmb_birim.pack(side="left")
entry_fiyat = ctk.CTkEntry(sub_f1, width=80, justify="right", placeholder_text="B.Fiyat"); entry_fiyat.pack(side="left", padx=5)
cmb_para = ctk.CTkComboBox(sub_f1, values=["TL", "USD", "EUR"], width=70); cmb_para.pack(side="left")

ctk.CTkButton(p1, text="LİSTEYE EKLE (+)", fg_color="#1976D2", hover_color="#1565C0", command=malzeme_ekle).pack(fill="x", padx=10, pady=10)
kategori_degisti(None) # Başlangıçta doldur

# Panel 2: Fason
p2 = create_card(frame_input, "2. Dış Hizmet / Fason")
p2.pack(side="left", fill="both", expand=True, padx=(0,10))

grid_f2 = ctk.CTkFrame(p2, fg_color="transparent")
grid_f2.pack(fill="both", expand=True, padx=10, pady=5)

ctk.CTkLabel(grid_f2, text="İşlem:").grid(row=0, column=0, sticky="e", pady=5)
cmb_oto_tur = ctk.CTkComboBox(grid_f2, values=["Lazer Kesim", "Abkant", "Taşlama", "Kaplama", "Otomasyon", "Nakliye"], width=180)
cmb_oto_tur.grid(row=0, column=1, sticky="w", padx=5)

ctk.CTkLabel(grid_f2, text="Açıklama:").grid(row=1, column=0, sticky="e", pady=5)
entry_oto_aciklama = ctk.CTkEntry(grid_f2, width=180); entry_oto_aciklama.grid(row=1, column=1, sticky="w", padx=5)

ctk.CTkLabel(grid_f2, text="Fiyat:").grid(row=2, column=0, sticky="e", pady=5)
sub_f2 = ctk.CTkFrame(grid_f2, fg_color="transparent")
sub_f2.grid(row=2, column=1, sticky="w")
entry_oto_fiyat = ctk.CTkEntry(sub_f2, width=80, justify="right"); entry_oto_fiyat.pack(side="left", padx=5)
cmb_oto_para = ctk.CTkComboBox(sub_f2, values=["TL", "USD", "EUR"], width=70); cmb_oto_para.pack(side="left")

ctk.CTkButton(p2, text="EKLE (+)", fg_color="#1976D2", hover_color="#1565C0", command=otomasyon_ekle).pack(fill="x", padx=10, pady=10)

# Panel 3: İşçilik
p3 = create_card(frame_input, "3. Atölye İşçilik")
p3.pack(side="left", fill="both", expand=True)

grid_f3 = ctk.CTkFrame(p3, fg_color="transparent")
grid_f3.pack(fill="both", expand=True, padx=10, pady=5)

ctk.CTkLabel(grid_f3, text="Kişi Sayısı:").grid(row=0, column=0, sticky="e", pady=5)
entry_isci_kisi = ctk.CTkEntry(grid_f3, width=60, justify="center"); entry_isci_kisi.insert(0, "1"); entry_isci_kisi.grid(row=0, column=1, sticky="w", padx=5)

ctk.CTkLabel(grid_f3, text="Saat/Kişi:").grid(row=1, column=0, sticky="e", pady=5)
entry_isci_saat = ctk.CTkEntry(grid_f3, width=60, justify="center"); entry_isci_saat.grid(row=1, column=1, sticky="w", padx=5)

ctk.CTkLabel(grid_f3, text="Saat Ücreti:").grid(row=2, column=0, sticky="e", pady=5)
sub_f3 = ctk.CTkFrame(grid_f3, fg_color="transparent")
sub_f3.grid(row=2, column=1, sticky="w")
entry_isci_ucret = ctk.CTkEntry(sub_f3, width=80, justify="right"); entry_isci_ucret.insert(0, "1100"); entry_isci_ucret.pack(side="left", padx=5)
cmb_isci_para = ctk.CTkComboBox(sub_f3, values=["TL", "USD", "EUR"], width=70); cmb_isci_para.pack(side="left")

ctk.CTkButton(p3, text="EKLE (+)", fg_color="#1976D2", hover_color="#1565C0", command=iscelik_ekle).pack(fill="x", padx=10, pady=10)

# Butonlar ve Filtre
f_ctrl = ctk.CTkFrame(app, fg_color="transparent")
f_ctrl.pack(fill="x", padx=15, pady=5)

ctk.CTkLabel(f_ctrl, text="Filtre:", font=("Segoe UI", 12, "bold")).pack(side="left")
cmb_filtre = ctk.CTkComboBox(f_ctrl, values=["Tümü", "Sadece Malzeme", "Sadece İşçilik", "Sadece Dış Hizmet"], command=lambda e: tabloyu_guncelle())
cmb_filtre.pack(side="left", padx=10)

# Sağ Taraftaki Buton Grubu
btns = [
    ("Klasörü Aç", dosya_konumunu_ac, "#607D8B"),
    ("Projeyi Yükle", projeyi_yukle, "#8E24AA"),
    ("Teklif Geçmişi", gecmisi_goster, "#3949AB"),
    ("Projeyi Kaydet", lambda: projeyi_kaydet(False), "#FBC02D"),
    ("PDF Oluştur", pdf_olustur_ve_ac, "#D81B60"),
    ("Excel Oluştur", excele_aktar, "#43A047"),
    ("Sıfırla", sifirla, "#D32F2F"),
    ("Sil", sil, "#E64A19")
]

for txt, cmd, col in reversed(btns):
    ctk.CTkButton(f_ctrl, text=txt, command=cmd, fg_color=col, width=100).pack(side="right", padx=5)

# Liste (Treeview)
f_list = ctk.CTkFrame(app, fg_color="transparent")
f_list.pack(fill="both", expand=True, padx=15, pady=5)

scroll = ctk.CTkScrollbar(f_list)
scroll.pack(side="right", fill="y")

cols = ("k", "u", "m", "f", "p", "t", "ht", "gbf") 
tablo = ttk.Treeview(f_list, columns=cols, show="headings", selectmode="extended", yscrollcommand=scroll.set)
tablo.pack(side="left", fill="both", expand=True)
scroll.configure(command=tablo.yview)

headers = ["Kategori", "Ürün / Açıklama", "Miktar", "Birim Fiyat", "Para", "Toplam Tutar", "", ""]
widths = [150, 400, 100, 120, 80, 150, 0, 0]
for col, t, w in zip(cols, headers, widths):
    tablo.heading(col, text=t, command=lambda c=col: sirala(c, False))
    tablo.column(col, width=w, anchor="w" if col in ["k","u"] else "center")
tablo.column("ht", width=0, stretch=False); tablo.column("gbf", width=0, stretch=False)

# Alt Bilgi ve Hesaplama Kartları
f_foot = ctk.CTkFrame(app, height=100)
f_foot.pack(fill="x", padx=15, pady=15, side="bottom")

# Hesaplama Girişleri (Sol)
f_calc = ctk.CTkFrame(f_foot, fg_color="transparent")
f_calc.pack(side="left", padx=20, pady=10)
ctk.CTkLabel(f_calc, text="Hesaplama Parametreleri", font=("Segoe UI", 12, "bold"), text_color="gray").grid(row=0, column=0, columnspan=2, sticky="w")
ctk.CTkLabel(f_calc, text="Malzeme %:").grid(row=1, column=0, sticky="e"); entry_kar_malzeme = ctk.CTkEntry(f_calc, width=50); entry_kar_malzeme.insert(0, "30"); entry_kar_malzeme.grid(row=1, column=1, padx=5, pady=2)
ctk.CTkLabel(f_calc, text="İşçilik %:").grid(row=2, column=0, sticky="e"); entry_kar_iscilik = ctk.CTkEntry(f_calc, width=50); entry_kar_iscilik.insert(0, "60"); entry_kar_iscilik.grid(row=2, column=1, padx=5, pady=2)
ctk.CTkLabel(f_calc, text="KDV %:").grid(row=3, column=0, sticky="e"); entry_kdv = ctk.CTkEntry(f_calc, width=50); entry_kdv.insert(0, "20"); entry_kdv.grid(row=3, column=1, padx=5, pady=2)
ctk.CTkButton(f_calc, text="HESAPLA", command=hesapla, fg_color="#F57C00", width=120).grid(row=4, column=0, columnspan=2, pady=5)

# Sonuç Kartları (Sağ)
f_res = ctk.CTkFrame(f_foot, fg_color="transparent")
f_res.pack(side="right", fill="both", expand=True, padx=10, pady=10)

def create_res_card(parent, title, color_theme):
    f = ctk.CTkFrame(parent, fg_color=color_theme)
    ctk.CTkLabel(f, text=title, font=("Segoe UI", 12, "bold"), text_color="#333").pack(anchor="w", padx=10, pady=5)
    return f

# Kart 1
c1 = create_res_card(f_res, "1. Ham Maliyet", "#C8E6C9") # Açık Yeşil
c1.pack(side="left", fill="both", expand=True, padx=5)
lbl_ham_malzeme_val = ctk.CTkLabel(c1, text="...", text_color="#333"); lbl_ham_malzeme_val.pack(anchor="e", padx=5)
lbl_ham_iscilik_val = ctk.CTkLabel(c1, text="...", text_color="#333"); lbl_ham_iscilik_val.pack(anchor="e", padx=5)
ctk.CTkLabel(c1, text="TOPLAM HAM:", font=("Segoe UI", 12, "bold"), text_color="#1B5E20").pack(anchor="w", padx=5)
lbl_ham_toplam_val = ctk.CTkLabel(c1, text="...", font=("Consolas", 14, "bold"), text_color="#1B5E20"); lbl_ham_toplam_val.pack(anchor="e", padx=5)

# Kart 2
c2 = create_res_card(f_res, "2. Teklif Fiyatı", "#BBDEFB") # Açık Mavi
c2.pack(side="left", fill="both", expand=True, padx=5)
lbl_satis_malzeme_val = ctk.CTkLabel(c2, text="...", text_color="#333"); lbl_satis_malzeme_val.pack(anchor="e", padx=5)
lbl_satis_iscilik_val = ctk.CTkLabel(c2, text="...", text_color="#333"); lbl_satis_iscilik_val.pack(anchor="e", padx=5)
ctk.CTkLabel(c2, text="TOPLAM TEKLİF:", font=("Segoe UI", 12, "bold"), text_color="#0D47A1").pack(anchor="w", padx=5)
lbl_satis_toplam_val = ctk.CTkLabel(c2, text="...", font=("Consolas", 14, "bold"), text_color="#0D47A1"); lbl_satis_toplam_val.pack(anchor="e", padx=5)

# Kart 3
c3 = create_res_card(f_res, "3. Müşteri Özeti", "#FFE0B2") # Açık Turuncu
c3.pack(side="left", fill="both", expand=True, padx=5)
ctk.CTkLabel(c3, text="Ara Toplam:", text_color="#333").pack(anchor="w", padx=5)
lbl_tl_teklif_val = ctk.CTkLabel(c3, text="...", text_color="#333"); lbl_tl_teklif_val.pack(anchor="e", padx=5)
ctk.CTkLabel(c3, text="KDV DAHİL:", font=("Segoe UI", 14, "bold"), text_color="#E65100").pack(anchor="w", padx=5, pady=(5,0))
lbl_tl_kdvli_val = ctk.CTkLabel(c3, text="...", font=("Consolas", 18, "bold"), text_color="#E65100"); lbl_tl_kdvli_val.pack(anchor="e", padx=5)

baslat_kur_thread()
app.mainloop()