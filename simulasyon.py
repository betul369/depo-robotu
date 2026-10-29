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
    
    
    
   


izgara, r = harita_oku("paket_ornek/test06/harita.txt")
print(r)
print(izgara)