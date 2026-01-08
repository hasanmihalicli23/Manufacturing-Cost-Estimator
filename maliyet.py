import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
import threading
import re
import json
import os

# --- VARSAYILAN KATALOG ---
varsayilan_katalog = {
    "Motorlar": ["Asenkron Motor 0.18 kW", "Asenkron Motor 0.37 kW", "Asenkron Motor 0.55 kW", "Asenkron Motor 0.75 kW", "Asenkron Motor 1.5 kW", "Servo Motor 400W", "Servo Motor 750W", "Step Motor"],
    "Redüktörler": ["Sonsuz Vida 30 Gövde", "Sonsuz Vida 40 Gövde", "Sonsuz Vida 50 Gövde", "Helisel Dişli", "Planet Redüktör"],
    "Sürücüler": ["Hız Kontrol 0.37 kW", "Hız Kontrol 0.75 kW", "Hız Kontrol 1.5 kW", "Hız Kontrol 2.2 kW"],
    "Rulmanlar": ["UCFL 204", "UCFL 205", "UCP 204", "UCP 205", "6000 Serisi", "6200 Serisi", "Lineer Rulman"],
    "Konveyör Parçaları": ["Denge Ayağı M10", "Denge Ayağı M12", "Modüler Bant Dişlisi", "Avare Rulo Ø50", "Tahrik Rulosu Ø60"],
    "Hammadde: Saclar": ["DKP Sac 1mm", "DKP Sac 2mm", "DKP Sac 3mm", "Paslanmaz Sac 1mm", "Paslanmaz Sac 2mm", "Galvaniz Sac"],
    "Hammadde: Profiller": ["Kutu Profil 30x30", "Kutu Profil 40x40", "Sigma Profil 30x30", "Sigma Profil 45x45"],
    "Hammadde: Dolu": ["Lama 30x5", "Lama 40x10", "Kare Dolu 20x20", "Transmisyon Mili Ø20", "Civa Çeliği Ø20"],
    "Civatalar": ["M5 Civata", "M6 Civata", "M8 Civata", "M10 Civata", "M8 Somun", "M10 Pul"],
    "Pnömatik": ["Piston Ø32", "Piston Ø50", "Valf 5/2", "Rekorlar", "Hortum"],
    "Diğer / Özel Giriş": ["Diğer (Manuel Giriş)"]
}

DOSYA_ADI = "katalog.json"

# --- VERİTABANI YÖNETİMİ ---
def katalog_yukle():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return varsayilan_katalog
    else:
        katalog_kaydet(varsayilan_katalog)
        return varsayilan_katalog

def katalog_kaydet(veri):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

katalog = katalog_yukle()

# --- KUR ÇEKME ---
def tcmb_kur_getir():
    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        res = requests.get(url)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            for currency in root.findall('Currency'):
                kod = currency.get('Kod')
                if kod == 'USD':
                    entry_kur_usd.delete(0, 'end'); entry_kur_usd.insert(0, currency.find('ForexSelling').text)
                elif kod == 'EUR':
                    entry_kur_eur.delete(0, 'end'); entry_kur_eur.insert(0, currency.find('ForexSelling').text)
            lbl_durum.config(text="Kurlar Güncel (TCMB) ✅", fg="#4CAF50")
        else: lbl_durum.config(text="TCMB Hatası!", fg="red")
    except: lbl_durum.config(text="Kur Çekilemedi", fg="orange")

def baslat_kur_thread(): threading.Thread(target=tcmb_kur_getir).start()

# --- FONKSİYONLAR ---
def kategori_degisti(event):
    secilen = cmb_kategori.get()
    cmb_urun['values'] = katalog.get(secilen, [])
    if katalog.get(secilen): cmb_urun.current(0)
    else: cmb_urun.set("")
    manuel_mod_kontrol()

def manuel_mod_kontrol():
    if var_manuel.get() == 1: 
        cmb_urun.config(state="normal"); cmb_urun.set(""); cmb_urun.focus_set()
    else: 
        cmb_urun.config(state="readonly")
        secilen = cmb_kategori.get()
        if katalog.get(secilen) and cmb_urun.get() not in katalog.get(secilen):
            cmb_urun.current(0)

def tabloya_ekle(kategori, urun, adet, birim_fiyat, para_birimi):
    try:
        tutar = float(adet) * float(birim_fiyat)
        tablo.insert("", "end", values=(kategori, urun, adet, f"{float(birim_fiyat):.2f}", para_birimi, f"{tutar:.2f}"))
    except: messagebox.showerror("Hata", "Sayısal değer hatası.")

def malzeme_ekle():
    if not entry_fiyat.get(): return
    secilen_kat = cmb_kategori.get()
    girilen_urun = cmb_urun.get()
    
    tabloya_ekle(secilen_kat, girilen_urun, entry_adet.get().replace(',', '.'), entry_fiyat.get().replace(',', '.'), cmb_para.get())
    
    # Yeni ürünse kaydet
    if secilen_kat in katalog:
        if girilen_urun not in katalog[secilen_kat]:
            katalog[secilen_kat].append(girilen_urun)
            katalog_kaydet(katalog)
            cmb_urun['values'] = katalog[secilen_kat]

    entry_adet.delete(0, 'end'); entry_adet.insert(0, "1"); entry_fiyat.delete(0, 'end')

# --- YENİ EKLENEN SİLME FONKSİYONU ---
def listeden_sil():
    secilen_kat = cmb_kategori.get()
    secilen_urun = cmb_urun.get()
    
    if not secilen_urun: return

    if secilen_kat in katalog and secilen_urun in katalog[secilen_kat]:
        # Onay İste
        onay = messagebox.askyesno("Kalıcı Sil", f"'{secilen_urun}' ürünü listeden ve veritabanından tamamen silinsin mi?")
        if onay:
            try:
                # Listeden çıkar
                katalog[secilen_kat].remove(secilen_urun)
                # Dosyayı güncelle
                katalog_kaydet(katalog)
                # Arayüzü güncelle
                cmb_urun['values'] = katalog[secilen_kat]
                cmb_urun.set("")
                if katalog[secilen_kat]: cmb_urun.current(0)
                messagebox.showinfo("Silindi", "Ürün başarıyla kaldırıldı.")
            except Exception as e:
                messagebox.showerror("Hata", f"Silinirken hata oluştu: {e}")
    else:
        messagebox.showwarning("Uyarı", "Bu ürün zaten listede kayıtlı değil (veya manuel yazılmış).")

def iscelik_ekle():
    try:
        kisi = float(entry_isci_kisi.get().replace(',', '.'))
        saat = float(entry_isci_saat.get().replace(',', '.'))
        ucret = float(entry_isci_ucret.get().replace(',', '.'))
        toplam = kisi * saat * ucret
        tabloya_ekle("İŞÇİLİK GİDERİ", f"{int(kisi)} Kişi x {saat} Saat (Birim: {ucret})", 1, toplam, cmb_isci_para.get())
    except: messagebox.showerror("Hata", "İşçilik hatası.")

def otomasyon_ekle():
    try:
        fiyat = float(entry_oto_fiyat.get().replace(',', '.'))
        aciklama = entry_oto_aciklama.get() or "Dış Otomasyon Hizmeti"
        tabloya_ekle("DIŞ OTOMASYON", aciklama, 1, fiyat, cmb_oto_para.get())
        entry_oto_fiyat.delete(0, 'end')
    except: messagebox.showerror("Hata", "Otomasyon fiyatı giriniz.")

def sil():
    for i in tablo.selection(): tablo.delete(i)

def sifirla():
    if messagebox.askyesno("Sıfırla", "Tüm liste silinecek?"):
        for i in tablo.get_children(): tablo.delete(i)
        entry_proje_adi.delete(0, 'end')
        for lbl in [lbl_ham_malzeme, lbl_ham_iscilik, lbl_ham_toplam, lbl_satis_malzeme, lbl_satis_iscilik, lbl_satis_toplam, lbl_tl_teklif, lbl_tl_kdvli]:
            lbl.config(text="0.00")

def hesapla():
    try:
        kur_usd = float(entry_kur_usd.get().replace(',', '.'))
        kur_eur = float(entry_kur_eur.get().replace(',', '.'))
        marj_malzeme = float(entry_kar_malzeme.get().replace(',', '.'))
        marj_iscilik = float(entry_kar_iscilik.get().replace(',', '.'))
        kdv_orani = float(entry_kdv.get().replace(',', '.'))

        ham_malzeme_usd = 0; ham_iscilik_usd = 0
        satis_malzeme_usd = 0; satis_iscilik_usd = 0

        for satir in tablo.get_children():
            vals = tablo.item(satir)['values']
            kat, tutar_org, para = vals[0], float(vals[5]), vals[4]

            if para == "TL": tutar_usd = tutar_org / kur_usd
            elif para == "USD": tutar_usd = tutar_org
            elif para == "EUR": tutar_usd = (tutar_org * kur_eur) / kur_usd
            
            if kat == "İŞÇİLİK GİDERİ":
                ham_iscilik_usd += tutar_usd
                satis_iscilik_usd += tutar_usd * (1 + (marj_iscilik / 100))
            else:
                ham_malzeme_usd += tutar_usd
                satis_malzeme_usd += tutar_usd * (1 + (marj_malzeme / 100))

        ham_toplam_usd = ham_malzeme_usd + ham_iscilik_usd
        satis_toplam_usd = satis_malzeme_usd + satis_iscilik_usd
        teklif_tl = satis_toplam_usd * kur_usd
        kdv_tutari = teklif_tl * (kdv_orani / 100)
        
        lbl_ham_malzeme.config(text=f"$ {ham_malzeme_usd:,.2f}")
        lbl_ham_iscilik.config(text=f"$ {ham_iscilik_usd:,.2f}")
        lbl_ham_toplam.config(text=f"$ {ham_toplam_usd:,.2f}")
        lbl_satis_malzeme.config(text=f"$ {satis_malzeme_usd:,.2f}")
        lbl_satis_iscilik.config(text=f"$ {satis_iscilik_usd:,.2f}")
        lbl_satis_toplam.config(text=f"$ {satis_toplam_usd:,.2f}")
        lbl_tl_teklif.config(text=f"₺ {teklif_tl:,.2f}")
        lbl_tl_kdvli.config(text=f"₺ {teklif_tl + kdv_tutari:,.2f}")

    except ValueError: messagebox.showerror("Hata", "Oranları ve kurları kontrol edin.")

def excele_aktar():
    proje = entry_proje_adi.get().strip()
    if not proje: messagebox.showwarning("Uyarı", "Proje Adı giriniz!"); return
    
    temiz_proje_adi = re.sub(r'[\\/*?:<>|]', '', proje)
    dosya = f"{temiz_proje_adi}.xlsx"

    veriler = [tablo.item(s)['values'] for s in tablo.get_children()]
    if not veriler: return

    df = pd.DataFrame(veriler, columns=["Kategori", "Ürün", "Miktar", "Birim Fiyat", "Para", "Tutar"])
    hesapla()
    
    try:
        with pd.ExcelWriter(dosya, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detaylar', index=False)
            ozet_data = {
                'Kalem': ['Proje', 'Tarih', 'USD Kuru', '--- HAM ---', 'Ham Malzeme ($)', 'Ham İşçilik ($)', '--- SATIŞ ---', 'Teklif Toplam ($)', 'KDV Dahil (TL)'],
                'Değer': [proje, datetime.now().strftime('%d.%m.%Y'), entry_kur_usd.get(), '', lbl_ham_malzeme.cget("text"), lbl_ham_iscilik.cget("text"), '', lbl_satis_toplam.cget("text"), lbl_tl_kdvli.cget("text")]
            }
            pd.DataFrame(ozet_data).to_excel(writer, sheet_name='Detaylı Özet', index=False)
        messagebox.showinfo("Tamam", f"Kaydedildi: {dosya}")
    except Exception as e: messagebox.showerror("Hata", str(e))

# --- ARAYÜZ ---
app = tk.Tk()
app.title("Elif Makina - Teklif Modülü v11.0 (Katalog Yönetimi)")
app.geometry("1200x900")

# BAŞLIK
frame_head = tk.Frame(app, bg="#263238", pady=15, padx=10); frame_head.pack(fill="x")
tk.Label(frame_head, text="PROJE ADI:", fg="white", bg="#263238", font=("Arial", 10, "bold")).pack(side="left")
entry_proje_adi = tk.Entry(frame_head, width=30, font=("Arial", 11)); entry_proje_adi.pack(side="left", padx=10); entry_proje_adi.insert(0, "Yeni_Proje")
entry_kur_usd = tk.Entry(frame_head, width=7); entry_kur_usd.pack(side="right", padx=5); entry_kur_usd.insert(0, "35.50")
tk.Label(frame_head, text="USD:", fg="#4CAF50", bg="#263238").pack(side="right")
entry_kur_eur = tk.Entry(frame_head, width=7); entry_kur_eur.pack(side="right", padx=5); entry_kur_eur.insert(0, "38.20")
tk.Label(frame_head, text="EUR:", fg="#FFC107", bg="#263238").pack(side="right")
lbl_durum = tk.Label(frame_head, text="...", bg="#263238", fg="gray"); lbl_durum.pack(side="right", padx=10)

# GİRİŞ ALANLARI
frame_main = tk.Frame(app); frame_main.pack(fill="x", padx=5, pady=5)

# Malzeme (SİL BUTONU EKLENDİ)
f1 = tk.LabelFrame(frame_main, text="1. Malzeme & Hammadde", fg="#0D47A1", font=("Arial", 9, "bold")); f1.pack(side="left", fill="both", expand=True, padx=5)
tk.Label(f1, text="Kategori:").grid(row=0, column=0)
cmb_kategori = ttk.Combobox(f1, values=list(katalog.keys()), state="readonly", width=22); cmb_kategori.grid(row=0, column=1, columnspan=2); cmb_kategori.current(0); cmb_kategori.bind("<<ComboboxSelected>>", kategori_degisti)

var_manuel = tk.IntVar()
chk_manuel = tk.Checkbutton(f1, text="Listede Yok / Elle Yaz", variable=var_manuel, command=manuel_mod_kontrol, fg="red"); chk_manuel.grid(row=1, column=0, columnspan=3, sticky="w", padx=5)

tk.Label(f1, text="Ürün:").grid(row=2, column=0)
cmb_urun = ttk.Combobox(f1, width=22); cmb_urun.grid(row=2, column=1, columnspan=2)

# SİL BUTONU BURADA
btn_listeden_sil = tk.Button(f1, text="X", command=listeden_sil, bg="#B71C1C", fg="white", font=("Arial", 8, "bold"), width=2)
btn_listeden_sil.grid(row=2, column=3, padx=2)

tk.Label(f1, text="Miktar:").grid(row=3, column=0)
entry_adet = tk.Entry(f1, width=5); entry_adet.grid(row=3, column=1, sticky="w"); entry_adet.insert(0, "1")
tk.Label(f1, text="Fiyat:").grid(row=4, column=0)
entry_fiyat = tk.Entry(f1, width=10); entry_fiyat.grid(row=4, column=1, sticky="w")
cmb_para = ttk.Combobox(f1, values=["TL", "USD", "EUR"], width=5, state="readonly"); cmb_para.current(0); cmb_para.grid(row=4, column=2, sticky="w")
tk.Button(f1, text="EKLE", command=malzeme_ekle, bg="#4CAF50", fg="white").grid(row=5, column=0, columnspan=3, sticky="we", pady=5)
kategori_degisti(None)

# İşçilik
f2 = tk.LabelFrame(frame_main, text="2. İşçilik", fg="#E65100", font=("Arial", 9, "bold")); f2.pack(side="left", fill="both", expand=True, padx=5)
tk.Label(f2, text="Kişi Sayısı:").grid(row=0, column=0); entry_isci_kisi = tk.Entry(f2, width=5); entry_isci_kisi.grid(row=0, column=1); entry_isci_kisi.insert(0, "1")
tk.Label(f2, text="Toplam Saat:").grid(row=1, column=0); entry_isci_saat = tk.Entry(f2, width=5); entry_isci_saat.grid(row=1, column=1)
tk.Label(f2, text="Saat Ücreti:").grid(row=2, column=0); entry_isci_ucret = tk.Entry(f2, width=5); entry_isci_ucret.grid(row=2, column=1); entry_isci_ucret.insert(0, "300")
cmb_isci_para = ttk.Combobox(f2, values=["TL", "USD", "EUR"], width=4); cmb_isci_para.current(0); cmb_isci_para.grid(row=2, column=2)
tk.Button(f2, text="EKLE", command=iscelik_ekle, bg="#FF9800").grid(row=4, column=0, columnspan=3, sticky="we", pady=5)

# Otomasyon
f3 = tk.LabelFrame(frame_main, text="3. Dış Hizmet", fg="#4A148C", font=("Arial", 9, "bold")); f3.pack(side="left", fill="both", expand=True, padx=5)
tk.Label(f3, text="Açıklama:").pack(); entry_oto_aciklama = tk.Entry(f3, width=20); entry_oto_aciklama.pack()
tk.Label(f3, text="Fiyat:").pack(); f3_sub = tk.Frame(f3); f3_sub.pack()
entry_oto_fiyat = tk.Entry(f3_sub, width=10); entry_oto_fiyat.pack(side="left")
cmb_oto_para = ttk.Combobox(f3_sub, values=["TL", "USD", "EUR"], width=4); cmb_oto_para.current(0); cmb_oto_para.pack(side="left")
tk.Button(f3, text="EKLE", command=otomasyon_ekle, bg="#9C27B0", fg="white").pack(fill="x", pady=10)

# LİSTE
f_list = tk.Frame(app); f_list.pack(fill="both", expand=True, padx=10, pady=5)
cols = ("k", "u", "a", "f", "p", "t")
tablo = ttk.Treeview(f_list, columns=cols, show="headings"); tablo.pack(fill="both", expand=True)
for c, t, w in zip(cols, ["Kategori", "Ürün", "Adet", "Birim Fiyat", "Para", "Toplam"], [120, 250, 50, 80, 50, 80]): 
    tablo.heading(c, text=t); tablo.column(c, width=w)

# ANALİZ
f_foot = tk.LabelFrame(app, text="Fiyatlandırma & Analiz Paneli", padx=10, pady=10, bg="#ECEFF1", font=("Arial", 10, "bold"))
f_foot.pack(fill="x", padx=10, pady=10)

f_left = tk.Frame(f_foot, bg="#ECEFF1"); f_left.pack(side="left", fill="y", padx=10)
tk.Button(f_left, text="Sil", command=sil, bg="#FFCDD2").grid(row=0, column=0, sticky="ew", pady=2)
tk.Button(f_left, text="Sıfırla", command=sifirla, bg="#D32F2F", fg="white").grid(row=1, column=0, sticky="ew", pady=2)
tk.Button(f_left, text="Excel Kaydet", command=excele_aktar, bg="#2E7D32", fg="white").grid(row=2, column=0, sticky="ew", pady=2)

f_set = tk.LabelFrame(f_left, text="Kâr Oranları (%)", bg="#FFF3E0", padx=5, pady=5)
f_set.grid(row=0, column=1, rowspan=3, padx=10, sticky="ns")
tk.Label(f_set, text="Malzeme:", bg="#FFF3E0").grid(row=0, column=0); entry_kar_malzeme = tk.Entry(f_set, width=4); entry_kar_malzeme.grid(row=0, column=1); entry_kar_malzeme.insert(0, "30")
tk.Label(f_set, text="İşçilik:", bg="#FFF3E0").grid(row=1, column=0); entry_kar_iscilik = tk.Entry(f_set, width=4); entry_kar_iscilik.grid(row=1, column=1); entry_kar_iscilik.insert(0, "60")
tk.Label(f_set, text="KDV:", bg="#FFF3E0", fg="red").grid(row=2, column=0); entry_kdv = tk.Entry(f_set, width=4); entry_kdv.grid(row=2, column=1); entry_kdv.insert(0, "20")
tk.Button(f_set, text="HESAPLA", command=hesapla, bg="#FF9800", font=("Arial", 9, "bold")).grid(row=3, column=0, columnspan=2, pady=5)

f_res = tk.Frame(f_foot, bg="#ECEFF1"); f_res.pack(side="right", fill="both", expand=True)

f_col1 = tk.LabelFrame(f_res, text="1. Ham Maliyetler ($)", bg="#E3F2FD", padx=10, pady=5)
f_col1.pack(side="left", fill="both", expand=True, padx=5)
tk.Label(f_col1, text="Malzeme:", bg="#E3F2FD").pack(anchor="w"); lbl_ham_malzeme = tk.Label(f_col1, text="$ 0.00", bg="#E3F2FD", font=("Arial", 9, "bold")); lbl_ham_malzeme.pack(anchor="e")
tk.Label(f_col1, text="İşçilik:", bg="#E3F2FD").pack(anchor="w"); lbl_ham_iscilik = tk.Label(f_col1, text="$ 0.00", bg="#E3F2FD", font=("Arial", 9, "bold")); lbl_ham_iscilik.pack(anchor="e")
tk.Frame(f_col1, height=2, bg="black").pack(fill="x", pady=5); tk.Label(f_col1, text="TOPLAM HAM:", bg="#E3F2FD").pack(anchor="w"); lbl_ham_toplam = tk.Label(f_col1, text="$ 0.00", bg="#E3F2FD", font=("Arial", 11, "bold"), fg="#0D47A1"); lbl_ham_toplam.pack(anchor="e")

f_col2 = tk.LabelFrame(f_res, text="2. Teklif Fiyatları ($)", bg="#E8F5E9", padx=10, pady=5)
f_col2.pack(side="left", fill="both", expand=True, padx=5)
tk.Label(f_col2, text="Malzeme (Kârlı):", bg="#E8F5E9").pack(anchor="w"); lbl_satis_malzeme = tk.Label(f_col2, text="$ 0.00", bg="#E8F5E9", font=("Arial", 9, "bold")); lbl_satis_malzeme.pack(anchor="e")
tk.Label(f_col2, text="İşçilik (Kârlı):", bg="#E8F5E9").pack(anchor="w"); lbl_satis_iscilik = tk.Label(f_col2, text="$ 0.00", bg="#E8F5E9", font=("Arial", 9, "bold")); lbl_satis_iscilik.pack(anchor="e")
tk.Frame(f_col2, height=2, bg="black").pack(fill="x", pady=5); tk.Label(f_col2, text="TEKLİF TOPLAM:", bg="#E8F5E9").pack(anchor="w"); lbl_satis_toplam = tk.Label(f_col2, text="$ 0.00", bg="#E8F5E9", font=("Arial", 12, "bold"), fg="#1B5E20"); lbl_satis_toplam.pack(anchor="e")

f_col3 = tk.LabelFrame(f_res, text="3. Genel Toplam (TL)", bg="#FFEBEE", padx=10, pady=5)
f_col3.pack(side="left", fill="both", expand=True, padx=5)
tk.Label(f_col3, text="Teklif (KDV Hariç):", bg="#FFEBEE").pack(anchor="w"); lbl_tl_teklif = tk.Label(f_col3, text="₺ 0.00", bg="#FFEBEE", font=("Arial", 10, "bold"), fg="#0277BD"); lbl_tl_teklif.pack(anchor="e")
tk.Frame(f_col3, height=2, bg="black").pack(fill="x", pady=10); tk.Label(f_col3, text="KDV DAHİL:", bg="#FFEBEE").pack(anchor="w"); lbl_tl_kdvli = tk.Label(f_col3, text="₺ 0.00", bg="#FFEBEE", font=("Arial", 14, "bold"), fg="#D32F2F"); lbl_tl_kdvli.pack(anchor="e")

baslat_kur_thread()
app.mainloop()