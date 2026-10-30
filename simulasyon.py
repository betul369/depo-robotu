#Depo Robotu Simulatoru - kurallar ve dosya islemleri.
import json
import csv
YONLER = ["K", "D", "G", "B"]
ADIM = {"K": (0, -1), "D": (1, 0), "G": (0, 1), "B": (-1, 0)}


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


def komut_uygula(durum, komut):
    ad, n = komut
    ayar = durum["ayarlar"]

    if durum["bitti"]:
        return "DURDU"

    if ad == "SAG" or ad == "SOL":
        maliyet = ayar["donus_maliyeti"]
        if maliyet > durum["batarya"]:
            durum["bitti"] = True
            return "BATARYA_BITTI"
        durum["batarya"] -= maliyet
        i = YONLER.index(durum["yon"])
        if ad == "SAG":
            i = (i + 1) % 4
        else:
            i = (i - 1) % 4
        durum["yon"] = YONLER[i]
        return "DONUS"
    
    if ad == "ILERI":
        dx, dy = ADIM[durum["yon"]]
        izgara = durum["izgara"]
        for _ in range(n):
            nx = durum["x"] + dx
            ny = durum["y"] + dy
            disarda = ny < 0 or ny >= len(izgara) or nx < 0 or nx >= len(izgara[0])
            if disarda or izgara[ny][nx] == "#":
                durum["carpisma"] += 1
                ceza = ayar["carpisma_cezasi"]
                if ceza > durum["batarya"]:
                    durum["batarya"] = 0
                    durum["bitti"] = True
                    return "BATARYA_BITTI"
                durum["batarya"] -= ceza
                return "CARPISMA"
            maliyet = ayar["adim_maliyeti"]
            if durum["yuk"]:
                maliyet *= ayar["yuk_carpani"]
            if maliyet > durum["batarya"]:
                durum["bitti"] = True
                return "BATARYA_BITTI"
            durum["batarya"] -= maliyet
            durum["x"] = nx
            durum["y"] = ny
            durum["adim"] += 1
            k = (nx, ny)
            durum["ziyaret"][k] = durum["ziyaret"].get(k, 0) + 1
        return "HAREKET"
    
    if ad == "AL":
        if durum["izgara"][durum["y"]][durum["x"]] == "K" and not durum["yuk"]:
            durum["izgara"][durum["y"]][durum["x"]] = "."
            durum["yuk"] = True
            return "ALINDI"
        return "GECERSIZ"

    if ad == "BIRAK":
        if not durum["yuk"]:
            return "GECERSIZ"
        hucre = durum["izgara"][durum["y"]][durum["x"]]
        if hucre == "T":
            durum["yuk"] = False
            durum["teslim"] += 1
            return "TESLIM"
        if hucre == ".":
            durum["izgara"][durum["y"]][durum["x"]] = "K"
            durum["yuk"] = False
            return "BIRAKILDI"
        return "GECERSIZ"

    if ad == "SARJ":
        if durum["izgara"][durum["y"]][durum["x"]] == "S":
            durum["batarya"] = ayar["batarya_kapasitesi"]
            return "SARJ"
        return "GECERSIZ"
    
    return "GECERSIZ"


def komut_metni(komut):
    ad, n = komut
    if n is None:
        return ad
    return ad + " " + str(n)


def log_satiri(no, komut, durum, olay):
    return {"adim": no, "komut": komut_metni(komut), "x": durum["x"],
            "y": durum["y"], "yon": durum["yon"],
            "batarya": durum["batarya"], "olay": olay}


def sonuc_olustur(durum):
    ziyaret = durum["ziyaret"]
    en_cok = max(ziyaret.values())
    adaylar = [k for k, v in ziyaret.items() if v == en_cok]
    x, y = min(adaylar, key=lambda k: (k[1], k[0]))
    return {"konum": [durum["x"], durum["y"]], "yon": durum["yon"],
            "batarya": durum["batarya"], "yuk": durum["yuk"],
            "teslim": durum["teslim"], "carpisma": durum["carpisma"],
            "toplam_adim": durum["adim"], "batarya_bitti": durum["bitti"],
            "en_cok_ziyaret": [x, y]}


def simulasyonu_calistir(izgara, baslangic, komutlar, ayarlar):
    durum = yeni_durum(izgara, baslangic, ayarlar)
    log = []
    for no, komut in enumerate(komutlar, start=1):
        if durum["bitti"]:
            break
        olay = komut_uygula(durum, komut)
        log.append(log_satiri(no, komut, durum, olay))
    return sonuc_olustur(durum), log


def sonuc_yaz(sonuc, dosya_yolu):
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)   


def log_yaz(log, dosya_yolu):
    alanlar = ["adim", "komut", "x", "y", "yon", "batarya", "olay"]
    with open(dosya_yolu, "w", encoding="utf-8", newline="") as f:
        yazici = csv.DictWriter(f, fieldnames=alanlar)
        yazici.writeheader()
        yazici.writerows(log)


OKLAR = {"K": "^", "D": ">", "G": "v", "B": "<"}
def harita_metni(durum):
    satirlar = []
    for y, satir in enumerate(durum["izgara"]):
        metin = ""
        for x, hucre in enumerate(satir):
            if x == durum["x"] and y == durum["y"]:
                metin += OKLAR[durum["yon"]]
            else:
                metin += hucre
        satirlar.append(metin)
    return "\n".join(satirlar)



if __name__ == "__main__":
    p = "deneme_verileri/veri_1/"
    iz, r = harita_oku(p + "harita.txt")
    a = ayarlari_oku(p + "ayarlar.json")
    k, h = komutlari_oku(p + "komutlar.txt")
    sonuc, log = simulasyonu_calistir(iz, r, k, a)
    sonuc["hatali_satirlar"] = h
    sonuc_yaz(sonuc, "sonuc.json")
    log_yaz(log, "log.csv")
    print(harita_metni(yeni_durum(iz, r, a)))