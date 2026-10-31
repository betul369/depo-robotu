import os
import tkinter as tk
from tkinter import filedialog, messagebox

import simulasyon as sim

HUCRE = 40
RENKLER = {"#": "#555555", ".": "#ffffff", "K": "#c68642",
           "T": "#6aa84f", "S": "#ffd966"}


class Uygulama:
    def __init__(self, pencere):
        self.pencere = pencere
        pencere.title("Depo Robotu Simulatoru")

        self.izgara = None
        self.baslangic = None
        self.ayarlar = None
        self.komutlar = []
        self.hatalar = []
        self.durum = None
        self.klasör = None
        self.sira = 0
        self.log = []


        butonlar = tk.Frame(pencere)
        butonlar.pack(padx=10, pady=10)
        tk.Button(butonlar, text="Dosyalari Yukle",
            command=self.dosyalari_yukle).pack(side=tk.LEFT, padx=5)
        tk.Button(butonlar, text="Adim",
                  command=self.adim).pack(side=tk.LEFT, padx=5)
        tk.Button(butonlar, text="Tumunu Calistir",
                  command=self.tumunu_calistir).pack(side=tk.LEFT, padx=5)
        tk.Button(butonlar, text="Sifirla",
                  command=self.sifirla).pack(side=tk.LEFT, padx=5)
       
        orta = tk.Frame(pencere)
        orta.pack(padx=10)
        self.tuval = tk.Canvas(orta, width=400, height=300, bg="#f2f2f2")
        self.tuval.pack(side=tk.LEFT)
        self.bilgi = tk.Label(orta, text="", font=("Courier", 11),
                              justify=tk.LEFT, anchor="nw", width=22,
                              relief=tk.SOLID, bd=1)
        self.bilgi.pack(side=tk.LEFT, padx=10, fill=tk.Y)
 
        self.log_etiketi = tk.Label(pencere, text="", font=("Courier", 10),
                                    anchor="w", relief=tk.SOLID, bd=1)
        self.log_etiketi.pack(fill=tk.X, padx=10, pady=10)


    def dosyalari_yukle(self):
        klasor = filedialog.askdirectory(title="Girdi klasorunu sec")
        if not klasor:
            return
        try:
            izgara, baslangic = sim.harita_oku(os.path.join(klasor, "harita.txt"))
            ayarlar = sim.ayarlari_oku(os.path.join(klasor, "ayarlar.json"))
            komutlar, hatalar = sim.komutlari_oku(os.path.join(klasor, "komutlar.txt"))
        except FileNotFoundError as e:
            messagebox.showerror("Dosya bulunamadi", str(e))
            return
        except ValueError as e:
            messagebox.showerror("Dosya hatasi", str(e))
            return
        self.klasor = klasor
        self.izgara, self.baslangic = izgara, baslangic
        self.ayarlar, self.komutlar, self.hatalar = ayarlar, komutlar, hatalar
        self.durum = sim.yeni_durum(izgara, baslangic, ayarlar)
        self.sira = 0
        self.log = []
        self.log_etiketi.config(text="")
        self.ciz()
        self.bilgi_guncelle()
        if hatalar:
            satirlar = [f"Satir {h['satir']}: {h['icerik']}  ({h['neden']})"
                        for h in hatalar[:15]]
            messagebox.showwarning("Hatali komut satirlari atlandi","\n".join(satirlar))
    
    
    def ciz(self):
        self.tuval.delete("all")
        izgara = self.durum["izgara"]
        self.tuval.config(width=len(izgara[0]) * HUCRE,
                          height=len(izgara) * HUCRE)
        for y, satir in enumerate(izgara):
            for x, hucre in enumerate(satir):
                self.tuval.create_rectangle(
                    x * HUCRE, y * HUCRE, (x + 1) * HUCRE, (y + 1) * HUCRE,
                    fill=RENKLER[hucre], outline="#999999")
        self.robot_ciz()

    def robot_ciz(self):
        sol = self.durum["x"] * HUCRE
        ust = self.durum["y"] * HUCRE
        pay = 6
        a, b = sol + pay, ust + pay
        c, d = sol + HUCRE - pay, ust + HUCRE - pay
        ox, oy = sol + HUCRE // 2, ust + HUCRE // 2
        ucgenler = {
            "K": [ox, b, a, d, c, d],
            "D": [c, oy, a, b, a, d],
            "G": [ox, d, a, b, c, b],
            "B": [a, oy, c, b, c, d],
        }
        renk = "#e69138" if self.durum["yuk"] else "#1f77b4"
        self.tuval.create_polygon(ucgenler[self.durum["yon"]],fill=renk, outline="black")

    def bilgi_guncelle(self):
        d = self.durum
        kapasite = self.ayarlar["batarya_kapasitesi"]
        siradaki = "-"
        if self.sira < len(self.komutlar):
            siradaki = sim.komut_metni(self.komutlar[self.sira])
        metin = (f"Batarya : {d['batarya']}/{kapasite}\n"
                 f"Yon     : {d['yon']}\n"
                 f"Yuk     : {'Var' if d['yuk'] else 'Yok'}\n"
                 f"Teslim  : {d['teslim']}\n"
                 f"Carpisma: {d['carpisma']}\n"
                 f"Siradaki: {siradaki}")
        self.bilgi.config(text=metin)
 
    def devam_edebilir(self):
        return (self.durum is not None and not self.durum["bitti"]and self.sira < len(self.komutlar))
 
    def tek_komut(self):
        komut = self.komutlar[self.sira]
        olay = sim.komut_uygula(self.durum, komut)
        self.sira += 1
        self.log.append(sim.log_satiri(self.sira, komut, self.durum, olay))
        self.log_etiketi.config(
            text=f"Adim {self.sira}: {sim.komut_metni(komut)} -> "
                 f"({self.durum['x']},{self.durum['y']}) {olay}")
        self.ciz()
        self.bilgi_guncelle()
 
    def adim(self):
        if self.durum is None:
            messagebox.showinfo("Bilgi", "Once dosyalari yukleyin.")
            return
        if not self.devam_edebilir():
            return
        self.tek_komut()
        if not self.devam_edebilir():
            self.bitir()
 
    def tumunu_calistir(self):
        if self.durum is None:
            messagebox.showinfo("Bilgi", "Once dosyalari yukleyin.")
            return
        if not self.devam_edebilir():
            return
        while self.devam_edebilir():
            self.tek_komut()
        self.bitir()
 
    def sifirla(self):
        if self.durum is None:
            return
        self.durum = sim.yeni_durum(self.izgara, self.baslangic, self.ayarlar)
        self.sira = 0
        self.log = []
        self.log_etiketi.config(text="")
        self.ciz()
        self.bilgi_guncelle()
 
    def bitir(self):
        sonuc = sim.sonuc_olustur(self.durum)
        sonuc["hatali_satirlar"] = self.hatalar
        try:
            sim.sonuc_yaz(sonuc, os.path.join(self.klasor, "sonuc.json"))
            sim.log_yaz(self.log, os.path.join(self.klasor, "log.csv"))
        except OSError as e:
            messagebox.showerror("Yazma hatasi", str(e))
            return
        if self.durum["bitti"]:
            neden = "Batarya bitti, simulasyon durdu."
        else:
            neden = "Tum komutlar calistirildi."
        messagebox.showinfo(
            "Simulasyon bitti",
            f"{neden}\nTeslim: {self.durum['teslim']}\n"
            f"sonuc.json ve log.csv klasore yazildi.")



if __name__ == "__main__":
    pencere = tk.Tk()
    Uygulama(pencere)
    pencere.mainloop()