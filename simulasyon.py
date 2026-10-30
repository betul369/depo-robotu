#Depo Robotu Simulatoru - kurallar ve dosya islemleri.
import json
def harita_oku(dosya_yolu):
    with open(dosya_yolu, encoding="utf-8") as f:
        satirlar = f.readlines()
        
    temiz = []
    for s in satirlar:
        temiz.append(s.rstrip("\r\n"))
        
    if len(temiz) == 0:
        raise ValueError("Harita bos")
        
    genislik = len(temiz[0])
    for satir in temiz:
        if len(satir) != genislik:
            raise ValueError("Satir uzunluklari farkli")
            
    baslangiclar = []
    for y, satir in enumerate(temiz):
        for x, hucre in enumerate(satir):
            if hucre == "R":
                baslangiclar.append((x, y))
            
    if len(baslangiclar) != 1:
        raise ValueError("Haritada tam olarak 1 robot (R) olmali")
                   
    izgara = []
    for satir in temiz:
        izgara.append(list(satir.replace("R", ".")))
    return izgara, baslangiclar[0]        
    

def komutlari_oku(dosya_yolu):
    komutlar = []
    hatalar = []
    with open(dosya_yolu, encoding="utf-8") as f:
        for no, ham in enumerate(f, start=1):
            satir = ham.strip()
            if satir == "":
                continue
            parcalar = satir.split()
            ad = parcalar[0]
            if ad == "ILERI":
                if len(parcalar) != 2:
                    hatalar.append({"satir": no, "icerik": satir,
                                    "neden": "ILERI tam olarak 1 sayi almali"})
                elif not parcalar[1].isdigit() or int(parcalar[1]) < 1:
                    hatalar.append({"satir": no, "icerik": satir,
                                    "neden": "ILERI icin pozitif tam sayi gerekli"})
                else:
                    komutlar.append(("ILERI", int(parcalar[1])))
            elif ad in ("SAG", "SOL", "AL", "BIRAK", "SARJ"):
                if len(parcalar) != 1:
                    hatalar.append({"satir": no, "icerik": satir,
                                    "neden": ad + " parametre almaz"})
                else:
                    komutlar.append((ad, None))
            else:
                hatalar.append({"satir": no, "icerik": satir,
                                "neden": "bilinmeyen komut"})
    return komutlar, hatalar    


def ayarlari_oku(dosya_yolu):
    with open(dosya_yolu, encoding="utf-8") as f:
        ayarlar = json.load(f)
        gerekli = ["batarya_kapasitesi", "baslangic_yonu", "adim_maliyeti",
                   "yuk_carpani", "donus_maliyeti", "carpisma_cezasi"]
        for anahtar in gerekli:
            if anahtar not in ayarlar:
                raise ValueError("ayarlar.json'da eksik anahtar: " + anahtar)
    return ayarlar
   

def yeni_durum(izgara, baslangic, ayarlar):
    x, y = baslangic
    return {
        "izgara": [satir[:] for satir in izgara],
        "x": x,
        "y": y,
        "yon": ayarlar["baslangic_yonu"],
        "batarya": ayarlar["batarya_kapasitesi"],
        "yuk": False,
        "teslim": 0,
        "carpisma": 0,
        "adim": 0,
        "bitti": False,
        "ziyaret": {(x, y): 1},
        "ayarlar": ayarlar,
    }






if __name__ == "__main__":
    a = ayarlari_oku("paket_ornek/test03/ayarlar.json")
    iz, r = harita_oku("paket_ornek/test03/harita.txt")
    d = yeni_durum(iz, r, a)
    print(d["x"], d["y"], d["yon"], d["batarya"])