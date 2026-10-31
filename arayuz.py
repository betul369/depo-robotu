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

        butonlar = tk.Frame(pencere)
        butonlar.pack(padx=10, pady=10)
        tk.Button(butonlar, text="Dosyalari Yukle",
            command=self.dosyalari_yukle).pack(side=tk.LEFT, padx=5)

        self.tuval = tk.Canvas(pencere, width=400, height=300, bg="#f2f2f2")
        self.tuval.pack(padx=10, pady=10)


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
        self.izgara, self.baslangic = izgara, baslangic
        self.ayarlar, self.komutlar, self.hatalar = ayarlar, komutlar, hatalar
        self.durum = sim.yeni_durum(izgara, baslangic, ayarlar)
        self.ciz()

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





if __name__ == "__main__":
    pencere = tk.Tk()
    Uygulama(pencere)
    pencere.mainloop()