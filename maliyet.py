"""
================================================================================
PROJE: Maliyet Analizi ve Otomatik Teklif Sistemi
YAZAR: Hasan Mihalıçlı
SÜRÜM: 1.3.0 (Final Stable - Order Fix)
TARİH: Ocak 2026

AÇIKLAMA:
- Fonksiyon tanımlama sırası düzeltildi (NameError giderildi).
- Önce mantık fonksiyonları, sonra arayüz çizimi gelir.
- Akıllı kayıt ve EXE özellikleri aktiftir.
================================================================================
"""

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
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# --- 1. AYARLAR VE SABİTLER ---
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

AYAR_DOSYASI = os.path.join(APP_DIR, "ayarlar.json")
DOSYA_ADI = os.path.join(APP_DIR, "katalog.json")

CTK_THEME = "blue"
CTK_APPEARANCE = "Dark"
APP_TITLE = "Teklif Hazırlama ve Maliyet Analizi"
FONT_MAIN = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 12, "bold")

COLOR_PRIMARY = "#1976D2"
COLOR_SECONDARY = "#546E7A"
COLOR_DANGER = "#D32F2F"
COLOR_SUCCESS = "#388E3C"

proje_verileri = []
oto_kayit_job = None 
ACIK_DOSYA_YOLU = None  

varsayilan_katalog = {
    "Motorlar": ["Asenkron Motor 0.18 kW", "Asenkron Motor 0.37 kW", "Asenkron Motor 0.55 kW"],
    "Redüktörler": ["Sonsuz Vida 30 Gövde", "Sonsuz Vida 50 Gövde", "Helisel Dişli"],
    "Sürücüler": ["Hız Kontrol 0.37 kW", "Hız Kontrol 0.75 kW", "Hız Kontrol 1.5 kW"],
    "Rulmanlar": ["UCFL 204", "UCFL 205", "UCP 204", "6204 ZZ"],
    "Hammadde: Saclar": ["DKP Sac 1mm", "DKP Sac 2mm", "Paslanmaz Sac 1mm"],
    "Hammadde: Profiller": ["Kutu Profil 30x30", "Kutu Profil 40x40", "Sigma Profil 30x30"],
    "Civatalar": ["M6 Civata", "M8 Civata", "M10 Civata"],
    "Pnömatik": ["Piston Ø32", "Piston Ø50", "Valf 5/2"],
    "Diğer / Özel Giriş": ["Diğer (Manuel Giriş)"]
}

# --- 2. YARDIMCI FONKSİYONLAR ---
def format_para(deger):
    try: return f"{float(deger):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def format_kur_goster(usd_tutar, kur_usd, kur_eur):
    tl_karsilik = usd_tutar * kur_usd
    eur_karsilik = (usd_tutar * kur_usd) / kur_eur if kur_eur > 0 else 0
    return f"USD: {format_para(usd_tutar):>10}\nEUR: {format_para(eur_karsilik):>10}\n TL: {format_para(tl_karsilik):>10}"

def temizle_dosya_adi(isim):
    return re.sub(r'[\\/*?:<>|]', '_', str(isim).strip())

def create_card(parent, title):
    f = ctk.CTkFrame(parent)
    ctk.CTkLabel(f, text=title, font=("Segoe UI", 13, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=5)
    return f

def create_res_card(parent, title, color_theme):
    f = ctk.CTkFrame(parent, fg_color=color_theme)
    ctk.CTkLabel(f, text=title, font=("Segoe UI", 12, "bold"), text_color="#333").pack(anchor="w", padx=10, pady=5)
    return f

# --- 3. VERİ YÖNETİMİ ---
def katalog_kaydet(veri):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=4)

def katalog_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as f: return json.load(f)
        except: return varsayilan_katalog
    else: 
        katalog_kaydet(varsayilan_katalog); return varsayilan_katalog

katalog = katalog_yukle()

# --- 4. İŞ MANTIĞI VE GUI FONKSİYONLARI (Arayüzden Önce Tanımlanmalı) ---

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
            lbl_durum.configure(text="Kurlar Güncel ✔", text_color=COLOR_SUCCESS) 
        else: lbl_durum.configure(text="Kur Hatası ✘", text_color=COLOR_DANGER) 
    except: lbl_durum.configure(text="Kur Hatası ✘", text_color=COLOR_DANGER)

def baslat_kur_thread(): threading.Thread(target=tcmb_kur_getir).start()

def proje_verilerini_topla():
    return {
        "metadata": {
            "proje_adi": entry_proje_adi.get(), "musteri": entry_musteri.get(),
            "kur_usd": entry_kur_usd.get(), "kur_eur": entry_kur_eur.get(),
            "kar_malzeme": entry_kar_malzeme.get(), "kar_iscilik": entry_kar_iscilik.get(), "kdv": entry_kdv.get()
        }, "items": proje_verileri
    }

def hesapla():
    try:
        kur_usd = float(entry_kur_usd.get().replace(',', '.')); kur_eur = float(entry_kur_eur.get().replace(',', '.'))
        marj_malzeme = float(entry_kar_malzeme.get().replace(',', '.')); marj_iscilik = float(entry_kar_iscilik.get().replace(',', '.'))
        kdv = float(entry_kdv.get().replace(',', '.'))
        ham_m = 0; ham_i = 0; satis_m = 0; satis_i = 0
        for veri in proje_verileri:
            tutar = veri["tutar"]
            if veri["para"] == "TL": tutar /= kur_usd
            elif veri["para"] == "EUR": tutar = (veri["tutar"] * kur_eur) / kur_usd
            if veri["tip"] == "ISCILIK": ham_i += tutar; satis_i += tutar * (1 + (marj_iscilik / 100))
            else: ham_m += tutar; satis_m += tutar * (1 + (marj_malzeme / 100))
        ham_toplam = ham_m + ham_i; satis_toplam = satis_m + satis_i
        lbl_ham_malzeme_val.configure(text=format_kur_goster(ham_m, kur_usd, kur_eur))
        lbl_ham_iscilik_val.configure(text=format_kur_goster(ham_i, kur_usd, kur_eur))
        lbl_ham_toplam_val.configure(text=format_kur_goster(ham_toplam, kur_usd, kur_eur))
        lbl_satis_malzeme_val.configure(text=format_kur_goster(satis_m, kur_usd, kur_eur))
        lbl_satis_iscilik_val.configure(text=format_kur_goster(satis_i, kur_usd, kur_eur))
        lbl_satis_toplam_val.configure(text=format_kur_goster(satis_toplam, kur_usd, kur_eur))
        lbl_tl_teklif_val.configure(text=format_kur_goster(satis_toplam, kur_usd, kur_eur))
        lbl_tl_kdvli_val.configure(text=format_kur_goster(satis_toplam * (1 + kdv/100), kur_usd, kur_eur))
    except: pass # İlk açılışta hata vermemesi için pass geçilebilir veya messagebox

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
                format_para(veri["birim_fiyat"]), veri["para"], format_para(veri["tutar"]), veri["tutar"], veri["birim_fiyat"]))

def projeyi_kaydet(sessiz=False):
    global ACIK_DOSYA_YOLU
    veri = proje_verilerini_topla(); proje_adi_ui = entry_proje_adi.get().strip()
    if not proje_adi_ui:
        if not sessiz: messagebox.showwarning("Eksik Bilgi", "Lütfen Proje Adı giriniz."); return False
    hedef_yol = None
    if ACIK_DOSYA_YOLU and os.path.exists(ACIK_DOSYA_YOLU):
        if temizle_dosya_adi(proje_adi_ui).lower() == os.path.splitext(os.path.basename(ACIK_DOSYA_YOLU))[0].lower():
            hedef_yol = ACIK_DOSYA_YOLU
    if not hedef_yol:
        if sessiz: return False 
        hedef_yol = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Elif Proje Dosyası", "*.json")], initialfile=f"{temizle_dosya_adi(proje_adi_ui)}.json", title="Projeyi Kaydet")
    if hedef_yol:
        try:
            with open(hedef_yol, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=4)
            ACIK_DOSYA_YOLU = hedef_yol
            if not sessiz: messagebox.showinfo("Başarılı", f"Proje kaydedildi:\n{hedef_yol}")
            return True
        except Exception as e:
            if not sessiz: messagebox.showerror("Hata", f"Kaydedilemedi: {e}"); return False
    return False

def yukle_from_path(dosya_yolu):
    global ACIK_DOSYA_YOLU, proje_verileri
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
        proje_verileri = veri.get("items", []); ACIK_DOSYA_YOLU = dosya_yolu
        tabloyu_guncelle(); hesapla(); messagebox.showinfo("Yüklendi", "Proje yüklendi.")
    except Exception as e: messagebox.showerror("Hata", f"Yüklenemedi: {e}")

def projeyi_yukle():
    dosya_yolu = filedialog.askopenfilename(filetypes=[("Elif Proje Dosyası", "*.json")])
    if dosya_yolu: yukle_from_path(dosya_yolu)

def excele_aktar():
    if not proje_verileri: messagebox.showwarning("Uyarı", "Liste boş."); return
    tam_yol = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=f"{temizle_dosya_adi(entry_proje_adi.get())}.xlsx", title="Excel Olarak Kaydet")
    if not tam_yol: return
    excel_data = []
    for veri in proje_verileri:
        t_tl = veri["tutar"] if veri["para"] == "TL" else 0
        t_usd = veri["tutar"] if veri["para"] == "USD" else 0
        t_eur = veri["tutar"] if veri["para"] == "EUR" else 0
        excel_data.append([veri["tip"], veri["kategori"], veri["urun"], veri["miktar"], veri["birim"], veri["birim_fiyat"], veri["para"], t_tl, t_usd, t_eur])
    df = pd.DataFrame(excel_data, columns=["Tip", "Kategori", "Ürün", "Miktar", "Birim", "Birim Fiyat", "Para", "TL", "USD", "EUR"])
    hesapla()
    try:
        with pd.ExcelWriter(tam_yol, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detaylar', index=False)
            ozet = {'Kalem': ['Proje', 'Müşteri', 'Tarih', 'USD', 'EUR', 'Toplam ($)', 'Teklif ($)', 'KDV Dahil ($)'],
                    'Değer': [entry_proje_adi.get(), entry_musteri.get(), datetime.now().strftime('%d.%m.%Y'), entry_kur_usd.get(), entry_kur_eur.get(),
                              lbl_ham_toplam_val.cget("text").split('\n')[0], lbl_satis_toplam_val.cget("text").split('\n')[0], lbl_tl_kdvli_val.cget("text").split('\n')[0]]}
            pd.DataFrame(ozet).to_excel(writer, sheet_name='Ozet', index=False)
        if messagebox.askyesno("Excel Hazır", f"Dosya oluşturuldu.\nAçmak ister misiniz?"): os.startfile(os.path.dirname(tam_yol))
    except Exception as e: messagebox.showerror("Hata", str(e))

def pdf_olustur_ve_ac():
    if not proje_verileri: messagebox.showwarning("Uyarı", "Liste boş."); return
    pdf_yol = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"{temizle_dosya_adi(entry_proje_adi.get())}.pdf", title="PDF Kaydet")
    if not pdf_yol: return
    try:
        kur_usd = float(entry_kur_usd.get().replace(',', '.')); kur_eur = float(entry_kur_eur.get().replace(',', '.'))
        kdv = float(entry_kdv.get().replace(',', '.'))
        c = canvas.Canvas(pdf_yol, pagesize=A4); w, h = A4
        try: pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf')); pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf')); font_n='Arial'; font_b='Arial-Bold'
        except: font_n='Helvetica'; font_b='Helvetica-Bold'
        c.setFont(font_b, 16); c.drawRightString(w-30, h-50, "MALİYET VE TEKLİF RAPORU")
        c.setFont(font_n, 10); c.drawRightString(w-30, h-70, f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
        c.rect(30, h-150, w-60, 40); c.setFont(font_b, 10); c.drawString(40, h-125, "FİRMA:"); c.drawString(40, h-140, "PROJE:")
        c.setFont(font_n, 10); c.drawString(100, h-125, entry_musteri.get()); c.drawString(100, h-140, entry_proje_adi.get())
        y = h-180; c.setFillColorRGB(0.95,0.95,0.95); c.rect(30, y, w-60, 20, fill=1); c.setFillColorRGB(0,0,0)
        c.setFont(font_b, 9); c.drawString(35, y+6, "KATEGORİ"); c.drawString(150, y+6, "ÜRÜN"); c.drawString(350, y+6, "MİKTAR"); c.drawString(420, y+6, "B.FİYAT($)"); c.drawString(500, y+6, "TUTAR($)")
        y -= 20; c.setFont(font_n, 9); top_usd = 0
        for v in proje_verileri:
            if y < 50: c.showPage(); y = h-50; c.setFont(font_n, 9)
            bf = v['birim_fiyat']; p = v['para']; bf_usd = bf/kur_usd if p=="TL" else (bf*kur_eur/kur_usd if p=="EUR" else bf)
            tut = bf_usd * v['miktar']; top_usd += tut
            c.drawString(35, y+6, v["kategori"]); c.drawString(150, y+6, v["urun"][:35]); c.drawString(350, y+6, f"{v['miktar']:g} {v['birim']}")
            c.drawString(420, y+6, f"${format_para(bf_usd)}"); c.drawString(500, y+6, f"${format_para(tut)}")
            c.setStrokeColorRGB(0.9,0.9,0.9); c.line(30, y, w-30, y); c.setStrokeColorRGB(0,0,0); y-=20
        genel = top_usd * (1 + kdv/100)
        y -= 30; c.setFont(font_b, 10); c.drawString(w-250, y, "ARA TOPLAM:"); c.drawString(w-100, y, f"${format_para(top_usd)}")
        y -= 15; c.drawString(w-250, y, "GENEL TOPLAM:"); c.drawString(w-100, y, f"${format_para(genel)}")
        c.save(); os.startfile(pdf_yol)
    except Exception as e: messagebox.showerror("Hata", str(e))

def oto_kayit_dongusu(ms):
    global oto_kayit_job
    if cmb_oto_kayit.get() == "Kapalı": return
    if entry_proje_adi.get(): projeyi_kaydet(sessiz=True)
    oto_kayit_job = app.after(ms, lambda: oto_kayit_dongusu(ms))

def oto_kayit_ayar_degisti(e=None):
    global oto_kayit_job
    if oto_kayit_job: app.after_cancel(oto_kayit_job); oto_kayit_job = None
    s = cmb_oto_kayit.get()
    if s != "Kapalı":
        ms = {"30 Saniye": 30000, "1 Dakika": 60000, "2 Dakika": 120000, "5 Dakika": 300000}
        oto_kayit_dongusu(ms.get(s, 60000))

def kategori_degisti(event):
    secilen = cmb_kategori.get()
    cmb_urun.configure(values=katalog.get(secilen, []))
    if katalog.get(secilen): cmb_urun.set(katalog.get(secilen)[0])
    else: cmb_urun.set("")
    manuel_mod_kontrol()

def manuel_mod_kontrol():
    if var_manuel.get() == 1: 
        cmb_urun.configure(state="normal"); cmb_urun.set(""); cmb_urun.focus_set()
    else: 
        cmb_urun.configure(state="readonly")
        secilen = cmb_kategori.get()
        if katalog.get(secilen) and cmb_urun.get() not in katalog.get(secilen): 
            cmb_urun.set(katalog.get(secilen)[0])

def listeden_sil_buton():
    kat = cmb_kategori.get(); urun = cmb_urun.get()
    if kat in katalog and urun in katalog[kat]:
        if messagebox.askyesno("Sil", f"'{urun}' silinsin mi?"):
            katalog[kat].remove(urun); katalog_kaydet(katalog); cmb_urun.configure(values=katalog[kat]); cmb_urun.set("")

def malzeme_ekle():
    if not entry_fiyat.get(): return
    secilen_kat = cmb_kategori.get(); girilen_urun = cmb_urun.get()
    try:
        tutar = float(entry_adet.get().replace(',', '.')) * float(entry_fiyat.get().replace(',', '.'))
        proje_verileri.append({"id": len(proje_verileri)+1, "tip": "MALZEME", "kategori": secilen_kat, "urun": girilen_urun,
            "miktar": float(entry_adet.get().replace(',', '.')), "birim": cmb_birim.get(), "birim_fiyat": float(entry_fiyat.get().replace(',', '.')), "para": cmb_para.get(), "tutar": tutar})
        tabloyu_guncelle()
    except: messagebox.showerror("Hata", "Sayısal Değer Hatası"); return

    if secilen_kat in katalog and girilen_urun not in katalog[secilen_kat]:
        katalog[secilen_kat].append(girilen_urun); katalog_kaydet(katalog); cmb_urun.configure(values=katalog[secilen_kat])
    entry_adet.delete(0, 'end'); entry_adet.insert(0, "1"); entry_fiyat.delete(0, 'end')

def otomasyon_ekle():
    try:
        tur = cmb_oto_tur.get(); aciklama = entry_oto_aciklama.get()
        fiyat = float(entry_oto_fiyat.get().replace(',', '.'))
        proje_verileri.append({"id": len(proje_verileri)+1, "tip": "FASON", "kategori": "DIŞ HİZMET / FASON", "urun": f"{tur} - {aciklama}" if aciklama else tur,
            "miktar": 1, "birim": "Hizmet", "birim_fiyat": fiyat, "para": cmb_oto_para.get(), "tutar": fiyat})
        tabloyu_guncelle()
        entry_oto_fiyat.delete(0, 'end'); entry_oto_aciklama.delete(0, 'end')
    except: messagebox.showerror("Hata", "Fiyat giriniz.")

def iscelik_ekle():
    try:
        kisi = float(entry_isci_kisi.get().replace(',', '.')); saat = float(entry_isci_saat.get().replace(',', '.'))
        ucret = float(entry_isci_ucret.get().replace(',', '.')); toplam_saat = kisi * saat
        tutar = toplam_saat * ucret
        proje_verileri.append({"id": len(proje_verileri)+1, "tip": "ISCILIK", "kategori": "İŞÇİLİK GİDERİ", "urun": f"{int(kisi)} Kişi Çalışması",
            "miktar": toplam_saat, "birim": "Saat", "birim_fiyat": ucret, "para": cmb_isci_para.get(), "tutar": tutar})
        tabloyu_guncelle()
    except: messagebox.showerror("Hata", "İşçilik değerlerini kontrol edin.")

def sifirla():
    if messagebox.askyesno("Sıfırla", "Tüm liste silinecek?"):
        proje_verileri.clear(); tabloyu_guncelle()
        entry_proje_adi.delete(0, 'end'); entry_musteri.delete(0, 'end')
        for lbl in [lbl_ham_malzeme_val, lbl_ham_iscilik_val, lbl_ham_toplam_val, lbl_satis_malzeme_val, lbl_satis_iscilik_val, lbl_satis_toplam_val, lbl_tl_teklif_val, lbl_tl_kdvli_val]:
            lbl.configure(text="...")

def sil():
    secili = tablo.selection()
    if not secili: return
    if messagebox.askyesno("Sil", "Seçili satırlar silinsin mi?"):
        silinecek_indexler = []
        for s in secili:
            vals = tablo.item(s)['values']
            for i, veri in enumerate(proje_verileri):
                if veri["urun"] == vals[1] and format_para(veri["tutar"]) == vals[5]: silinecek_indexler.append(i); break
        for i in sorted(silinecek_indexler, reverse=True): del proje_verileri[i]
        tabloyu_guncelle()

def sirala(col, reverse):
    l = [(float(tablo.set(k, "ham_tutar")) if col == "Tutar" else tablo.set(k, col), k) for k in tablo.get_children('')]
    l.sort(reverse=reverse, key=lambda x: x[0])
    for index, (val, k) in enumerate(l): tablo.move(k, '', index)
    tablo.heading(col, command=lambda: sirala(col, not reverse))

# --- 5. ARAYÜZ (GUI) OLUŞTURMA ---
ctk.set_appearance_mode(CTK_APPEARANCE); ctk.set_default_color_theme(CTK_THEME); ctk.set_widget_scaling(1.0)
app = ctk.CTk(); app.title(APP_TITLE)
app.after(0, lambda: app.state('zoomed') if os.name == 'nt' else app.geometry("1200x800"))
style = ttk.Style(); style.theme_use("clam")
style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=30, font=("Segoe UI", 10))
style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat", font=("Segoe UI", 11, "bold"))
style.map("Treeview", background=[('selected', '#1f538d')]) 

frame_head = ctk.CTkFrame(app, corner_radius=0); frame_head.pack(fill="x")
f_left = ctk.CTkFrame(frame_head, fg_color="transparent"); f_left.pack(side="left", padx=20, pady=15)
ctk.CTkLabel(f_left, text="PROJE ADI:", font=FONT_BOLD).pack(side="left")
entry_proje_adi = ctk.CTkEntry(f_left, width=200, placeholder_text="Yeni Proje"); entry_proje_adi.pack(side="left", padx=10)
ctk.CTkLabel(f_left, text="MÜŞTERİ:", font=FONT_BOLD).pack(side="left", padx=(10, 0))
entry_musteri = ctk.CTkEntry(f_left, width=200, placeholder_text="Müşteri Firma"); entry_musteri.pack(side="left", padx=10)
f_right = ctk.CTkFrame(frame_head, fg_color="transparent"); f_right.pack(side="right", padx=20)
lbl_durum = ctk.CTkLabel(f_right, text="...", font=("Segoe UI", 14, "bold")); lbl_durum.pack(side="right", padx=10)
entry_kur_eur = ctk.CTkEntry(f_right, width=60, justify="center"); entry_kur_eur.insert(0, "38.20"); entry_kur_eur.pack(side="right")
ctk.CTkLabel(f_right, text="EUR", text_color="#FBC02D", font=FONT_BOLD).pack(side="right", padx=5)
entry_kur_usd = ctk.CTkEntry(f_right, width=60, justify="center"); entry_kur_usd.insert(0, "35.50"); entry_kur_usd.pack(side="right")
ctk.CTkLabel(f_right, text="USD", text_color="#00E676", font=FONT_BOLD).pack(side="right", padx=5)
f_center = ctk.CTkFrame(frame_head, fg_color="transparent"); f_center.pack(side="left", expand=True)
ctk.CTkLabel(f_center, text="Oto Kayıt:", font=FONT_BOLD).pack(side="left", padx=5)
cmb_oto_kayit = ctk.CTkComboBox(f_center, values=["Kapalı", "30 Saniye", "1 Dakika", "2 Dakika", "5 Dakika"], width=120, command=oto_kayit_ayar_degisti); cmb_oto_kayit.pack(side="left")

frame_input = ctk.CTkFrame(app, fg_color="transparent"); frame_input.pack(fill="x", padx=15, pady=10)

p_malzeme = create_card(frame_input, "1. Malzeme & Hammadde"); p_malzeme.pack(side="left", fill="both", expand=True, padx=(0,10))
grid_f = ctk.CTkFrame(p_malzeme, fg_color="transparent"); grid_f.pack(fill="both", expand=True, padx=10, pady=5)
ctk.CTkLabel(grid_f, text="Kategori:").grid(row=0, column=0, sticky="e", pady=5)
cmb_kategori = ctk.CTkComboBox(grid_f, values=list(katalog.keys()), width=180, command=kategori_degisti); cmb_kategori.grid(row=0, column=1, sticky="w", padx=5)
var_manuel = tk.IntVar(); ctk.CTkCheckBox(grid_f, text="Elle Yaz", variable=var_manuel, command=manuel_mod_kontrol, width=20, height=20).grid(row=0, column=2, sticky="w", padx=5)
ctk.CTkLabel(grid_f, text="Ürün:").grid(row=1, column=0, sticky="e", pady=5)
cmb_urun = ctk.CTkComboBox(grid_f, width=250); cmb_urun.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)
ctk.CTkButton(grid_f, text="X", width=30, fg_color=COLOR_DANGER, hover_color="#B71C1C", command=listeden_sil_buton).grid(row=1, column=3, padx=5)
ctk.CTkLabel(grid_f, text="Miktar/Fiyat:").grid(row=2, column=0, sticky="e", pady=5)
sub_f1 = ctk.CTkFrame(grid_f, fg_color="transparent"); sub_f1.grid(row=2, column=1, columnspan=3, sticky="w")
entry_adet = ctk.CTkEntry(sub_f1, width=50, justify="center"); entry_adet.insert(0, "1"); entry_adet.pack(side="left", padx=5)
cmb_birim = ctk.CTkComboBox(sub_f1, values=["Adet", "Kg", "Mt", "Tk", "Lt"], width=70); cmb_birim.pack(side="left")
entry_fiyat = ctk.CTkEntry(sub_f1, width=80, justify="right", placeholder_text="B.Fiyat"); entry_fiyat.pack(side="left", padx=5)
cmb_para = ctk.CTkComboBox(sub_f1, values=["TL", "USD", "EUR"], width=70); cmb_para.pack(side="left")
ctk.CTkButton(p_malzeme, text="LİSTEYE EKLE (+)", fg_color=COLOR_PRIMARY, hover_color="#1565C0", command=malzeme_ekle).pack(fill="x", padx=10, pady=10)
kategori_degisti(None)

p_fason = create_card(frame_input, "2. Dış Hizmet / Fason"); p_fason.pack(side="left", fill="both", expand=True, padx=(0,10))
grid_f2 = ctk.CTkFrame(p_fason, fg_color="transparent"); grid_f2.pack(fill="both", expand=True, padx=10, pady=5)
ctk.CTkLabel(grid_f2, text="İşlem:").grid(row=0, column=0, sticky="e", pady=5)
cmb_oto_tur = ctk.CTkComboBox(grid_f2, values=["Lazer Kesim", "Abkant", "Taşlama", "Kaplama", "Otomasyon", "Nakliye"], width=180); cmb_oto_tur.grid(row=0, column=1, sticky="w", padx=5)
ctk.CTkLabel(grid_f2, text="Açıklama:").grid(row=1, column=0, sticky="e", pady=5); entry_oto_aciklama = ctk.CTkEntry(grid_f2, width=180); entry_oto_aciklama.grid(row=1, column=1, sticky="w", padx=5)
ctk.CTkLabel(grid_f2, text="Fiyat:").grid(row=2, column=0, sticky="e", pady=5)
sub_f2 = ctk.CTkFrame(grid_f2, fg_color="transparent"); sub_f2.grid(row=2, column=1, sticky="w")
entry_oto_fiyat = ctk.CTkEntry(sub_f2, width=80, justify="right"); entry_oto_fiyat.pack(side="left", padx=5)
cmb_oto_para = ctk.CTkComboBox(sub_f2, values=["TL", "USD", "EUR"], width=70); cmb_oto_para.pack(side="left")
ctk.CTkButton(p_fason, text="EKLE (+)", fg_color=COLOR_PRIMARY, hover_color="#1565C0", command=otomasyon_ekle).pack(fill="x", padx=10, pady=10)

p_iscilik = create_card(frame_input, "3. Atölye İşçilik"); p_iscilik.pack(side="left", fill="both", expand=True)
grid_f3 = ctk.CTkFrame(p_iscilik, fg_color="transparent"); grid_f3.pack(fill="both", expand=True, padx=10, pady=5)
ctk.CTkLabel(grid_f3, text="Kişi Sayısı:").grid(row=0, column=0, sticky="e", pady=5); entry_isci_kisi = ctk.CTkEntry(grid_f3, width=60, justify="center"); entry_isci_kisi.insert(0, "1"); entry_isci_kisi.grid(row=0, column=1, sticky="w", padx=5)
ctk.CTkLabel(grid_f3, text="Saat/Kişi:").grid(row=1, column=0, sticky="e", pady=5); entry_isci_saat = ctk.CTkEntry(grid_f3, width=60, justify="center"); entry_isci_saat.grid(row=1, column=1, sticky="w", padx=5)
ctk.CTkLabel(grid_f3, text="Saat Ücreti:").grid(row=2, column=0, sticky="e", pady=5)
sub_f3 = ctk.CTkFrame(grid_f3, fg_color="transparent"); sub_f3.grid(row=2, column=1, sticky="w")
entry_isci_ucret = ctk.CTkEntry(sub_f3, width=80, justify="right"); entry_isci_ucret.insert(0, "1100"); entry_isci_ucret.pack(side="left", padx=5)
cmb_isci_para = ctk.CTkComboBox(sub_f3, values=["TL", "USD", "EUR"], width=70); cmb_isci_para.pack(side="left")
ctk.CTkButton(p_iscilik, text="EKLE (+)", fg_color=COLOR_PRIMARY, hover_color="#1565C0", command=iscelik_ekle).pack(fill="x", padx=10, pady=10)

f_ctrl = ctk.CTkFrame(app, fg_color="transparent"); f_ctrl.pack(fill="x", padx=15, pady=5)
ctk.CTkLabel(f_ctrl, text="Filtre:", font=("Segoe UI", 12, "bold")).pack(side="left")
cmb_filtre = ctk.CTkComboBox(f_ctrl, values=["Tümü", "Sadece Malzeme", "Sadece İşçilik", "Sadece Dış Hizmet"], command=lambda e: tabloyu_guncelle()); cmb_filtre.pack(side="left", padx=10)
btns = [("Projeyi Aç", projeyi_yukle, COLOR_SECONDARY), ("Kaydet", lambda: projeyi_kaydet(False), COLOR_PRIMARY), 
        ("PDF", pdf_olustur_ve_ac, COLOR_PRIMARY), ("Excel", excele_aktar, COLOR_PRIMARY), ("Sıfırla", sifirla, COLOR_DANGER), ("Satır Sil", sil, COLOR_DANGER)]
for txt, cmd, col in reversed(btns): ctk.CTkButton(f_ctrl, text=txt, command=cmd, fg_color=col, width=90, height=32, font=("Segoe UI", 12, "bold")).pack(side="right", padx=5)

f_list = ctk.CTkFrame(app, fg_color="transparent"); f_list.pack(fill="both", expand=True, padx=15, pady=5)
scroll = ctk.CTkScrollbar(f_list); scroll.pack(side="right", fill="y")
cols = ("k", "u", "m", "f", "p", "t", "ht", "gbf") 
tablo = ttk.Treeview(f_list, columns=cols, show="headings", selectmode="extended", yscrollcommand=scroll.set); tablo.pack(side="left", fill="both", expand=True)
scroll.configure(command=tablo.yview)
headers = ["Kategori", "Ürün / Açıklama", "Miktar", "Birim Fiyat", "Para", "Toplam Tutar", "", ""]
widths = [150, 400, 100, 120, 80, 150, 0, 0]
for c, t, w in zip(cols, headers, widths): tablo.heading(c, text=t, command=lambda x=c: sirala(x, False)); tablo.column(c, width=w, anchor="w" if c in ["k","u"] else "center")
tablo.column("ht", width=0, stretch=False); tablo.column("gbf", width=0, stretch=False)

f_foot = ctk.CTkFrame(app, height=100); f_foot.pack(fill="x", padx=15, pady=15, side="bottom")
f_calc = ctk.CTkFrame(f_foot, fg_color="transparent"); f_calc.pack(side="left", padx=20, pady=10)
ctk.CTkLabel(f_calc, text="Hesaplama Parametreleri", font=("Segoe UI", 12, "bold"), text_color="gray").grid(row=0, column=0, columnspan=2, sticky="w")
ctk.CTkLabel(f_calc, text="Malzeme %:").grid(row=1, column=0, sticky="e"); entry_kar_malzeme = ctk.CTkEntry(f_calc, width=50); entry_kar_malzeme.insert(0, "30"); entry_kar_malzeme.grid(row=1, column=1, padx=5, pady=2)
ctk.CTkLabel(f_calc, text="İşçilik %:").grid(row=2, column=0, sticky="e"); entry_kar_iscilik = ctk.CTkEntry(f_calc, width=50); entry_kar_iscilik.insert(0, "60"); entry_kar_iscilik.grid(row=2, column=1, padx=5, pady=2)
ctk.CTkLabel(f_calc, text="KDV %:").grid(row=3, column=0, sticky="e"); entry_kdv = ctk.CTkEntry(f_calc, width=50); entry_kdv.insert(0, "20"); entry_kdv.grid(row=3, column=1, padx=5, pady=2)
ctk.CTkButton(f_calc, text="HESAPLA", command=hesapla, fg_color="#F57C00", width=120).grid(row=4, column=0, columnspan=2, pady=5)

f_res = ctk.CTkFrame(f_foot, fg_color="transparent"); f_res.pack(side="right", fill="both", expand=True, padx=10, pady=10)
c1 = create_res_card(f_res, "1. Ham Maliyet", "#C8E6C9"); c1.pack(side="left", fill="both", expand=True, padx=5)
lbl_ham_malzeme_val = ctk.CTkLabel(c1, text="...", text_color="#333"); lbl_ham_malzeme_val.pack(anchor="e", padx=5)
lbl_ham_iscilik_val = ctk.CTkLabel(c1, text="...", text_color="#333"); lbl_ham_iscilik_val.pack(anchor="e", padx=5)
ctk.CTkLabel(c1, text="TOPLAM HAM:", font=("Segoe UI", 12, "bold"), text_color="#1B5E20").pack(anchor="w", padx=5)
lbl_ham_toplam_val = ctk.CTkLabel(c1, text="...", font=("Consolas", 14, "bold"), text_color="#1B5E20"); lbl_ham_toplam_val.pack(anchor="e", padx=5)

c2 = create_res_card(f_res, "2. Teklif Fiyatı", "#BBDEFB"); c2.pack(side="left", fill="both", expand=True, padx=5)
lbl_satis_malzeme_val = ctk.CTkLabel(c2, text="...", text_color="#333"); lbl_satis_malzeme_val.pack(anchor="e", padx=5)
lbl_satis_iscilik_val = ctk.CTkLabel(c2, text="...", text_color="#333"); lbl_satis_iscilik_val.pack(anchor="e", padx=5)
ctk.CTkLabel(c2, text="TOPLAM TEKLİF:", font=("Segoe UI", 12, "bold"), text_color="#0D47A1").pack(anchor="w", padx=5)
lbl_satis_toplam_val = ctk.CTkLabel(c2, text="...", font=("Consolas", 14, "bold"), text_color="#0D47A1"); lbl_satis_toplam_val.pack(anchor="e", padx=5)

c3 = create_res_card(f_res, "3. Müşteri Özeti", "#FFE0B2"); c3.pack(side="left", fill="both", expand=True, padx=5)
ctk.CTkLabel(c3, text="Ara Toplam:", text_color="#333").pack(anchor="w", padx=5)
lbl_tl_teklif_val = ctk.CTkLabel(c3, text="...", text_color="#333"); lbl_tl_teklif_val.pack(anchor="e", padx=5)
ctk.CTkLabel(c3, text="KDV DAHİL:", font=("Segoe UI", 14, "bold"), text_color="#E65100").pack(anchor="w", padx=5, pady=(5,0))
lbl_tl_kdvli_val = ctk.CTkLabel(c3, text="...", font=("Consolas", 18, "bold"), text_color="#E65100"); lbl_tl_kdvli_val.pack(anchor="e", padx=5)

baslat_kur_thread()
app.mainloop()