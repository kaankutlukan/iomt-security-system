import requests

TARGET_URL = "http://172.20.10.14:3000/login"
USER_TO_ATTACK = "admin"

payloads = [
    "' OR '1'='1",
    "' OR 1=1 --",
    "admin' --",
    "' OR 'a'='a",
    "') OR ('1'='1"
]

def tarama_baslat():
    print("=" * 50)
    print(" HTTP ÜZERİNDEN GÜVENLİK TESTİ BAŞLATILDI")
    print(f"Hedef: {TARGET_URL}")
    print("=" * 50)

    for i, p in enumerate(payloads, 1):
        print(f"🔍 [{i}/{len(payloads)}] Deneniyor: {p}")
        
        try:
            response = requests.post(
                TARGET_URL, 
                data={"user": p, "pass": "12345"}, 
                timeout=15
            )

            if "ENGEL" in response.text or "banlandı" in response.text:
                print(f" [DURDURULDU] Savunma Servisi (IPS) devreye girdi! IP banlandı.")
                print(f"Nedeni: Şüpheli karakter/saldırı girişimi tespit edildi.")
                break
            else:
                print(f"✅ [GÜVENLİ] Giriş reddedildi (Kod korumalı).")

        except Exception as e:
            print(f"❌ Bağlantı hatası: {e}")
            break

    print("\n" + "=" * 50)
    print("🏁 TEST TAMAMLANDI")
    print("=" * 50)

if __name__ == "__main__":
    tarama_baslat()
