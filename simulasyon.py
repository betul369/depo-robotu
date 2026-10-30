#Depo Robotu Simulatoru - kurallar ve dosya islemleri.

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
    
   

if __name__ == "__main__":
    #k, h = komutlari_oku("paket_ornek/test05/komutlar.txt")
        k, h = komutlari_oku("deneme_verileri/veri_1/komutlar.txt")
print([(x["satir"], x["icerik"]) for x in h])
#print(k)
#print([x["satir"] for x in h])

